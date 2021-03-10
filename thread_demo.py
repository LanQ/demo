from threading import Thread, Condition
import time

count = 0
class Child(Thread):

    def __init__(self, condition):
        self.condition = condition
        super().__init__()

    def run(self):
        global count
        print('child running')
        while True:
            with condition:
                if count != 10:
                    count += 1
                    print(f'child incrementing count to {count}')
                else:
                    print('child notifying')
                    self.condition.notify()
                    return
            time.sleep(1)


if __name__ == '__main__':
    condition = Condition()
    child = Child(condition)
    child.start()
    print('main thread waiting on condition ... ')

    with condition:
        while count != 10:
            condition.wait()
    print('Main thread waking up ')
    child.join()