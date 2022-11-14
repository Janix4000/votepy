import matplotlib.pyplot as plt
from scipy.stats import uniform, norm
import numpy as np
from numpy import pi
from functools import cmp_to_key

from votepy.rules.chamberlin_courant_impl import chamberlin_courant_greedy
from votepy.rules.k_borda_impl import k_borda
from votepy.rules.bloc_impl import bloc
from votepy.rules.sntv_impl import sntv


# from greedy_monroe import greedy_monroe


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
                zip(uniform.rvs(loc=0, scale=a, size=num_voters),
                    uniform.rvs(loc=0, scale=b, size=num_voters))))

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


def data_to_voting(voting_algorithm, data, size_of_committee, *rule_args):
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

            def manhattan_dist(p1):
                return abs(voter[0] - p1[0]) + abs(voter[1] - p1[1])

            votings[i_sample].append(
                [mapping[(i_sample, x)] for x in sorted(candidates_list[i_sample], key=squared_dist)])

    result = []
    for i_sample, voting in enumerate(votings):
        # if i_sample % 10 == 0:
        #     print(i_sample)
        result.append([mapping[(i_sample, x)] for x in voting_algorithm(voting, size_of_committee, *rule_args)])
    return np.array(result)


class Visualizator:
    def __init__(self, votings_results, data):
        self.votings_results = votings_results
        self.data = data

    def visualize_results(self, save_to_file=False, name="None", title=""):
        xs_winners, ys_winners = [], []
        xs_voters, ys_voters = [], []
        xs_candidates, ys_candidates = [], []

        voters, candidates = self.data

        def alpha_parameter(k=0.7):
            size = np.product(np.array(voters).shape) + np.product(np.array(candidates).shape) + np.product(
                self.votings_results.shape)
            return k / min(1.4, np.log10(size) + 0.1)

        for x in voters:
            for q in x:
                xs_voters.append(q[0])
                ys_voters.append(q[1])
        fig = plt.figure(figsize=(8, 6), dpi=80)
        plt.scatter(xs_voters, ys_voters, color=(0.9, 0.9, 0.9), s=1, alpha=alpha_parameter() / 10, zorder=0)

        for x in candidates:
            for q in x:
                xs_candidates.append(q[0])
                ys_candidates.append(q[1])
        plt.scatter(xs_candidates, ys_candidates, color=(0.85, 0.85, 0.85), s=1, alpha=alpha_parameter() / 10, zorder=0)

        for voting_result in self.votings_results:
            for p in voting_result:
                xs_winners.append(p[0])
                ys_winners.append(p[1])
        plt.scatter(xs_winners, ys_winners, color=(0.25, 0.25, 0.25), s=5, alpha=0.08, zorder=1)
        plt.legend(["Voters", "Not chosen candidates", "chosen candidates"], framealpha=1, loc=(0, -0.3))
        plt.title(title)
        fig.tight_layout()

        if not save_to_file:
            plt.show()
        else:
            plt.savefig(name)
            plt.clf()
            plt.cla()
            plt.close()


if __name__ == "__main__":
    generator = Generator(num_sampling=1000)
    data = generator.uniform_rectangle(250, 200, a=3, b=3)

    results = data_to_voting(bloc, data, size_of_committee=15)
    vis = Visualizator(results, data)
    vis.visualize_results()
