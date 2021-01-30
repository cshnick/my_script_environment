from dice.dice_plot import plot_blue_animals, plot_red_animals, plot_pairs
from time import perf_counter

if __name__ == "__main__":
    before = perf_counter()
    plot_pairs(1000000)
    print(f'Finished, time elapsed: {perf_counter() - before}')
