#!/usr/bin/env python

from datetime import datetime as dt
from decimal import Decimal
import time
import struct

def ntp_timestamp(timestamp):
  epoch_time = dt(1970, 1, 1)
  print(epoch_time)
  ntp_time = dt(1900, 1, 1)
  print(ntp_time)
  ntp_delta = (epoch_time - ntp_time).days * 24 * 3600
  print(ntp_delta)
  now_ntptime = timestamp + ntp_delta
  ntp_hi = int(now_ntptime)
  ntp_lo = int(abs(now_ntptime - int(now_ntptime)) * 2**32)
  print(now_ntptime, hex(ntp_hi), hex(ntp_lo))
  ntp_hex = hex(ntp_hi)[2:] + hex(ntp_lo)[2:]
  print(bytes.fromhex(ntp_hex))

def datetime_test():
  d0=dt.now()
  print(d0)
  print("d0 sec =", d0.second)
  print("d0 usec =", d0.microsecond)
  time.sleep(1)
  d1=dt.now()
  print(d1)
  print("d1 sec =", d1.second)
  print("d1 usec =", d1.microsecond)
  usec_hex = hex(int((d1.microsecond/500000)*0x80000000))
  print("usec =", usec_hex, int((d1.microsecond/500000)*0x80000000))

  delta = d1-d0
  print("delta sec =", delta.seconds)
  print("delta usec =", delta.microseconds)

  usec = delta.microseconds/1000000
  usec_hex = (delta.microseconds/500000)*0x80000000
  print(hex(int(usec_hex)))
  print(struct.pack('>d', usec))

datetime_test()
ntp_timestamp(time.time())


