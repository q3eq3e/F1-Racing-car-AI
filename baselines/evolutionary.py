from abc import ABC
import numpy as np
from F1_track.envs.F1_track import F1Track
import gymnasium

env = gymnasium.make("F1_track/F1Track-v0").env
# env = gymnasium.make("F1_track:F1_track/F1Track-v0").env


def evaluate(x):
    env.reset()[0]  # random initial state
    reward = 0
    for gene in x:
        _, reward, finished, terminated, _ = env.step(*gene)
        if finished or terminated:
            break
    return reward  # only last reward


class EvolutionarySolver(ABC):
    def __init__(self, dimensionality, minimalize: bool) -> None:
        super().__init__()
        self.size = dimensionality
        # whether the problem is minimalized or not
        self.minimalization = minimalize

    def get_parameters(self) -> dict[str, any]:
        """Returns a dictionary of hyperparameters"""
        return {
            "size": self.size,
            "minimalization": self.minimalization,
        }

    def get_random_point(self) -> np.ndarray:
        # sapmles from only [-1,1) not [-1,1]
        return np.random.sample((self.size, 2)) * 2 - 1

    def initialize_population(self, pop_size):
        # random uniform distribution
        population = np.empty(shape=pop_size, dtype=np.ndarray)
        for i, x in enumerate(population):
            population[i] = self.get_random_point()
        return population

    def rate(self, q, population):
        return np.array([q(osobnik) for osobnik in population])

    def find_best(self, population, quality):
        if self.minimalization:
            idx = np.argmin(quality)
        else:
            idx = np.argmax(quality)
        return population[idx], quality[idx]

    def roulette_reproduction(self, population, quality):
        min_q = min(quality)
        if self.minimalization:
            # lepiej max_q - quality i wtedy to zachowa prawdopodobienstwa jakie powinny byc
            epsilon = 1e-10
            quality = 1 / (quality - min_q + epsilon)

        repr_val = np.empty(shape=len(quality))
        for i, q in enumerate(quality):
            repr_val[i] = q - min_q

        repr_val_sum = sum(repr_val)

        # creating cdf of reproduction with first specimen
        repr_cdf = [repr_val[0] / repr_val_sum]
        # for the rest
        for val in repr_val[1:]:
            repr_cdf.append(val / repr_val_sum + repr_cdf[-1])

        repr_cdf[-1] = 1.0  # correcting last
        # reproducing population
        reproduced_population = np.empty(len(population), dtype=np.ndarray)
        for i in range(len(population)):
            random_number = np.random.rand()
            for val, x in zip(repr_cdf, population):
                if random_number <= val:
                    reproduced_population[i] = x
                    break

        return np.array(reproduced_population, dtype=np.ndarray)

    def averaging_crossover(self, population):
        children = np.empty(len(population), dtype=np.ndarray)

        parents = np.random.choice(population, size=(len(population), 2))
        for idx, p in enumerate(parents):
            p1, p2 = p
            weight = np.random.sample()
            child = p1 * weight + p2 * (1 - weight)
            children[idx] = child

        return np.array(children, dtype=np.ndarray)

    def gauss_mutation(self, population, sigma):
        mutated = []
        for x in population:
            mutated.append(x + sigma * np.random.normal())

        return np.array(mutated, dtype=np.ndarray)

    def solve(self, pop_size, t_max, sigma, q=evaluate):
        t = 0
        # lepiej inicjalizacje wydzielic zeby mozna bylo zaczac od konkretnej lub eksperckiej
        curr_popoulation = self.initialize_population(pop_size)
        curr_rate = self.rate(q, curr_popoulation)
        avg_rate = [curr_rate.mean()]
        x_best, o_best = self.find_best(curr_popoulation, curr_rate)
        best_rate = [o_best]
        while t < t_max:
            # reprodukcja
            curr_popoulation = self.roulette_reproduction(curr_popoulation, curr_rate)
            # krzyzowanie
            curr_popoulation = self.averaging_crossover(curr_popoulation)
            # mutacja
            curr_popoulation = self.gauss_mutation(curr_popoulation, sigma)
            # ocena
            curr_rate = self.rate(q, curr_popoulation)
            x_t, o_t = self.find_best(curr_popoulation, curr_rate)
            if self.minimalization:
                if o_t < o_best:
                    o_best = o_t
                    x_best = x_t
            else:
                if o_t > o_best:
                    o_best = o_t
                    x_best = x_t
            avg_rate.append(curr_rate.mean())
            best_rate.append(o_t)
            t += 1

        return x_best, o_best, avg_rate, best_rate
