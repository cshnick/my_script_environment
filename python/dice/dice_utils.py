from .dice import Animal, RedDice, BlueDice, Dice
from typing import List, Tuple
from collections import Counter, namedtuple

RollRes = namedtuple('RollRes', ['label', 'percent', 'count'])


def gen_pairs():
    animal_list = animals_array()
    res: List[Tuple[Animal, Animal]] = []
    for animal in Animal:
        if animal != Animal.Undefined:
            animal_list.append(animal)

    def iter_closure():
        while len(animal_list) > 1:
            cur: Animal = animal_list[0]
            del (animal_list[0])
            for animal in animal_list:
                res.append((cur, animal))
            iter_closure()

    iter_closure()

    return res


def animals_array() -> List[Animal]:
    animal_list: List[Animal] = []
    for animal in Animal:
        if animal != Animal.Undefined:
            animal_list.append(animal)
    return animal_list


def _roll_animals(bound: int, dice: Dice):
    acnt: Counter = Counter()
    for i in range(bound):
        acnt[dice.roll()] += 1

    return acnt.keys(), acnt.values()


def pairs_to_labels() -> List[str]:
    return [f'{a1.name} {a2.name}' for a1, a2 in gen_pairs()]


def roll_pairs(bound: int):
    bd = BlueDice()
    rd = RedDice()
    acnt: Counter = Counter()

    for i in range(bound):
        tmp_list = []
        tmp_list.append(bd.roll().name[0])
        tmp_list.append(rd.roll().name[0])
        tmp_list.sort()
        acnt[' '.join(tmp_list)] += 1

    return acnt.keys(), acnt.values()


def roll_red_animals(bound: int = 10):
    return _roll_animals(bound, RedDice())


def roll_blue_animals(bound: int = 10):
    return _roll_animals(bound, BlueDice())
