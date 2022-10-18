import matplotlib.pyplot as plt
import scipy as sp
from scipy.stats import uniform, norm
import numpy as np
from numpy import pi
from functools import cmp_to_key
from k_borda import k_borda
from bloc import bloc
from sntv import sntv
from greedy_monroe import greedy_monroe


class Generator:
    def __init__(self, num_sampling=100):
        self.num_sampling = num_sampling

    def uniform_rectangle(self, num_candidates, num_voters, a=3, b=3):
        candidates_list, voters_list = [], []
        for _ in range(self.num_sampling):
            candidates_list.append(list(
                zip(uniform.rvs(loc=0, scale=a, size=num_candidates),
                    uniform.rvs(loc=0, scale=b, size=num_candidates))))

            voters_list.append(list(
                zip(uniform.rvs(loc=0, scale=a, size=num_voters), uniform.rvs(loc=0, scale=b, size=num_voters))))

        return candidates_list, voters_list

    def normal(self, num_candidates, num_voters, mean=0, sigma=1):
        candidates_list, voters_list = [], []
        for _ in range(self.num_sampling):
            candidates_list.append(list(
                zip(norm.rvs(loc=mean, scale=sigma, size=num_candidates),
                    norm.rvs(loc=mean, scale=sigma, size=num_candidates))))

            voters_list.append(list(
                zip(norm.rvs(loc=mean, scale=sigma, size=num_voters),
                    norm.rvs(loc=mean, scale=sigma, size=num_voters))))
        return candidates_list, voters_list

    def two_overlapping_circles(self, num_candidates, num_voters, r1=5, o1=(-4, 0), r2=5, o2=(4, 0)):
        candidates_list, voters_list = [], []

        for i_samples in range(self.num_sampling):
            r = r1 * np.sqrt(uniform.rvs(size=(num_candidates + 1) // 2))
            theta = np.array(uniform.rvs(size=(num_candidates + 1) // 2)) * 2 * pi

            x_candidates = o1[0] + (r * np.cos(theta))
            y_candidates = o1[1] + (r * np.sin(theta))

            candidates_list.append(list(zip(x_candidates, y_candidates)))

            r = r1 * np.sqrt(uniform.rvs(size=(num_voters + 1) // 2))
            theta = np.array(uniform.rvs(size=(num_voters + 1) // 2)) * 2 * pi

            x_candidates = o1[0] + (r * np.cos(theta))
            y_candidates = o1[1] + (r * np.sin(theta))

            voters_list.append(list(zip(x_candidates, y_candidates)))

            r = r2 * np.sqrt(uniform.rvs(size=num_candidates // 2))
            theta = np.array(uniform.rvs(size=num_candidates // 2)) * 2 * pi

            x_voters = o2[0] + (r * np.cos(theta))
            y_voters = o2[1] + (r * np.sin(theta))

            candidates_list[i_samples].extend(list(zip(x_voters, y_voters)))

            r = r2 * np.sqrt(uniform.rvs(size=num_voters // 2))
            theta = np.array(uniform.rvs(size=num_voters // 2)) * 2 * pi

            x_voters = o2[0] + (r * np.cos(theta))
            y_voters = o2[1] + (r * np.sin(theta))

            voters_list[i_samples].extend(list(zip(x_voters, y_voters)))
        return candidates_list, voters_list


def data_to_voting(voting_algorithm, data, **kwargs):
    candidates_list, voters_list = data
    mapping = dict()
    for i_sample in range(len(candidates_list)):
        for j in range(len(candidates_list[i_sample])):
            mapping[(i_sample, candidates_list[i_sample][j])] = j
            mapping[(i_sample, j)] = candidates_list[i_sample][j]

    votings = [[] for _ in range(len(candidates_list))]
    for i_sample in range(len(voters_list)):
        for voter in voters_list[i_sample]:
            def squared_dist(p1):
                return (voter[0] - p1[0]) ** 2 + (voter[1] - p1[1]) ** 2

            # print(voter, sorted(candidates_list[i_sample], key=squared_dist))
            # plt.scatter(voter[0], voter[1], color = "blue")
            # xs, ys = zip(*sorted(candidates_list[i_sample], key=squared_dist))
            # plt.scatter(xs, ys, c=[squared_dist((x, y)) for x, y in zip(xs, ys)], cmap='Reds')
            # plt.show()
            votings[i_sample].append(
                [mapping[(i_sample, x)] for x in sorted(candidates_list[i_sample], key=squared_dist)])

    result = []
    for i_sample, voting in enumerate(votings):
        result.append([mapping[(i_sample, x)] for x in voting_algorithm(voting, **kwargs)])
    return result


class Vizualizator:
    def __init__(self, votings_results, data):
        self.votings_results = votings_results
        self.data = data

    def vizualize_results(self):
        xs_winners, ys_winners = [], []
        xs_voters, ys_voters = [], []
        xs_candidates, ys_candidates = [], []

        voters, candidates = data

        for x in voters:
            for q in x:
                xs_voters.append(q[0])
                ys_voters.append(q[1])
        plt.scatter(xs_voters, ys_voters, color="#e56b6f", s=1)

        for x in candidates:
            for q in x:
                xs_candidates.append(q[0])
                ys_candidates.append(q[1])
        plt.scatter(xs_candidates, ys_candidates, color="#48cae4", s=1)

        for voting_result in self.votings_results:
            for p in voting_result:
                xs_winners.append(p[0])
                ys_winners.append(p[1])
        plt.scatter(xs_winners, ys_winners, color="green", s=5)
        plt.show()


if __name__ == "__main__":
    generator = Generator(num_sampling=100)
    data = generator.uniform_rectangle(200, 200, a=3, b=3)
    results = data_to_voting(k_borda, data, size_of_committee=15, number_of_scored_candidates=3)
    vis = Vizualizator(results, data)
    vis.vizualize_results()
