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
SAMPLE_TIME=10 #minutes
CORES_MAX=4

filename = "CPU_" + str(datetime.datetime.now())
filename = filename.replace(" ","_")
filename = filename.replace(":","_")
filename = filename.replace(".","_")

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

def stressTest(cpu_cores):
    if (cpu_cores > 0):
        pid = os.spawnlp(os.P_NOWAIT, "stress", "stress", "--cpu",str(cpu_cores))
        log("running stress with base pid=%s, cpu_cores=%d" % (str(pid),cpu_cores))
    else:
        log("running baseline measurements")
    second = 0
    while (second < SAMPLE_TIME * 60):
        metrics = getMetrics()
        log("%s,%d    (%d/%d)" % (metrics,cpu_cores,second/SAMPLE_RATE,SAMPLE_TIME*60/SAMPLE_RATE))
        data.write("%s,%d\n" % (metrics,cpu_cores))
        second += SAMPLE_RATE
        time.sleep(SAMPLE_RATE)

    os.system("killall stress") # the pid of the children threads differ, so use this instead

log("initializing CPU stress test")
log("TIME=%d, RATE=%d" % (SAMPLE_TIME,SAMPLE_RATE))

# Create an output file
results = filename + ".csv"
data = open(results,"w+")
log("benchmark results stored in %s" % results)
data.write("time,clockrate,temperature,cores\n") # column headers

# Start the stress test
log("starting stress test")
cores=0
while (cores <= CORES_MAX):
    stressTest(cores)
    cores += 1

log("CPU stress test complete")

