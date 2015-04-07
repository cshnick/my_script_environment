#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import readline
from color.colorize import Color
import signal
import achivement_engine.PyAeCore as Ae
import os
import external.texttable as tt


os.environ['AE_DELEGATES_PATH'] = os.getcwd() + "/achivement_engine/Calcs"
os.environ['VERBOSE'] = '1'

v_mul_table = 'Таблица умножения'
v_show_statistics = 'Статистика'
v_show_achievements = 'Достижения'
v_stop = 'Стоп'
v_new_user = 'Новый пользователь'
v_new_project = 'Новый проект'

f_statement = "Statement"
f_result = "Result"
f_success = "Success"

f_id = "id"
f_ach_id = "AchivementId"
f_start = "Start"
f_finish = "Finish"
f_time = "Time"
f_actTime = "ActionTime"
f_session = "Session"
f_name = "Name"
f_session_id = "SessionId"
f_description = "Description"
f_condition = "Condition"


class MTGenerator(object):
    def __init__(self):
        self.__mt = []
        self.__gen_mt()

    def __gen_mt(self):
        random.seed()
        for i in range(2, 10):
            for j in range(2, 10):
                self.__mt.append((i, j))

    def get_random(self):
        if not self.__mt:
            print Color('Ты прошел всю таблицу умножения, начинаем заново!').as_blue()
            self.__gen_mt()
        mt_length = self.__mt.__len__()
        rand_index = random.randint(0, mt_length - 1)
        mul_pair = self.__mt[rand_index]
        del self.__mt[rand_index]

        return mul_pair


class SimpleCompleter(object):

    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        # response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response


class Ask:
    great = 0
    good = 0
    total = 0
    e = Ae.EngineImpl()
    e.init("Таблица умножения", "Илья")

    def __init__(self):
        pass

    @staticmethod
    def print_stat():
        print 'exit'
        print Color('Всего попыток: ').as_cyan() + Color(str(Ask.total)).as_white()
        print Color('=================').as_white()
        print Color('Отлично:       ').as_green() + Color(str(Ask.great)).as_white()
        print Color('Неплохо:       ').as_yellow() + Color(str(Ask.good)).as_white()
        print Color('Ошибок:        ').as_purple() + Color(str(Ask.total - Ask.great - Ask.good)).as_white()


    @staticmethod
    def add_action(ans, right, str):
        cxx_dct = Ae.map_sv()
        cxx_dct[f_statement] = Ae.variant(str)
        cxx_dct[f_result] = Ae.variant(ans)
        cxx_dct[f_success] = Ae.variant(right)
        Ask.e.addAction(cxx_dct)

    @staticmethod
    def print_achievements(p_achievements):
        for k in p_achievements:
            table = tt.Texttable()
            strg =  "Заработано достижение %s" % k[f_name].toString()
            table.add_row([strg,])
            print(table.draw())
            print(Color(k[f_description].toString()).as_cyan())

        return True

    @staticmethod
    def ask_mt(r1, r2):
        question = '' + str(r1) + 'x' + str(r2) + '='
        ans = raw_input(question)
        if not ans:
            Ask.e.end()
            Ask.print_stat()
            raise Exception("End of mul table checking")

        right = r1*r2
        Ask.add_action(ans=ans, right=(int(right) == int(ans)), str=question)
        achieves = Ask.e.take_ach_params()
        Ask.print_achievements(p_achievements=achieves)

        return ans, right

    @staticmethod
    def do_ask_mt(r1, r2, toplevel=True):
        (ans, right) = Ask.ask_mt(r1, r2)
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
            Ask.do_ask_mt(r1, r2, toplevel=False)

    @staticmethod
    def mul_table_loop():
        mtg = MTGenerator()
        Ask.e.init("Таблица умножения", "Илья")
        Ask.e.begin()
        while True:
            r1, r2 = mtg.get_random()
            try:
                Ask.do_ask_mt(r1, r2, toplevel=True)
            except:
                break

    @staticmethod
    def do_ask_choice():
        sans = Color('Что будем делать?').as_yellow()
        try:
            ans = raw_input(sans + ' (Просто нажми ввод,  чтобы Начать работать с таблицей умножения)\n')
        except ValueError:
            return False
        if not ans:
            ans = v_mul_table
            print ans

        if ans == v_mul_table:
            print Color("------------------").as_green()
            Ask.mul_table_loop()

        elif ans == v_stop:
            Ask.e.dropTables()
            return False
        elif ans == v_new_user:
            Ask.e.addUser('Игорек', '')
        elif ans == v_new_project:
            Ask.e.addProject(v_mul_table)

        return True


def st_handler(signum, frame):
    Ask.e.end()
    Ask.print_stat()
    exit(0)


def main():
    signal.signal(signal.SIGINT, st_handler)
    # Register our completer function
    readline.set_completer(SimpleCompleter([v_mul_table,
                                            v_show_statistics,
                                            v_show_achievements,
                                            v_new_user,
                                            v_new_project,
                                            v_stop])
                           .complete)
    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')
    res = True
    while res:
        res = Ask.do_ask_choice()


if __name__ == '__main__':
    main()
