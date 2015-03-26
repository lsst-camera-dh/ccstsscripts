source ~/.bashrc
export SHELL=/bin/bash

#source /afs/slac/g/lsst/software/redhat6-x86_64-64bit-gcc44/DMstack/Winter2013-v6_2/loadLSST.sh

export PATH=/opt/lsst/installation/root/Linux64/anaconda/2.1.0/bin:${PATH}
source /opt/lsst/installation/root/loadLSST.bash

export EUPS_PATH=/opt/lsst/installation/root:${EUPS_PATH}

setup eotest
setup mysqlpython
setup scipy

PS1="[eotest]$ "

#export PYTHONPATH=${PYTHONPATH}:/nfs/slac/g/ki/ki18/jchiang/LSST/JH/jh_modules
#export VIRTUAL_ENV=/nfs/slac/g/ki/ki18/jchiang/LSST/JH/virtual_env

source /home/ts3prod/prod/lcatr/TS3_JH_acq/jh_inst_novirtualenv/bin/jh_setup
