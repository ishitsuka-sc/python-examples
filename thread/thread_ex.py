#!/usr/bin/env python

import time
import threading

data='xxx'

def ex1():
  print("ex1")
  for i in range(10):
    time.sleep(1)
    print(i,":","data=", data)
  print("ex1 exit")

def ex2():
  global data
  print("ex2")
  time.sleep(3)
  data="aaaa"

th1 = threading.Thread(target=ex1)
th2 = threading.Thread(target=ex2)
th1.start()
th2.start()
th1.join()

