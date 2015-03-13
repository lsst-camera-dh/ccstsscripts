set term png
set output 'ts_ccdtemperature.png'
set title "CCD/Dewar Temperature Plot\nvs. time"
set xlabel "Date\nTime"
set timefmt "%Y-%m-%d %H:%M:%S"
set yrange [ -120. : 26. ]
set xdata time
set ylabel "Temperature\ndegrees Celsius"
set format x "%d/%m\n%H:%M"
set grid
set key left
plot 'ts_ccdtemperature.dat' using 1:3
replot
# t '', \
#     'ts_ccdtemperature.dat' using 1:3 t 'T' with points