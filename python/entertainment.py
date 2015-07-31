#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'ilia'

from color.colorize import Color
import random
import sys
import time

class Functional(object):
    def __init__(self):
        pass
    @staticmethod
    def perform_test():
        squares = map(lambda x: x * x, range(0, 4))
        print(Color("Squares: %s" % squares).as_green())

        names = ['Маша', 'Петя', 'Вася']
        code_names = ['Шпунтик', 'Винтик', 'Фунтик']

        print("Names:")
        map(lambda nme: print("\t{0}".format(nme)), map(lambda x: "" + x  + ": " + random.choice(code_names), names))

        print("Hashes")
        map(lambda nme: print("\t{0}".format(nme)), map(hash, names))

        sentences = ['капитан джек воробей',
                     'капитан дальнего плавания',
                     'ваша лодка готова, капитан']

        # cap_count = 0
        # for sentence in sentences:
        #     cap_count += sentence.count('капитан')

        cap_count = reduce(lambda a,x: a + x.count('капитан'), sentences, 0)
        print("Captains count: {0}".format(cap_count))

        people = [{'имя': 'Маша', 'рост': 160},
            {'name': 'Саша', 'рост': 80},
            {'name': 'Паша'}]

        height_total = 0
        height_count = 0
        for person in people:
            if 'рост' in person:
                height_total += person['рост']
                height_count += 1

        if height_count > 0:
            average_height = height_total / height_count
            print(Color("Avegate height: {0}".format(average_height)).as_blue())

        def filter_person(p_person):
            if 'рост' in p_person:
                return True
            return False

        have_height = filter(lambda p: True if 'рост' in p else False, people)
        [print('Next person: {0}'.format(res)) for res in have_height]

        def reduce_func((hei, cnt), nxt):
            hei += nxt['рост']
            cnt += 1

            return hei, cnt

        hei, cnt = reduce(reduce_func, have_height, (0, 0))
        print("Reduce result:\n\thei: %s\n\tcnt: %s" % (hei, cnt))


class CarsGame(object):
    def __init__(self):
        pass

    @staticmethod
    def imperative_run():
        time = 5
        car_positions = [1, 1, 1]

        while time:
            # decrease time
            time -= 1

            print('')
            for i in range(len(car_positions)):
                # move car
                if random.random() > 0.3:
                    car_positions[i] += 1

def template_print_required(func):
    def wrapper(self, *args, **kwargs):
        if not self.template:
            self.template = map(lambda x: self.template.append(''), range(self.line_nums))
            self.print_template()
        return func(self, *args, **kwargs)

    return wrapper

class Utils(object):
    def __init__(self):
        pass

    @staticmethod
    def overprint_test():
        for i, k in enumerate(range(15)):
            #print(str(i) + " ###\r"),
            sys.stdout.write('{0} \r'.format(i))
            sys.stdout.flush()
            time.sleep(0.2)

        sys.stdout.write('\n')

    @staticmethod
    def overprint_up():
        sys.stdout.write('First string\n')
        time.sleep(0.5)
        sys.stdout.write('Second string\n')
        time.sleep(0.5)
        #move cursor up two lines
        sys.stdout.write('\033[<{0}>A'.format(2))
        sys.stdout.write('\rThird string\n\n')
        time.sleep(0.5)

    @staticmethod
    def cursor_up_to(lines=0):
        if not lines: return
        sys.stdout.write('\033[<{0}>A'.format(lines))

    @staticmethod
    def cursor_down_to(lines=0):
        if not lines: return
        sys.stdout.write('\033[<{0}>B\r'.format(lines))

    @staticmethod
    def cursor_save():
        sys.stdout.write('\033[s')

    @staticmethod
    def cursor_restore():
        sys.stdout.write('\033[u')

    @staticmethod
    def carriage_return():
        sys.stdout.write('\r')

    class LinePrinter(object):
        def __init__(self, line_nums=1):
            self.__current_line = -1
            self.__line_nums = line_nums
            self.__template = []

        @property
        def template(self):
            return self.__template

        @template.setter
        def template(self, value):
            self.__template = value

        @property
        def line_nums(self):
            return self.__line_nums

        @template_print_required
        def set_text(self, line_pos=0, text=''):
            if line_pos > len(self.template): raise IndexError

            #Utils.cursor_save()
            self.template[line_pos] = text
            Utils.cursor_up_to(len(self.template))
            Utils.carriage_return()
            self.print_template()
            #Utils.cursor_restore()

            return self

        def new_line(self):
            sys.stdout.write('\n')

        def print_template(self):
            map(lambda x: sys.stdout.write('{0}\n'.format(x)), self.template)

def main():
    printer = Utils.LinePrinter(3)
    printer.set_text(text='Test_text', line_pos=1)
    time.sleep(1)
    printer.set_text(text='Test_text1', line_pos=2)
    time.sleep(1)
    printer.set_text(text='Test_text3', line_pos=0)
    time.sleep(1)

    #printer.new_line()

if __name__ == '__main__':
    main()