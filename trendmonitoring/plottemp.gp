set term png
set output 'ts_roomtemperature.png'
set title "Cleanroom Temperature Plot\nvs. time"
set xlabel "Date\nTime"
set timefmt "%Y-%m-%d %H:%M:%S"
set yrange [ 60. : 75. ]
set xdata time
set ylabel "Temperature\nF"
set format x "%d/%m\n%H:%M"
set grid
set key left
plot 'ts_roomtemperature.dat' using 1:3
replot
# t '', \
#     'ts_roomtemperature.dat' using 1:3 t 'T' with points