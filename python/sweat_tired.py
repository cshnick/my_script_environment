#!/usr/bin/python2

from time import sleep
import pymouse
import logging

_INTERVAL = 60  # s
logging.basicConfig(filename='sweat_tired.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    m = pymouse.PyMouse()
    prev_x, prev_y = m.position()
    while True:
        sleep(_INTERVAL)
        x, y = m.position()
        if (prev_x, prev_y) == (x, y):
            logging.info('script initiated')
            bound = 300
            for i in range(bound):
                sleep(.01)
                offset = -1 if i > bound / 2 else 1
                x, y = x + offset, y + offset
                m.move(x, y)
        prev_x, prev_y = m.position()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
