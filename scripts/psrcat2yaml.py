#!/usr/bin/env python3

import yaml
import subprocess
import numpy as np

PSRCATBIN = 'psrcat'

def dictFromPsrcat(sourceName):
    """Generate a dictionary from an entry in psrcat
    sourceName: str, psrcat source name

    returns: dict
    """
    result = subprocess.run('%s -nonumber -nohead -c \'JNAME RAJD DECJD P0 P1 W50 S1400 DM\' %s'%(PSRCATBIN, sourceName), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print('Error: there is an issue with psrcat, prehaps it is not in the PATH')
        return None
    srcStr = result.stdout.decode('utf-8').strip()
    
    if srcStr.startswith('WARNING'):
        print(srcStr)
        return None
    
    srcList = " ".join(srcStr.split()).split(' ')

    try:
        srcRAJD = float(srcList[2])
    except ValueError:
        print('WARNING: RAJD missing')
        srcRAJD = None

    try:
        srcDECJD = float(srcList[3])
    except ValueError:
        print('WARNING: DECJD missing')
        srcDECJD = None

    try:
        srcP0 = float(srcList[4])
    except ValueError:
        print('WARNING: P0 missing')
        srcP0 = None

    try:
        srcP1 = float(srcList[7])
    except ValueError:
        print('WARNING: P1 missing')
        srcP1 = None

    try:
        srcW50 = float(srcList[10])
    except ValueError:
        print('WARNING: W50 missing')
        srcW50 = None

    try:
        srcS1400 = float(srcList[13])
    except ValueError:
        print('WARNING: S1400 missing')
        srcS1400 = None

    try:
        srcDM = float(srcList[16])
    except ValueError:
        print('WARNING: DM missing')
        srcDM = None

    srcDict = {
            'NAME'   : sourceName,
            'RAJD'   : srcRAJD,
            'DECJD'  : srcDECJD,
            'SOURCE_PARAM' : {
                'JNAME'  : srcList[0],
                'P0'     : srcP0,
                'P1'     : srcP1,
                'W50'    : srcW50,
                'S1400'  : srcS1400,
                'DM'     : srcDM
            }
        }
    
    return srcDict

if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='''Generate a YAML source file from a PSRCAT entry, assumes psrcat installed''')
    parser.add_argument('sourceName', help='psrcat source name')
    args = parser.parse_args()
    
    srcDict = dictFromPsrcat(args.sourceName)
    
    if not(srcDict is None):
        ofn = args.sourceName + '.yml'
        print('Writing source entry to %s'%ofn)
        with open(ofn, 'w') as ofh:
            yaml.dump(srcDict, ofh, default_flow_style=False)

