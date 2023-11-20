#!/usr/bin/env python3
import sys
import time
import os
import subprocess

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

sys.path.append('../')

import INFLUX_CONFIG

def record_bubble():
    write_api = INFLUX_CONFIG.client.write_api(write_options=SYNCHRONOUS)
    point = Point(INFLUX_CONFIG.point)\
            .tag("brew", INFLUX_CONFIG.data_tag)\
            .field("bubble", True)\
            .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(INFLUX_CONFIG.bucket, INFLUX_CONFIG.org, point)
    print("Logging Bubble")

try:
    p1 = subprocess.Popen(["parecord","--raw","--rate=20000","--format=s16le","--channels=1"],stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["./beat_counter","-s20000","-t50"], stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
    while True:
        line = p2.stdout.readline()
        if line.startswith("BUBBLE DETECTED"): 
            record_bubble()
except KeyboardInterrupt:
    print("SIGINT - exiting.")
    p2.kill()
    p2.wait()
    p1.kill()
    p1.wait()
