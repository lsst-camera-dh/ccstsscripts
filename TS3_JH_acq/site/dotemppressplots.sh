#!/bin/bash                                                                    
mysql CCSTrending -h lsstdb2.rcf.bnl.gov -u ccs --password=vst4lsst <<EOF | awk '{if ((NR%6)==0) print $0}' > ts_dewarpressure.dat
select FROM_UNIXTIME(tstampmills/1000.),doubleData from rawdata where descr_id = 123 and doubleData > 0. order by -tstampmills limit 540;
EOF
gnuplot /home/ts3prod/prod/lcatr/TS3_JH_acq/site/plotdewarpressure.gp
mysql CCSTrending -h lsstdb2.rcf.bnl.gov -u ccs --password=vst4lsst <<EOF | awk '{if ((NR%6)==0) print $0}' > ts_ccdtemperature.dat
select FROM_UNIXTIME(tstampmills/1000.),doubleData from rawdata where descr_id = 122 order by -tstampmills limit 540;
EOF
gnuplot /home/ts3prod/prod/lcatr/TS3_JH_acq/site/plotccdtemp.gp
# keeping the knowledge
#show tables;
#select * from datadesc;
#| 117 | a        |                 0 | ts/roomtemperature                          |                 0 | roomtemperature         | ts           |
#| 118 | a        |                 0 | ts/cleanroomhumidity                        |                 0 | cleanroomhumidity       | ts           |
#| 123 | a        |                 0 | ts/dewarpressure                            |                 0 | dewarpressure           | ts           |
#| 116 | a        |                 0 | ts/dewpoint                                 |                 0 | dewpoint                | ts           |
#| 128 | a        |                 0 | ts/partcounter                              |                 0 | partcounter             | ts           |
#| 122 | a        |                 0 | ts/ccdtemperature                           |                 0 | ccdtemperature          | ts           |

#describe rawdata;
#mysql> select * from rawdata limit 30;
#+------+---------------------+------------+---------------+----------+
#| id   | doubleData          | stringData | tstampmills   | descr_id |
#+------+---------------------+------------+---------------+----------+
#| 3341 |               36.25 | NULL       | 1378898147739 |       21 |
#| 3342 |                41.5 | NULL       | 1378898147739 |       22 |
