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

#(ttl, cnt) = reduce(lambda (ta, ca), x: print(x['рост']), people, (0, 0))

# print("total: {0}".format(ttl))
# print("count: {0}".format(cnt))

import clipboard

clipboard.copy("Pwd")