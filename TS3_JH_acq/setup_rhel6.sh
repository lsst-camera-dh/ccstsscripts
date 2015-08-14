export SHELL=/bin/bash

#source ./loadLSST.sh
source /opt/lsst/rhel-6-x86_64/loadLSST.sh

#export EUPS_PATH=/nfs/slac/g/ki/ki18/jchiang/LSST/DMstack/eups:${EUPS_PATH}#ex
export EUPS_PATH=/opt/lsst/rhel-6-x86_64/DMstack/eups:${EUPS_PATH}

setup eotest
setup mysqlpython
setup scipy
setup pyfits
