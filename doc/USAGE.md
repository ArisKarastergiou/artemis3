## ARTEMIS3 Usage Documentation

### Configuration Files

In the ./config/ directory there are a number of configuration files which can be modified, written by hand, or generated to facilitate ease of observations.

<ARRAY>_*.yml (e.g. HBA_single_source.yml):

These are observation configuration files used to setup the LCU beamctl beamlet ccontroller and LuMP receiver code.

sources/*.yml:

Astronomical source which at the minimum contain an RAJD (J2000 degrees), DECJD (J2000 degrees), and NAME (string)

### Generating a set of observing scripts:

LCU and LuMP receiver scripts scan be generated using ./scripts/generateObsScripts.py with YAML config files. For example to generate an set on observation scripts to observe B1133+16 with the HBA do the following:

```
./generateObsScripts.py -o ../config/HBA_single_source.yml -s ../config/sources/B1133+16.yml
```
