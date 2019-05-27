#! /usr/bin/env python3

# get current lst and end lst
# find first source
# check if source is up and will remain up for duration of observation and there is time before end of session, else move to next source
# if all, generate observing scripts for source, LuMP and LCU
# get time at end of observation
# repeat for next source until all sources negative

#!/usr/bin/env python3
#!/usr/bin/env python3
import astropy.time
import astropy.coordinates
import subprocess
from astropy.utils.data import conf

def getsourcepos(sourceName):
    result = subprocess.run('/data/Code/psrcat/psrcat -o short -nonumber -nohead -c \'JNAME RAJD DECJD\' %s'%(sourceName), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print('Error: there is an issue with psrcat, prehaps it is not in the PATH')
        return None
    srcStr = result.stdout.decode('utf-8').strip().split()
    rajd = float(srcStr[1])
    decjd = float(srcStr[2])
    pos = astropy.coordinates.SkyCoord(rajd,decjd,unit='deg')
    return pos
import numpy as np
from numpy.core.defchararray import add

def getlst(t, source):
    lst = t.sidereal_time('mean')
    
    print('Observatory:', t.location.to_geodetic())
    print('UTC: ', t)
    print('LST: ', lst)
#    with conf.set_temp('remote_timeout', 30):
#        apsource = astropy.coordinates.SkyCoord.from_name(source)
    apsource = getsourcepos(source.strip('PSR '))
#    print (apsource.ra.hour)
    sourcealtaz = apsource.transform_to(astropy.coordinates.AltAz(obstime=t,location=t.location))
#    print("Elevation = {0.alt:.2}".format(sourcealtaz))
#    print (lst.hour)
    return lst

def sourcelist(filename):
    totalduration = 0
    sources = np.genfromtxt(filename,usecols=0, dtype=str)
    durations = np.genfromtxt(filename,usecols=1, dtype=int)
    return sources, durations

def findfirstsource(source, lst, startoffset):
    positiveminoffset = 24
    index = -1
    for i in range(len(source)): 
#        with conf.set_temp('remote_timeout', 30):
#            offset = astropy.coordinates.SkyCoord.from_name(source[i]).ra.hour + startoffset - lst.hour 
        apsource = getsourcepos(source[i].strip('PSR '))
        offset = apsource.ra.hour + startoffset - lst.hour 
        if offset > 0 and np.mod(offset,24.) < positiveminoffset:
            positiveminoffset = np.mod(offset,24.)
            index = i
    return index

def issourceup(source, t):
#    with conf.set_temp('remote_timeout', 30):
#        apsource = astropy.coordinates.SkyCoord.from_name(source)
    apsource = getsourcepos(source.strip('PSR '))
    sourcealtaz = apsource.transform_to(astropy.coordinates.AltAz(obstime=t,location=t.location))
    if sourcealtaz.alt.deg > 20.0:
#        print (source," is up at ", sourcealtaz.alt.deg) 
        isup = 1
    else:
        isup = 0
    return isup


if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser(
            description='''Produce a reasonable schedule for an observing epoch''')
    parser.add_argument('-o', '--observatory', help='Observatory name, default: UK608', default='UK608')
    parser.add_argument('-s', '--startdate', help='Start date of observations, e.g. 2019-04-16 10:18:59.685907', required='true')
    parser.add_argument('-e', '--enddate', help='Start date of observations, e.g. 2019-04-16 10:18:59.685907', required='true')
    parser.add_argument('-f', '--filename', help='Catalogue of sources and durations', required='true')
    parser.add_argument('-so', '--strictorder', help='keeps order specified in source file', action='store_true')
    home = '/data/Code/Git/Artemis3/'
    args = parser.parse_args()
    now = astropy.time.Time.now()
    tstart = astropy.time.Time(args.startdate)
    tend = astropy.time.Time(args.enddate)
    locUK608 = astropy.coordinates.EarthLocation.from_geodetic(lat=51.143833512, lon=-1.433500703, height=176.028) # UK608 LBA
    locIE613 = astropy.coordinates.EarthLocation.from_geocentric(3801633.528060000, -529021.899396000, 5076997.185, unit='m') # IE613 LBA
    if args.observatory.startswith('UK608'): tstart.location = locUK608
    elif argsobservatory.startswith('IE613'): tstart.location = locIE613
    if args.observatory.startswith('UK608'): tend.location = locUK608
    elif argsobservatory.startswith('IE613'): tend.location = locIE613
    filename = args.filename
    sources, durations = sourcelist(filename)
    numberofsources = len(sources)
    print ('Designing observations starting at ', tstart) 
    print (numberofsources, ' Sources')
#    print (sources, durations)
    psrnames = add('PSR ',sources)
#    print (psrnames, durations)
    lst = getlst(tstart, psrnames[0])
    # Find first source
    if args.strictorder:
        index = 0
    else:
        index = findfirstsource(psrnames, lst, 3) # the last argument is in hours, to be subtracted from the LST to find the first source
    rotated_psrnames = np.roll(psrnames, -index)
    rotated_durations = np.roll(durations, -index)
#    print (rotated_psrnames)
    currenttime = tstart
    deadtime = astropy.time.TimeDelta(60, format='sec')
    stepwait = astropy.time.TimeDelta(600, format='sec')
    script = list()
    for i in range(numberofsources):
        # check if source is up
        sourceup = issourceup(rotated_psrnames[i], currenttime)
 #       while not sourceup:
 #           currenttime += stepwait
 #           sourceup = issourceup(rotated_psrnames[i], currenttime)
        # check if source will be up after duration of obs
        dt = astropy.time.TimeDelta(rotated_durations[i], format='sec')
        sourceupend = issourceup(rotated_psrnames[i], currenttime + dt)
        # check if end of run occurs before end of obs
        sourceupfinal = (tend - currenttime - dt > 0.0)
        if sourceup and sourceupend and sourceupfinal:
            #write script
            utc = currenttime
            utc.format='fits'
            utcstart=utc.value[:-4]+'Z'
            print (i, ". Writing script files for ", rotated_psrnames[i], utcstart, currenttime.sidereal_time('mean'))
            script.append(home+"scripts/generateObsScripts.py -o "+home+"config/HBA_single_source.yml -s "+home+"config/sources/"+rotated_psrnames[i].strip('PSR ')+".yml -d "+utcstart+" --duration "+str(rotated_durations[i]))
            currenttime += dt + deadtime
        else:
            print (i, ". Not Writing script filesfor ", rotated_psrnames[i], currenttime, currenttime.sidereal_time('mean'))

    with open('source_this.exe', 'w') as f:
        for item in script:
            f.write("%s\n" % item)
            
