# coding: utf-8
import re
import time
from threading import Thread

from adbutils import adb, errors


class CPU(Thread):
    def __init__(self, record_time: float = 1, step_time: float = 5) -> None:
        Thread.__init__(self)
        self.setDaemon(True)
        self.total_cpu_usage = ''
        self.top = ''
        self.cpu_per_pid = {}
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

    def decode_each_pid_cpu_usage(self) -> str:
        pass

    def run(self) -> None:
        deadtime = time.time() + self.record_time
        while self.running and (time.time() < deadtime):
            self._get_top()
            # 解析总体cpu使用情况
            self.decode_total_cpu_usage_from_top()
            # 解析每个pid cpu使用情况

            # 等待步进时间step_time进行下次采样
            time.sleep(self.step_time)
        self.running = False

    def stop(self):
        self.running = False


if __name__ == '__main__':
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
        time.sleep(step_time)


        x.append(time.time())
        y.append(cpu.total_cpu_usage)
        plt.clf()

        plt.plot(x, y)
        plt.pause(0.1)
        plt.ioff()
