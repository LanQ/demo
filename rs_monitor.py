# coding=utf-8
import os
import subprocess
import time
import xlwings as xw
import matplotlib.pyplot as plt

def decode_cpustr(cpustr=[]):
    # ['cpu', '178689', '80601', '266586', '4331318', '6918', '39547', '29670', '0', '0', '0']
    # 从左往右一共 11 列哦
    # CPU 编号：第一行是 CPU 的累加
    # user（us）：用户态 CPU 的时间，不包括下面的 nice 时间，但包括了 guest 时间
    # nice（ni）：低优先级用户态 CPU 的时间，就是进程的 nice 值被调整为 1-19 之间时的 CPU 时间；注意 nice 可取值范围是 -20 到 19，数值越大，优先级反而越低
    # system（sys）：内核态 CPU 的时间
    # idle（id）：空闲时间，它不包括等待 I/O 的时间（iowait）
    # iowait（wa）：等待 I/O 的 CPU 时间
    # irq（hi）：处理硬中断的 CPU 时间
    # softirq（si）：处理软中断的 CPU 时间
    # steal（st）：当系统运行在虚拟机中的时间，被其他虚拟机占用的 CPU 时间
    # guest：通过虚拟化运行其他操作系统的时间，就是运行虚拟机的 CPU 时间
    # guest_nice（gnice）：以低优先级运行虚拟机的时间
    cpuinfo = {
        'user': int(cpustr[1]),
        'nice': int(cpustr[2]),
        'system': int(cpustr[3]),
        'idle': int(cpustr[4]),
        'iowait': int(cpustr[5]),
        'irq': int(cpustr[6]),
        'softirq': int(cpustr[7]),
        'total': int(cpustr[1]) + int(cpustr[2]) + int(cpustr[3]) + int(cpustr[4]) + int(cpustr[5]) + int(cpustr[6]) + int(cpustr[7])
    }
    return cpuinfo

def getCpu(sample_time = 1):

    sample_time = sample_time
    cmd = 'adb shell cat /proc/stat'
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        cpustr_first = p.stdout.read().decode('utf-8').split('\r\n')[0].split()
        cpu_first = decode_cpustr(cpustr_first)
    except Exception as e:
        print(e)

    time.sleep(sample_time)

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        cpustr_next = p.stdout.read().decode('utf-8').split('\r\n')[0].split()
        cpu_next = decode_cpustr(cpustr_next)
    except Exception as e:
        print(e)

    # print(cpu_first, cpu_next)
    cpu_average_usage = 1 - (cpu_next["idle"] - cpu_first["idle"])/(cpu_next["total"] - cpu_first["total"])

    return cpu_average_usage, time.time()

def get_result():
    file_path = r'D:/test.xlsx'
    xw.Book(file_path)  # 固定打开表格
    wb = xw.books.active  # 在活动app
    sht = wb.sheets['sheet1']

    data_time = 60
    sample_time = 3

    rows = data_time / sample_time
    row = 1
    #设置标题
    sht.range(f'a{row}').value = [‘时间’, ‘CPU平均使用率’]
    for row in range(rows):
        cpu_average_usage, t = getCpu()
        sht.range(f'a{row+1}').value = [t, cpu_average_usage]

    # sheet = xw.Book('1.xlsx').sheets[0]
    # chart = sheet.charts.add()
    # # 数据源：sheet.range('A1:C7')，或者sheet.range('A1').expand()
    # chart.set_source_data(sheet.range('A1').expand())
    # chart.chart_type = 'line'  # 线形
    # title = '商品销量'  # 标题名称
    # chart.api[1].SetElement(2)  # 显示标题
    # chart.api[1].ChartTitle.Text = title  # 设置标题名称
    # chart.api[1].SetElement(302)  # 在轴下方显示主要类别轴标题。
    # chart.api[1].Axes(1).AxisTitle.Text = "日期"  # 横轴标题名称
    # chart.api[1].SetElement(311)  # 在轴旁边显示主要类别的轴标题。
    # chart.api[1].Axes(2).AxisTitle.Text = "销量"  # 纵轴标题名称


if __name__ == '__main__':
    cpu_average_usage, t = getCpu()
    print(f'{t}: {cpu_average_usage}')
