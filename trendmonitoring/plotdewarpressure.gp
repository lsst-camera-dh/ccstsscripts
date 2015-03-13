set term png
set output 'ts_dewarpressure.png'
set title "Dewar Pressure Plot\nvs. time"
set xlabel "Date\nTime"
set timefmt "%Y-%m-%d %H:%M:%S"
#set yrange [ 0. : 1. ]
set xdata time
set ylabel "Pressure\nTorr"
set format x "%d/%m\n%H:%M"
set grid
set key left
plot 'ts_dewarpressure.dat' using 1:3
replot
# t '', \
#     'ts_dewarpressure.dat' using 1:3 t 'T' with points