# myenovos
A Python module and command line program for accessing electricity consumption data from https://my.enovos.lu (for which an account is required).

Includes a tool for inserting the data into an [InfluxDB](https://www.influxdata.com/) time-series database, eg. for visualization with [Grafana](https://grafana.com/).

# Requirements
- Python 3.8
- ```myenovos.py``` needs the [requests](https://docs.python-requests.org/en/master/) library.
- ```myenovos-influxdb.py``` needs the [influxdb client library](https://pypi.org/project/influxdb/) as well as [dateutil](https://pypi.org/project/python-dateutil/).

# Command line usage
```myenovos.py``` can be used as a command-line program to print data in JSON format:

```bash
$ ./myenovos.py --help

usage: myenovos.py [-h] [--customer CUSTOMER_NR] [--contract CONTRACT_NR] [--start-timestamp START_TS] [--end-timestamp END_TS] username password

Fetch data from my.enovos.lu. Can be invoked with @argsfile to supply arguments from a file (1 per line).

positional arguments:
  username              User name on https://my.enovos.lu
  password              Password on https://my.enovos.lu

optional arguments:
  -h, --help            show this help message and exit
  --customer CUSTOMER_NR, -cu CUSTOMER_NR
                        Customer number (defaults to first customer number of user)
  --contract CONTRACT_NR, -co CONTRACT_NR
                        Contract number for which to get consumption history (defaults to first open electricity contract)
  --start-timestamp START_TS, -s START_TS
                        Start unix timestamp (defaults to 1st of current month)
  --end-timestamp END_TS, -e END_TS
                        End unix timestamp (defaults to current time)
```

Running the program with only the my.enovos.lu username and password results
in it printing the JSON consumption data for the first open electricity contract
for the current month.

To avoid giving credentials on the command line, options can be read from
a file, like this:

```bash
$ cat myenovos.args
myenovosuser@example.com
myenovospassword

$ ./myenovos.py @myenovos.args -cu 123456789
...
```

# InfluxDB import
```myenovos-influxdb.py``` can be used to import consumption data into InfluxDB.

In addition to the my.enovos.lu credentials, it requires an Influx database name
to be given. It supports the same options as ```myenovos.py``` for customer/contract
selection, as well as options for the InfluxDB connection parameters:

```bash
$ ./myenovos-influxdb.py --help
usage: myenovos-influxdb.py [-h] [--customer CUSTOMER_NR] [--contract CONTRACT_NR] [--start-timestamp START_TS] [--end-timestamp END_TS] [--influx-host INFLUX_HOST] [--influx-port INFLUX_PORT] [--influx-user INFLUX_USER] [--influx-password INFLUX_PASSWORD] username password influx_db

Fetch data from my.enovos.lu and insert into InfluxDB. Can be invoked with @argsfile to supply arguments from a file (1 per line).

positional arguments:
  username              User name on https://my.enovos.lu
  password              Password on https://my.enovos.lu
  influx_db             InfluxDB database name to import into

optional arguments:
  -h, --help            show this help message and exit
  --customer CUSTOMER_NR, -cu CUSTOMER_NR
                        Customer number (defaults to first customer number of user)
  --contract CONTRACT_NR, -co CONTRACT_NR
                        Contract number for which to get consumption history (defaults to first open electricity contract)
  --start-timestamp START_TS, -s START_TS
                        Start unix timestamp (defaults to 1st of current month)
  --end-timestamp END_TS, -e END_TS
                        End unix timestamp (defaults to current time)
  --influx-host INFLUX_HOST
                        defaults to localhost
  --influx-port INFLUX_PORT
                        defaults to 8086
  --influx-user INFLUX_USER
                        defaults to root
  --influx-password INFLUX_PASSWORD
```

It also supports the ```@argsfile``` syntax to supply arguments from a file.

# Python API
```myenovos.py``` can be imported as a Python module. The API is property based
and can be used like this:

```python
>>> import myenovos
>>> e = myenovos.MyEnovos('myusername', 'mypassword')
>>> e.user
<User first_name='Hombre' last_name='Incognito' email='user@example.com'>
>>> e.user.customers  # a user can manage multiple customer accounts
[<Customer customer_nr='1234567890'>]
>>> e.user.customers[0].contracts  # a customer can have multiple contracts
[<Contract contract_nr='012345678901' product='naturgas home T1'>, <Contract contract_nr='012345678902' product='naturstroum home mono'>]
>>> e.user.customers[0].contracts[1].get_history()
[{'status': 'MACO', 'value': 0.642, 'ts': '2021-04-30T22:00:00.000Z'}, {'status': 'MACO', 'value': 0.32, 'ts': '2021-04-30T22:15:00.000Z'}, {'status': 'MACO', 'value': 0.164, 'ts': '2021-04-30T22:30:00.000Z'}, {'status': 'MACO', 'value': 0.438, 'ts': '2021-04-30T22:45:00.000Z'}, {'status': 'MACO', 'value': 0.432, 'ts': '2021-04-30T23:00:00.000Z'}, ...]
```
Consumption data is returned unchanged from the my.enovos.lu service.

Please refer to the source code for further details regarding the API.
