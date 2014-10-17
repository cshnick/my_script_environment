#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
from color.colorize import Color
import signal

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
    
  def ask(self, r1, r2):
    ask = raw_input('' + str(r1) + 'x' + str(r2) + '=')
    if not ask:
      Ask.print_stat()
      exit(0)
    right = r1*r2
    return (ask, right)

  def do_ask(self, r1, r2, toplevel=True):
    (ans, right) = self.ask(r1, r2)
    Ask.total = Ask.total + 1
    if int(right) == int(ans):
      mesge = 'Крутяк!!!!' if toplevel else 'Неплохо, но можно было бы и с первой попытки'
      col = 'green' if toplevel else 'yellow'
      print Color(mesge).as_color(col)
      if toplevel:
	Ask.great = Ask.great + 1
      else:
	Ask.good = Ask.good + 1
    else:
      print Color('Попробуй еще раз').as_purple()
      self.do_ask(r1, r2, toplevel=False)
    
def ST_handler(signum, frame):
    Ask.print_stat()
    exit(0)
  
def main():
  signal.signal(signal.SIGINT, ST_handler)
  while True:
    r1 = random.randint(2, 4)
    r2 = random.randint(2, 9)
    Ask().do_ask(r1, r2, toplevel=True)
  
if __name__ == '__main__':
  main()
