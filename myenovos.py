#!/usr/bin/env python

import sys
import datetime
import requests
import urllib.parse
import functools
import argparse
import json

class Contract:
    def __init__(self, my_enovos, contract_data):
        self.my_enovos = my_enovos
        self.contract_data = contract_data
        self.contract_nr = self.contract_data['vkont']
        self.kind = self.contract_data['installation_service_type']

    def __str__(self):
        return self.contract_data['productname']

    @property
    def open(self):
        return self.contract_data['open']

    def get_history(self, start_datetime=None, end_datetime=None):
        if not end_datetime:
            end_datetime = datetime.datetime.now()
        if not start_datetime:
            start_datetime = end_datetime.replace(day=1)
        start_timestamp = int(start_datetime.timestamp() * 1000)
        end_timestamp = int(end_datetime.timestamp() * 1000)
        customer_nr = self.contract_data['customerid']
        pod = self.contract_data['devicedesignation']
        installation_id = self.contract_data['installationid']
        r = self.my_enovos._session.get(f'https://customer-portal-service.enocloud.eu/v3/cp/customer/{customer_nr}/contracts/{self.contract_nr}/loadprofile?activity=01&pod={pod}&obis=1-1%3A1.29.0&start={start_timestamp}&end={end_timestamp}&vkont={self.contract_nr}&installationid={installation_id}')
        return r.json()

    def __repr__(self):
        return f"<Contract contract_nr='{self.contract_nr}' product='{self.contract_data['productname']}'>"


class Customer:
    def __init__(self, my_enovos, customer_nr):
        self.my_enovos = my_enovos
        self.customer_nr = customer_nr

    @functools.cached_property
    def contracts(self):
        contract_list = self.my_enovos._session.get(f'https://customer-portal-service.enocloud.eu/v3/cp/customer/{self.customer_nr}/contracts').json()
        return [Contract(self.my_enovos, contract_data) for contract_data in contract_list]

    def get_contract_by_nr(self, contract_nr):
        return next((c for c in self.contracts if c.contract_nr == contract_nr), None)

    def __repr__(self):
        return f"<Customer customer_nr='{self.customer_nr}'>"


class User:
    def __init__(self, my_enovos):
        self.my_enovos = my_enovos

    @functools.cached_property
    def _info(self):
        return self.my_enovos._session.get('https://auth-customer.enovos.lu/api/userinfo').json()

    @property
    def customer_nrs(self):
        return self._info['partner_id']

    @property
    def customers(self):
        return [Customer(self.my_enovos, c_nr) for c_nr in self.customer_nrs]

    def __repr__(self):
        return f"<User first_name='{self._info['first_name']}' last_name='{self._info['last_name']}' email='{self._info['email']}'>"


class MyEnovos:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @functools.cached_property
    def _session(self):
        s = requests.session()
        s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'})
        r = s.post('https://auth-customer.enovos.lu/login', json=dict(username=self.username, password=self.password))
        # Get authorization token from redirect url of previous request in redirect chain
        token = urllib.parse.parse_qs(urllib.parse.urlparse(r.history[-1].headers['Location']).fragment)['access_token'][0]
        s.headers['authorization'] = 'Bearer ' + token
        return s

    @property
    def user(self):
        return User(self)

    def __repr__(self):
        return f"<MyEnovos username='{self.username}'>"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch data from my.enovos.lu. Can be invoked with @argsfile to supply arguments from a file (1 per line)', fromfile_prefix_chars='@')
    parser.add_argument('username', type=str, help='User name on https://my.enovos.lu')
    parser.add_argument('password', type=str, help='Password on https://my.enovos.lu')
    parser.add_argument('--customer', '-cu', metavar='customer_nr', required=False, type=str, dest='customer_nr', default=None, help='Customer number (defaults to first customer number of user)')
    parser.add_argument('--contract', '-co', metavar='contract_nr', required=False, type=str, dest='contract_nr', default=None, help='Contract number for which to get consumption history (defaults to first open electricity contract)')
    parser.add_argument('--start-timestamp', '-s', metavar='start_ts', required=False, type=str, dest='start_ts', default=None, help='Start unix timestamp (defaults to 1st of current month)')
    parser.add_argument('--end-timestamp', '-e', metavar='end_ts', required=False, type=str, dest='end_ts', default=None, help='End unix timestamp (defaults to current time)')
    args = parser.parse_args()

    e = MyEnovos(args.username, args.password)

    if args.customer_nr:
        customer = next((c for c in e.user.customers if c.customer_nr == args.customer_nr), None)
    else:
        customer = e.user.customers[0]

    contracts = customer.contracts
    if args.contract_nr:
        contract = customer.get_contract_by_nr(args.contract_nr)
    else:
        contract = next((c for c in contracts if c.open and c.kind == 'Electricity'), None)

    start_dt = None
    if args.start_ts:
        start_dt = datetime.datetime.fromtimestamp(float(args.start_ts))

    end_dt = None
    if args.end_ts:
        end_dt = datetime.datetime.fromtimestamp(float(args.end_ts))

    print(json.dumps(contract.get_history(start_dt, end_dt), indent=2))
