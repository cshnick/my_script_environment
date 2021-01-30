from enum import Enum
from random import randint, seed
from typing import List


class Animal(Enum):
    Rabbit = 1
    Sheep = 2
    Pig = 3
    Cow = 4
    Horse = 5
    Fox = 6
    Wolf = 7
    Undefined = 8


class Dice:
    sides: List[Animal] = None

    def roll(self) -> Animal:
        rnd: int = randint(0, 11)
        res: Animal = self.sides[rnd]
        return res


class BlueDice(Dice):
    sides: List[Animal] = [
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Sheep,
        Animal.Sheep,
        Animal.Sheep,
        Animal.Pig,
        Animal.Cow,
        Animal.Wolf
    ]


class RedDice(Dice):
    sides: List[Animal] = [
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Rabbit,
        Animal.Sheep,
        Animal.Sheep,
        Animal.Pig,
        Animal.Pig,
        Animal.Horse,
        Animal.Fox,
    ]


def print_roll(b: Animal, r: Animal):
    print(f'{b.name} {r.name}')


def test_roll():
    seed(None, 2)
    b: Dice = BlueDice()
    r: Dice = RedDice()
    for i in range(100):
        print_roll(b.roll(), r.roll())


def test_utils():
    pass


if __name__ == "__main__":
    test_utils()
