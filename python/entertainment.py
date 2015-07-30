#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'ilia'

from color.colorize import Color
import random

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

from random import random
time = 5
car_positions = [1, 1, 1]

while time:
    # decrease time
    time -= 1

    print('')
    for i in range(len(car_positions)):
        # move car
        if random() > 0.3:
            car_positions[i] += 1

        # draw car
        #print('-' * car_positions[i])


import clipboard
clipboard.copy("Pwd")
