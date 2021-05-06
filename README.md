# myenovos

A Python module and command line program for accessing electricity consumption data from https://my.enovos.lu (for which an account is required).

Includes a tool for inserting the data into an [InfluxDB](https://www.influxdata.com/) time-series database, eg. for visualization with [Grafana](https://grafana.com/).

# Requirements

- myenovos.py needs the [requests](https://docs.python-requests.org/en/master/) library.
- myenovos-influxdb.py needs the [influxdb client library](https://pypi.org/project/influxdb/) as well as [dateutil](https://pypi.org/project/python-dateutil/).
