#!/usr/bin/env python3

import yaml
import psrcat2yaml

import argparse
parser = argparse.ArgumentParser(
    description='''Generate YAML source files from an observation file, assumes psrcat installed''')
parser.add_argument('obsFile', help='Observation file')
args = parser.parse_args()
totalduration = 0
fh = open(args.obsFile, 'r')
for ll in fh:
    if ll.startswith('#'): continue
    srcName, duration, obsMode = ll.strip().split(' ')
    totalduration += int(duration)
    print('Source name:', srcName)
    
    srcDict = psrcat2yaml.dictFromPsrcat(srcName)

    if not(srcDict is None):
        ofn = srcName + '.yml'
        print('Writing source entry to %s'%ofn)
        with open(ofn, 'w') as ofh:
            yaml.dump(srcDict, ofh, default_flow_style=False)
print ('Total observing time (h):', float(totalduration)/3600.)
fh.close()

