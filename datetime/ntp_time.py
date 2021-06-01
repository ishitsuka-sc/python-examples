#!/usr/bin/env python

from datetime import datetime as dt
import time
import struct
import ntplib
import math

print("sytetem time=", time.time())
ntp_time  = ntplib.system_to_ntp_time(time.time())
print("ntp time=", ntp_time)

frac_ntptime, int_ntptime = math.modf(ntp_time)
print(int(int_ntptime))
print(frac_ntptime)

int_ntptime = 1234567
frac_ntptime = 0x7fffffff 
aaa = ntplib._to_time(int_ntptime, frac_ntptime)
print(aaa)

long_time = 12345.499999
print("time=", long_time)
high=ntplib._to_int(long_time)
low=ntplib._to_frac(long_time)
print("to_int:", high, hex(high))
print("to_frac:", low, hex(low))
print("ntp_time:", hex(high <<32 | low))
print("to_time:", ntplib._to_time(high, low))

