set term png
set output 'ts_partcounter.png'
set title "Cleanroom Particle Counter Plot\nvs. time"
set xlabel "Date\nTime"
set timefmt "%Y-%m-%d %H:%M:%S"
set yrange [ 0. : 15. ]
set xdata time
set ylabel "Number of Particles\nper cubic inch"
set format x "%d/%m\n%H:%M"
set grid
set key left
plot 'ts_partcounter.dat' using 1:3
replot
# t '', \
#     'ts_partcounter.dat' using 1:3 t 'T' with points