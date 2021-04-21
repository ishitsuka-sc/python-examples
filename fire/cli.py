#!/usr/bin/env python

import fire

def hello(mac='', ip='', dns='', name='World'):
  if(mac):
    print("Mac addr is..", mac)
  if(ip):
    print("IP addr  is..", ip)
  return "Hello %s\n" % name

fire.Fire(hello)
