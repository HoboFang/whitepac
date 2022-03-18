#!/usr/bin/env python3

import re
import ipaddress
import json
import requests
import sys
from math import log2

IPV4BIT = 32
REGION, NETIP, IPNUM = 1, 3, 4
DEFAULTRGN = 'CN'
RPLCSPEC = '{/*ReplaceSpec*/}' 
RPLCWHITE = '{/*ReplaceWhite*/}'
PACTEMPLATE = 'whiteip_temp.pac'
PACFILENAME = 'whiteip.pac'
RAWSPECIP = 'iana-ipv4-special-registry.txt'
RAWASIAIP = 'delegated-apnic-latest.txt'
URLSPECIP = 'https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.txt'
URLASIAIP = 'https://ftp.apnic.net/stats/apnic/delegated-apnic-latest'

def ipNum2Mask(num):
    assert isinstance(num, int) and num > 0
    return IPV4BIT - int(log2(num))

def mask2IpNum(msk):
    assert isinstance(msk, int) and msk > 0 and msk <= IPV4BIT
    return pow(2, (IPV4BIT - msk)) 

def buildNetTree(nettable):
    assert isinstance(nettable, dict) and len(nettable) > 0
    # minmask used to get the key from an ip
    minmask = ipNum2Mask(max(nettable.values()))
    minmask_val = (pow(2, minmask)-1) << (IPV4BIT - minmask)
    assert minmask_val > 0 
    nettrunk = {'mask': minmask}

    for netip, ipnum in nettable.items():
        if  ipNum2Mask(ipnum) == minmask:
            # this is the final node
            nettrunk[netip] = ipnum
        else:
            # build branch as table
            netip_cut = netip & minmask_val
            if netip_cut in nettrunk.keys():
                nettrunk[netip_cut][netip] = ipnum
            else:
                nettrunk[netip_cut] = {netip: ipnum}

    # convert branch's structure to tree 
    for key, value in nettrunk.items():
        if isinstance(value, dict):
            nettrunk[key] = buildNetTree(value)

    return nettrunk
           
def buildSpecTree(specraw):
    assert isinstance(specraw, list) and len(specraw) > 0
    specnettab = {}
    for line in specraw:
        if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line.strip()):
            network = line.split()[0]
            if not network[-1].isdigit():
                network = network[:-1]
            if network.find('/') == -1:
                network += '/32'
            # these two IP has been contained by others
            if network in '0.0.0.0/32' '255.255.255.255/32':
                continue
            sline = network.split('/')
            specnettab[int(ipaddress.IPv4Address(sline[0]))] = mask2IpNum(int(sline[1]))
    return buildNetTree(specnettab)

def buildWhiteTree(asiaraw, region):
    assert isinstance(asiaraw, list) and len(asiaraw) > 0 \
        and isinstance(region, list) and len(region) > 0
    nettable = {}
    for line in asiaraw:
        if re.match(r'apnic\|[A-Z]{2}\|ipv4', line):
            sline = line.split('|')
            if sline[REGION] in region:
                nettable[int(ipaddress.IPv4Address(sline[NETIP]))] = int(sline[IPNUM])
    return buildNetTree(nettable)

def main():
    args = sys.argv[1:]
    if '-u' in args:
        print('Updating text,this may take a while...')
        with open(RAWSPECIP, 'wt') as fspec:
            fspec.write(requests.get(URLSPECIP).text)
        with open(RAWASIAIP, 'wt') as fasia:
            fasia.write(requests.get(URLASIAIP).text)
        exit()

    region = []
    for arg in args:
        if re.match(r'^[A-Z]{2}$', arg):
            region.append(arg)
    if len(region) == 0:
        region.append(DEFAULTRGN)

    with open(RAWSPECIP, 'rt') as fspec:
        spectree = buildSpecTree(fspec.readlines())
    with open(RAWASIAIP, 'rt') as fasia:
        whitetree = buildWhiteTree(fasia.readlines(), region)

    with open(PACFILENAME, 'wt') as fpac:
        with open(PACTEMPLATE, 'rt') as ftemp:
            for line in ftemp:
                if line.find(RPLCSPEC) != -1:
                    fpac.write(line.replace(RPLCSPEC, str(json.dumps(spectree))))
                elif line.find(RPLCWHITE) != -1:
                    fpac.write(line.replace(RPLCWHITE, str(json.dumps(whitetree))))
                else:
                    fpac.write(line)

main()
