#!/usr/bin/env python3
import time
import sys

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# local modules
import LCD2004

sys.path.append('../')
import INFLUX_CONFIG

LCD2004.init(0x3f,1)
FILE_REF_SENSOR=open("/sys/bus/w1/devices/28-0114535d9aaa/temperature")
FILE_VESSEL_SENSOR=open("/sys/bus/w1/devices/28-011453dbe6aa/temperature")

def write_temperatures(ref_temp,vessel_temp):
    print('{:0.3f} and {:0.3f}'.format(ref_temp, vessel_temp))
    LCD2004.write(0,0, 'Ref: {:0.3f}'.format(ref_temp))
    LCD2004.write(0,1, 'Vessel: {:0.3f}'.format(vessel_temp))

def get_temperatures():
    FILE_REF_SENSOR.seek(0)
    FILE_VESSEL_SENSOR.seek(0)
    return (
            float(FILE_REF_SENSOR.read()) / 1000,
            float(FILE_VESSEL_SENSOR.read()) / 1000
    )

def record_temperatures(ref,ves):
    write_api = INFLUX_CONFIG.client.write_api(write_options=SYNCHRONOUS)
    point = Point(INFLUX_CONFIG.point)\
            .tag("brew", INFLUX_CONFIG.data_tag)\
            .field("vessel_temp", ves)\
            .field("reference_temp", ref)\
            .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(INFLUX_CONFIG.bucket, INFLUX_CONFIG.org, point)

try:
    while True:
        (ref,vessel) = get_temperatures()
        record_temperatures(ref,vessel)
        write_temperatures(ref,vessel)
        time.sleep(10)
except KeyboardInterrupt:
    print("SIGINT - exiting.")
