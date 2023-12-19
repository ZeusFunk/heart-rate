import serial
import numpy as np
from scipy.signal import firwin, lfilter
import matplotlib.pyplot as plt

# 设置串口参数
ser = serial.Serial('COM6', 115200)

# 设置滤波器参数
sample_rate = 500  # 采样频率
cutoff_freq = 40   # 截止频率
numtaps = 64       # 滤波器阶数

# 使用firwin()函数设计FIR滤波器
fir_coeff = firwin(numtaps, cutoff_freq/(sample_rate/2))

# 初始化滤波器的z状态
z = np.zeros(numtaps-1)

# 初始化图表
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-')
ax.set_xlim(0, 300)

# 初始化xdata和ydata
xdata, ydata = [], []

try:
    while True:
        # 从串口读取数据
        if ser.in_waiting:
            data = ser.readline().decode('utf-8').strip()
            try:
                heart_rate = int(data)  # 确保数据可以转换为整数
            except ValueError:
                continue  # 如果转换失败，跳过这个数据

            # 应用滤波器
            heart_rate_filtered, z = lfilter(fir_coeff, 1, [heart_rate], zi=z)
            heart_rate_filtered = heart_rate_filtered[0]

            # 更新图表数据
            xdata.append(len(xdata))
            ydata.append(heart_rate_filtered)

            # 保持xdata和ydata的长度为1000
            if len(xdata) > 300:
                xdata = xdata[-300:]
                ydata = ydata[-300:]

            # 更新图表
            line.set_data(list(range(len(ydata))), ydata)  # 使用实际长度的x轴和y轴
            if len(ydata) > 0:
                ax.set_ylim(min(ydata), max(ydata))  # 动态调整y轴范围
            fig.canvas.draw()
            fig.canvas.flush_events()

except KeyboardInterrupt:
    # 停止程序
    plt.close(fig)
    ser.close()
    print("程序已停止")