import time


def wait_time(sec):
    timer = sec
    while timer > 0:
        time.sleep(0.985)
        timer -= 1
