#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
from color.colorize import Color
import signal
import achivement_engine.AeCore as ae

class Ask:
  great = 0
  good = 0
  total = 0
  @staticmethod
  def print_stat():
    print 'exit'
    print Color('Всего попыток: ').as_cyan() + Color(str(Ask.total)).as_white()
    print Color('=================').as_white()
    print Color('Отлично:       ').as_green() + Color(str(Ask.great)).as_white()
    print Color('Неплохо:       ').as_yellow() + Color(str(Ask.good)).as_white()
    print Color('Ошибок:        ').as_purple() + Color(str(Ask.total - Ask.great - Ask.good)).as_white()
    

  @staticmethod
  def ask(r1, r2):
    ans = raw_input('' + str(r1) + 'x' + str(r2) + '=')
    if not ans:
      Ask.print_stat()
      exit(0)
    right = r1*r2
    return ans, right

  @staticmethod
  def do_ask(r1, r2, toplevel=True):
    (ans, right) = Ask.ask(r1, r2)
    Ask.total += 1
    if int(right) == int(ans):
      mesge = 'Крутяк!!!!' if toplevel else 'Неплохо, но можно было бы и с первой попытки'
      col = 'green' if toplevel else 'yellow'
      print Color(mesge).as_color(col)
      if toplevel:
        Ask.great += 1
      else:
	    Ask.good += 1
    else:
      print Color('Попробуй еще раз').as_purple()
      Ask.do_ask(r1, r2, toplevel=False)
    
def ST_handler(signum, frame):
    Ask.print_stat()
    exit(0)
  
def main():
  signal.signal(signal.SIGINT, ST_handler)

  a = ae.EngineImpl()
  a.begin()
  dct = dict()
  dct['a'] = ae.variant('b')
  dct['b'] = ae.variant('c')
  dct['e'] = ae.variant('f')
  cxx_dct = ae.map_sv(dct)
  cxx_dct['g'] = ae.variant('h')
  a.addAction(cxx_dct)
  a.end()

  while True:
    r1 = random.randint(2, 9)
    r2 = random.randint(2, 9)
    Ask.do_ask(r1, r2, toplevel=True)
  
if __name__ == '__main__':
  main()
