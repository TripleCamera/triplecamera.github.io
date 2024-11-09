set terminal svg size 600,600 enhanced font 'Arial,10'  # 设置输出为 SVG
set output 'stats.svg'  # 输出文件名

set style data boxes  # 设置样式为条形图
set style fill solid 1.0 border -1  # 填充样式
# set boxwidth 0.8  # 设置条形宽度
set boxwidth 1
set boxdepth 1

set xlabel "X axis"  # X轴标签
set ylabel "Y axis"  # Y轴标签
set zlabel "Z axis (Height)"  # Z轴标签

# set ticslevel 0  # 将零点放在 X-Y 平面上
set xyplane at 0
set grid z vertical lw 1.0
# set xrange [-0.5:21.5]
# set yrange [-0.5:20.5]
set autoscale noextend
set zrange [0:20]  # Z轴范围
set palette defined (0 "dark-green", 1 "light-green")
set style line 1 lc rgb "dark-green"  # 深绿色 (小于 5)
set style line 2 lc rgb "light-green"  # 浅绿色 (大于等于 5)
set style fill transparent solid 0.7

# set view 60, 30  # 设置观察角度 (水平, 垂直)
set view 60, 120
set grid  # 打开网格

# splot 'data.dat' using 1:2:3 with boxes lc rgb "blue"  # 绘制数据
splot 'data.dat' using 1:2:3:($1 > 5 || $2 > 5 ? 2 : 1) with boxes lc variable
