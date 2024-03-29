#!/usr/bin/env python

import argparse
import dateutil.parser
import datetime
import myenovos

from influxdb import InfluxDBClient


def insert_contract_data(contract, influx, start_dt, end_dt):

    tags = {
        'contract_nr': contract.contract_data['vkont'],
        'customer_nr': contract.contract_data['customerid'],
        'device_designation': contract.contract_data['devicedesignation'],
        'product_name': contract.contract_data['productname'],
        'installation_id': contract.contract_data['installationid'],
        'installation_service_type': contract.contract_data['installation_service_type'],
    }

    points = []
    for consumption in contract.get_history(start_dt, end_dt):
        if consumption['status'] != 'MACO':
            continue

        timestamp = dateutil.parser.isoparse(consumption['ts'])
        value = float(consumption['value'])

        points.append({
            'measurement': 'Enovos Consumption',
            'tags': tags,
            'time': timestamp.isoformat(),
            'fields': {
                'value': value
            }
        })

    influx.write_points(points)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Fetch data from my.enovos.lu and insert into InfluxDB. Can be invoked with @argsfile to supply arguments from a file (1 per line).', fromfile_prefix_chars='@')
    parser.add_argument('username', type=str, help='User name on https://my.enovos.lu')
    parser.add_argument('password', type=str, help='Password on https://my.enovos.lu')
    parser.add_argument('influx_db', type=str, help='InfluxDB database name to import into')
    parser.add_argument('--customer', '-cu', type=str, dest='customer_nr', default=None, help='Customer number (defaults to first customer number of user)')
    parser.add_argument('--contract', '-co', type=str, dest='contract_nr', default=None, help='Contract number for which to get consumption history (defaults to first open electricity contract)')
    parser.add_argument('--start-timestamp', '-s', type=str, dest='start_ts', default=None, help='Start unix timestamp (defaults to 1st of current month)')
    parser.add_argument('--end-timestamp', '-e', type=str, dest='end_ts', default=None, help='End unix timestamp (defaults to current time)')
    parser.add_argument('--influx-host', type=str, default='localhost', help='defaults to localhost')
    parser.add_argument('--influx-port', type=int, default=8086, help='defaults to 8086')
    parser.add_argument('--influx-user', type=str, default='root', help='defaults to root')
    parser.add_argument('--influx-password', type=str, default=None)

    args = parser.parse_args()

    start_dt = datetime.datetime.fromtimestamp(float(args.start_ts)) if args.start_ts else None
    end_dt = datetime.datetime.fromtimestamp(float(args.end_ts)) if args.end_ts else None

    e = myenovos.MyEnovos(args.username, args.password)

    if args.customer_nr:
        customer = e.user.get_customer_by_nr(args.customer_nr)
    else:
        customer = e.user.customers[0]

    if args.contract_nr:
        contract = customer.get_contract_by_nr(args.contract_nr)
    else:
        contract = next((c for c in customer.contracts if c.open and c.kind == 'Electricity'), None)

    influx = InfluxDBClient(args.influx_host, args.influx_port, args.influx_user, args.influx_password, args.influx_db)
    influx.create_database(args.influx_db)

    insert_contract_data(contract, influx, start_dt, end_dt)
