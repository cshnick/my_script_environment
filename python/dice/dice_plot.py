import matplotlib.pyplot as plt
from dice.dice_utils import roll_blue_animals, roll_red_animals, roll_pairs
from dice.dice import Animal
from typing import List


def animals_list_to_plot_labels(animals: List[Animal]):
    return [animal.name for animal in animals]


def plot_blue_animals(bound: int = 10):
    keys, ba = roll_blue_animals(bound)
    plot_animals(animals_list_to_plot_labels(keys), ba, "Blue rolls", '#03A4EC')


def plot_red_animals(bound: int = 10):
    keys, ra = roll_red_animals(bound)
    plot_animals(animals_list_to_plot_labels(keys), ra, "Red rolls", '#EC4134')


def plot_pairs(bound: int = 10):
    keys, pa = roll_pairs(bound)
    plot_animals(keys, pa, 'Paired rolls', '#8E24AA')


def plot_animalsv2():
    fig, ax1 = plt.subplots(figsize=(7, 9))  # Create the figure
    fig.subplots_adjust(left=0.115, right=0.88)
    fig.canvas.set_window_title('Eldorado K-8 Fitness Chart')
    pass


def plot_animals(labels, rolls, comment="Rolls", color='b'):
    width = 1.0
    fig, ax = plt.subplots()

    ax.bar(labels, rolls, width, yerr=None, label=comment, color=color)
    # ax.bar(labels, red_rolls, width, yerr=None, bottom=blue_rolls,
    #        label='Red rolls')

    ax.set_ylabel('Rolls count')
    ax.set_title(comment)
    ax.legend()

    plt.show()


if __name__ == "__main__":
    plot_pairs(100)
