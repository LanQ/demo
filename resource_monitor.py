# coding: utf-8
import re
import time
from threading import Thread
from typing import Callable, Any, Iterable, Mapping

from adbutils import adb, errors


class CPU(Thread):
    def __init__(self, record_time: float = 1, step_time: float = 5) -> None:
        Thread.__init__(self)
        self.setDaemon(True)
        self.total_cpu_usage = ''
        self.top = ''
        self.cpu_per_process = {}
        self.record_time = record_time
        self.step_time = step_time
        self.running = True
        self.is_adb_device_exist = False
        self.d = None

    def _get_top(self):
        # COLUMNS=512 进行宽度设置 若不设置args列显示不全
        # top -n 1
        # -m 500 最多显示500个进程
        # -s 6 按cpu使用列排序
        try:
            if not self.is_adb_device_exist:
                self.d = adb.device()
                self.is_adb_device_exist = True
                print(id(self.d))

            self.top = self.d.shell('COLUMNS=512 top -n 1 -m 500 -s 6')
        except Exception as e:
            # print(f'未找到设备 或 连接不上设备 {e}')
            self.is_adb_device_exist = False
            self.top = ''

    def decode_total_cpu_usage_from_top(self) -> str:
        if self.top:
            for line in self.top.splitlines():
                if 'cpu' in line:
                    # 800%cpu  42%user   0%nice  71%sys 684%idle   0%iow   3%irq   0%sirq   0%host
                    # 进行解析
                    pattern = r'\d+'
                    numbers = re.findall(pattern, line)
                    if numbers:
                        number_cpu = float(numbers[0])
                        number_idle = float(numbers[4])
                        self.total_cpu_usage = (number_cpu - number_idle) / number_cpu
                    break
        else:
            self.total_cpu_usage = ''

    def decode_each_process_cpu_usage_from_top(self) -> str:
        if self.top:
            data_lines = self.top.splitlines()[5:]
            for line in data_lines:
                #'  1457 system       18  -2  16G 315M 242M S  0.0   8.6   7:15.33 system_server'
                line = line.strip()
                line_split = line.split()

                # 处理个别行中的异常字符ANSI code https://tforgione.fr/posts/ansi-escape-codes/
                # ['\x1b[1m', '23808', 'shell', '20', '0', '10G', '3.0M', '1.8M', 'R', '45.7', '0.0', '0:00.11', 'top', '-n', '1', '-m', '500', '-s', '6']
                # ['\x1b[m']
                if '\x1b[' in line_split[0]:
                    line_split = line_split[1:]

                print(line_split)

                if line_split:
                    row_cpu = line_split[8]
                    # 适配args含有空格情况
                    # '1057 root         20   0  10G 1.7M 1.5M S  5.7   0.0   0:28.55 msm_irqbalance -f /vendor/etc/msm_irqbalance.conf',
                    row_args = ''.join(line_split[11:])
                    pid = line_split[0]
                    self.cpu_per_process[row_args] = row_cpu, pid

        else:
            self.cpu_per_process = {}

    def run(self) -> None:
        deadtime = time.time() + self.record_time
        while self.running and (time.time() < deadtime):
            self._get_top()
            # 解析总体cpu使用情况
            self.decode_total_cpu_usage_from_top()
            # 解析每个pid cpu使用情况
            self.decode_each_process_cpu_usage_from_top()
            # 等待步进时间step_time进行下次采样
            time.sleep(self.step_time)
        self.running = False

    def stop(self):
        self.running = False


def show_cpu():
    record_time = 60
    step_time = 1
    cpu = CPU(record_time=record_time, step_time=step_time)
    cpu.start()

    import matplotlib.pyplot as plt

    x = []
    y = []

    deadtime = time.time() + record_time
    while time.time() < deadtime:
        print(f'cpu.total_cpu_usage: {cpu.total_cpu_usage}')

        if cpu.cpu_per_process:
            for k, v in cpu.cpu_per_process.items():
                print(k, v)
        time.sleep(step_time)

        x.append(time.time())
        y.append(cpu.total_cpu_usage)
        plt.clf()

        plt.plot(x, y)
        plt.pause(0.1)
        plt.ioff()


class Memory(Thread):

    def __init__(self, record_time: float = 1, step_time: float = 5) -> None:
        Thread.__init__(self)
        self.setDaemon(True)
        self.record_time = record_time
        self.step_time = step_time
        self.step_time = step_time
        self.is_adb_device_exist = False
        self.d = None
        self.memory = ''
        self.running = True
        self.memory_used = ''
        self.memory_per_process = {}

    def _get_memory(self):
        try:
            if not self.is_adb_device_exist:
                self.d = adb.device()
                self.is_adb_device_exist = True
                print(id(self.d))

            self.memory = self.d.shell('dumpsys meminfo')
        except Exception as e:
            # print(f'未找到设备 或 连接不上设备 {e}')
            self.is_adb_device_exist = False
            self.memory = ''

    def decode_total_used_memory_from_dumpsys(self):
        if self.memory:
            memory_summary = self.memory.splitlines()[-6:]
            memory_free = int(memory_summary[1].split(': ')[1].split('K (')[0].replace(',', ''))
            memory_total = int(memory_summary[0].split(': ')[1].split('K (')[0].replace(',', ''))
            self.memory_used = memory_total - memory_free
        else:
            self.memory_used = ''

    def decode_each_process_memory_pss_usage_from_dumpsys(self):
        if self.memory:
            memory_pss = self.memory.split('Total PSS by process:')[1].split('Total PSS by OOM adjustment:')[0].strip()
            memory_pss_lines = memory_pss.splitlines()
            for line in memory_pss_lines:
                #  '        693K: android.hidl.allocator@1.0-service (pid 977)'
                process = line.split(': ')[1].split(' (')[0]
                row_memory = line.split('K: ')[0].strip().replace(',', '')
                pid = line.split('(pid ')[1][:-1]
                self.memory_per_process[process] = row_memory, pid
        else:
            self.memory_per_process = {}

    def run(self) -> None:
        deadtime = time.time() + self.record_time
        while self.running and (time.time() < deadtime):
            self._get_memory()
            self.decode_total_used_memory_from_dumpsys()
            self.decode_each_process_memory_pss_usage_from_dumpsys()
            print(self.memory_used)
            print(self.memory_per_process)
            time.sleep(self.step_time)


if __name__ == '__main__':
    memory = Memory(record_time=60)
    memory.start()
    time.sleep(60)
