#!/usr/bin/env python

import ipaddress
import re

# https://gist.github.com/wido/f5e32576bb57b5cc6f934e177a37a0d3
def mac2eui64(mac, prefix=None):
    '''
    Convert a MAC address to a EUI64 address
    or, with prefix provided, a full IPv6 address
    '''
    # http://tools.ietf.org/html/rfc4291#section-2.5.1
    eui64 = re.sub(r'[.:-]', '', mac).lower()
    eui64 = eui64[0:6] + 'fffe' + eui64[6:]
    eui64 = hex(int(eui64[0:2], 16) ^ 2)[2:].zfill(2) + eui64[2:]

    if prefix is None:
        return ':'.join(re.findall(r'.{4}', eui64))
    else:
        try:
            net = ipaddress.ip_network(prefix, strict=False)
            euil = int('0x{0}'.format(eui64), 16)
            return str(net[euil])
        except:  # pylint: disable=bare-except
            return

ip = ipaddress.ip_address('192.0.2.1')
print(ip.packed)
ip = ipaddress.ip_address('fe80::a00:27ff:fe51:47ce')
ip = ipaddress.ip_address('2001:0db8:ac10:fe01::')
print(ip)
print(ip.version)
print(ip.packed)
print("global", ip.is_global)
print("link", ip.is_link_local)

'''
ex.
net6 fe80::a00:27ff:fe51:47ce  prefixlen 64  scopeid 0x20<link>
ether 08:00:27:51:47:ce  txqueuelen 1000  (Ethernet)
'''
print(mac2eui64(mac='08:00:27:51:47:ce', prefix='fe80::/64'))
