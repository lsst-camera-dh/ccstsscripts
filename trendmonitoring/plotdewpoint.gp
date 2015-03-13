set term png
set output 'ts_dewpoint.png'
set title "Cleanroom Dew Point Plot\nvs. time"
set xlabel "Date\nTime"
set timefmt "%Y-%m-%d %H:%M:%S"
set yrange [ 10. : 55. ]
set xdata time
set ylabel "Dewpoint\nF"
set format x "%d/%m\n%H:%M"
set grid
set key left
plot 'ts_dewpoint.dat' using 1:3
replot
# t '', \
#     'ts_dewpoint.dat' using 1:3 t 'T' with points