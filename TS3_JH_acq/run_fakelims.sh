#!/bin/bash
#(python /nfs/farm/g/lsst/u1/jobHarness/jh_inst/tests/fakelims.py) \
#    >& fakelims.out &

(python my_fakelims.py ts3_traveler) >& fakelims.out &
