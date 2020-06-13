#!/usr/bin/python3
# CPU benchmarking for rpi
# NOTE: only compatible with pi due to vcgencmd dependency

import datetime
import os
import subprocess
import time
import signal

INITIAL_TEMP_TIME = 1 #minute
SAMPLE_RATE=5 #seconds
SAMPLE_TIME=60 #minutes

filename = "CPU_" + str(datetime.datetime.now()).replace(" ","_")

# Create log file
logname = filename + ".log"
logfile = open(logname,"w+")

def log(msg):
    print(msg)
    logfile.write("%s\n" % msg)


def getClockrate():
    value = subprocess.check_output(["vcgencmd measure_clock arm"],shell=True)
    value = str(value).strip()
    value = value.replace("b'frequency(48)=","")
    value = value.replace("\\n'","")
    return value

def getTemperature():
    value = subprocess.check_output(["vcgencmd measure_temp"],shell=True)
    value = str(value).strip()
    value = value.replace("b\"temp=","")
    value = value.replace("'C\\n\"","")
    return value

def getMetrics():
    time = str(datetime.datetime.now())
    clock = getClockrate()
    temp = getTemperature()
    return "%s,%s,%s" % (time,clock,temp)

log("initializing CPU stress test")
log("TIME=%d, RATE=%d" % (SAMPLE_TIME,SAMPLE_RATE))

# Create an output file
results = filename + ".csv"
data = open(results,"w+")
log("benchmark results stored in %s" % results)
data.write("time,clockrate,temperature\n") # column headers

# Get initial temps
log("measuring initial temperatures")
seconds=0
while (seconds < INITIAL_TEMP_TIME * 60):
    metrics = getMetrics()
    log(metrics)
    data.write("%s\n" % metrics)
    seconds += SAMPLE_RATE
    time.sleep(SAMPLE_RATE)

# Start the stress test
log("starting stress test")
pid = os.spawnlp(os.P_NOWAIT, "stress", "stress", "--cpu","4")
log("running stress with base pid=%s" % str(pid))
seconds = 0
while (seconds < SAMPLE_TIME * 60):
    metrics = getMetrics()
    log("%s    -> %d:%d (%d:00)" % (metrics,seconds/60,seconds%60,SAMPLE_TIME))
    data.write("%s\n" % metrics)
    seconds += SAMPLE_RATE
    time.sleep(SAMPLE_RATE)

os.system("killall stress") # the pid of the children threads differ, so use this instead

log("CPU stress test complete")

