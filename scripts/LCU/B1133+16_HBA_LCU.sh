#!/bin/bash

# generated with generateObsScripts.py on 2019-03-14 21:16:43.599194

rspctl --bitmode=8

/opt/lofar/bin/beamctl --antennaset=HBA_JOINED --rcus=0:191 --band=110_190 --beamlets=0:487 --subbands=12:499 --anadir=3.037109.6,0.276656.6,J2000 --digdir=3.037109.6,0.276656.6,J2000 &
