#!/usr/bin/env python3

from jinja2 import Environment, FileSystemLoader
import yaml
import os
import datetime
import numpy as np

# HARDCODE
LUMPTEMPLATE = 'LuMP_recorder.j2'
LCUTEMPLATE = 'beamctl.j2'
LUMPPROCESS = 'LuMP_processor.j2'
DATADIRROOT = '/local_data/ARTEMIS/'
SCRIPTDIR = '/data/Commissioning/PSRMonitor/Artemis3/'

if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='''Generate an LCU beamctl script and LuMP recorder scripts from ARTEMIS3 YAML config files''')
    parser.add_argument('-o', '--obsConfigFile', help='YAML observation config file (required)')
    parser.add_argument('-s', '--srcConfigFile', help='YAML source config file (required)')
    parser.add_argument('-d', '--start_date', default=None, help='Start date and time to begin observation, if not used the observation begins when the script begins, which is not ideal when capturing all lanes, use the format: YYYY-MM-DDThh:mm:ssZ e.g. 2019-02-26T10:30:00Z')
    parser.add_argument('--templateDir', help='jinja2 template dir', default='../templates')
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')
    parser.add_argument('--dry_run', help='Do not write scripts, just test out the generator script, useful with the -v option', action='store_true')
    parser.add_argument('--duration', help='Number of seconds to capture, default: 60', default=60)
    args = parser.parse_args()

    if args.obsConfigFile is None:
        print('ERROR: Observation config file is not set but is required, exiting')
        exit(1)
    if args.srcConfigFile is None:
        print('ERROR: Source config file is not set but is required, exiting')
        exit(1)
    obsConfigDict = yaml.load(open(args.obsConfigFile))
    srcConfigDict = yaml.load(open(args.srcConfigFile))

    # Useful variables
    dt = datetime.datetime.now()
    dataPath = dt.strftime('%Y%m%d_%H%M%S')
    generatorStartTime = str(dt)
    arrayMode = obsConfigDict['beamctl']['antennaset'].split('_')[0]
    decRad = srcConfigDict['DECJD'] * np.pi / 180.
    raRad = srcConfigDict['RAJD'] * np.pi / 180.
    dirStr = '%0.6f,%0.6f,J2000'%(raRad,decRad)

    # Generate LuMP scripts
    lumpDict = obsConfigDict['LuMP']
    if not (args.start_date is None):
        lumpDict['opt_arg'] = '--start_date=%s'%args.start_date
    year = int(args.start_date[0:4])
    month = int(args.start_date[5:7])
    day = int(args.start_date[8:10])
    hour = int(args.start_date[11:13])
    minute = int(args.start_date[14:16])
    lumpDict['generator_script'] = os.path.basename(__file__)
    lumpDict['generator_datetime'] = generatorStartTime
    lumpDict['anadir'] = dirStr
    lumpDict['digdir'] = dirStr
    lumpDict['duration'] = args.duration
    lumpDict['datadir'] = DATADIRROOT + '%s_%s'%(dataPath, srcConfigDict['NAME'])
    lumpDict['sourcename'] =  srcConfigDict['NAME']
    lumpDict['ephemeris'] =  srcConfigDict['NAME'][1:]+'.par'
    lumpDict['source_RA'] = srcConfigDict['RAJ']
    lumpDict['source_Dec'] = srcConfigDict['DecJ']
    lumpDict['dspsr_out'] = '/oxford_data2/PSRMonitor/data/' + srcConfigDict['NAME'] +'/' + args.start_date[0:4] + args.start_date[5:7] + args.start_date[8:10]
    print (lumpDict['dspsr_out'])
    # build a config dict for each lane
    configBase = lumpDict.copy()
    configBase.pop('lane', None)

    configBase['sourcename_array'] = '[%s]*%i'%(srcConfigDict['NAME'], lumpDict['beamlets_per_lane'])
    configBase['rightascension_array'] = '[%0.6f]*%i'%(raRad, lumpDict['beamlets_per_lane'])
    configBase['declination_array'] = '[%0.6f]*%i'%(decRad, lumpDict['beamlets_per_lane'])
    configBase['epoch_array'] = '[J2000]*%i'%(lumpDict['beamlets_per_lane'])
    obstime = datetime.datetime(year,month,day, hour,minute)
    attime = obstime - datetime.timedelta(minutes=1)
    
    for lane in lumpDict['lane']:
        configLane = {**configBase, **lane}
        configLane['filename_base'] = '%s_lane%i'%(srcConfigDict['NAME'], lane['id'])
        
        #Load Jinja2 template
        env = Environment(loader = FileSystemLoader(args.templateDir), trim_blocks=True, lstrip_blocks=True)
        templateLuMP = env.get_template(LUMPTEMPLATE)
        renderText = templateLuMP.render(configLane)
        templateLuMPProc = env.get_template(LUMPPROCESS)
        renderTextProc = templateLuMPProc.render(configLane)
        
        if args.verbose: print(renderText)

        outputFn = SCRIPTDIR + '%s_%s_lane%i.sh'%(srcConfigDict['NAME'], arrayMode, lane['id'])
        outputFnProc = SCRIPTDIR + '%s_%s_lane%i_Proc.sh'%(srcConfigDict['NAME'], arrayMode, lane['id'])
        if lane['id'] < 3:
            adagio = 'adagio1'
        else:
            adagio = 'adagio2'
            
        startdate = attime.strftime('%H:%M %m/%d/%Y')
        atstring = 'echo \"ssh %s \'bash -ix \' < %s \" |at %s \n' %(adagio,outputFn, startdate)
        if os.path.exists('atscript.exe'):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not
        fh2 = open('atscript.exe',append_write)
        fh2.write(atstring)
        fh2.close()
        if not args.dry_run:
            print('Writing ' + outputFn)
            fh = open(outputFn,'w')
            fh.write(renderText)
            fh.close()
        if not args.dry_run:
            print('Writing ' + outputFnProc)
            fh = open(outputFnProc,'w')
            fh.write(renderTextProc)
            fh.close()

    # Generate LCU script
    lcuDict = obsConfigDict['beamctl']
    lcuDict['generator_script'] = os.path.basename(__file__)
    lcuDict['generator_datetime'] = generatorStartTime
    lcuDict['anadir'] = dirStr
    lcuDict['digdir'] = dirStr

    #Load Jinja2 template
    templateLCU = env.get_template(LCUTEMPLATE)
    renderText = templateLCU.render(lcuDict)
    
    if args.verbose: print(renderText)

    outputFn = SCRIPTDIR + '%s_%s_LCU.sh'%(srcConfigDict['NAME'], arrayMode)
    atstring = 'echo \"ssh lcu \'bash -ix \' < %s \" |at %s \n' %(outputFn, startdate)
    fh2 = open('atscript.exe',append_write)
    fh2.write(atstring)
    fh2.close()
    if not args.dry_run:
        print('Writing ' + outputFn)
        fh = open(outputFn,'w')
        fh.write(renderText)
        fh.close()

