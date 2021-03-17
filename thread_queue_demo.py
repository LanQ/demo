# code=utf-8

from threading import Thread
import time
import queue

q = queue.Queue()

class myClassA(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while True:
            print('A')
            q.put('q')

class myClassB(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            print('B')


myClassA()
myClassB()

s = time.time()

while time.time() - s < 3:
    print(q.get())