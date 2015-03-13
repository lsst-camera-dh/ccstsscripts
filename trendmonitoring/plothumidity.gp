set term png
set output 'ts_roomhumidity.png'
set title "Cleanroom Humidity Plot\nvs. time"
set xlabel "Date\nTime"
set timefmt "%Y-%m-%d %H:%M:%S"
set yrange [ 10. : 55. ]
set xdata time
set ylabel "Humidity\n%"
set format x "%d/%m\n%H:%M"
set grid
set key left
plot 'ts_roomhumidity.dat' using 1:3
replot
# t '', \
#     'ts_roomhumidity.dat' using 1:3 t 'T' with points