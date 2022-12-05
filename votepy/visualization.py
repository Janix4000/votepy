import math

import matplotlib.pyplot as plt
from scipy.stats import uniform, norm
import numpy as np
from numpy import pi
from functools import cmp_to_key

from votepy.rules.chamberlin_courant import chamberlin_courant_greedy
from votepy.rules.k_borda import k_borda
from votepy.rules.bloc import bloc
from votepy.rules.sntv import sntv
import json
from time import time
from random import shuffle


# from greedy_monroe import greedy_monroe


class Generator:
    def __init__(self, num_sampling=100):
        self.num_sampling = num_sampling

    def uniform_rectangle(self, num_candidates, num_voters, a=6, b=6):
        candidates_list, voters_list = [], []
        for _ in range(self.num_sampling):
            candidates_list.append(list(
                zip(uniform.rvs(loc=-3, scale=a, size=num_candidates),
                    uniform.rvs(loc=-3, scale=b, size=num_candidates))))
            shuffle(candidates_list[-1])

            voters_list.append(list(
                zip(uniform.rvs(loc=-3, scale=a, size=num_voters),
                    uniform.rvs(loc=-3, scale=b, size=num_voters))))
            shuffle(voters_list[-1])

        return candidates_list, voters_list

    def uniform_circle(self, num_candidates, num_voters, r=3, o=(0, 0)):
        candidates_list, voters_list = [], []
        for i_samples in range(self.num_sampling):
            r_point = r * np.sqrt(uniform.rvs(size=(num_candidates + 1)))
            theta = np.array(uniform.rvs(size=(num_candidates + 1))) * 2 * pi

            x_candidates = o[0] + (r_point * np.cos(theta))
            y_candidates = o[1] + (r_point * np.sin(theta))

            candidates_list.append(list(zip(x_candidates, y_candidates)))
            shuffle(candidates_list[-1])

            r_point = r * np.sqrt(uniform.rvs(size=(num_voters + 1)))
            theta = np.array(uniform.rvs(size=(num_voters + 1))) * 2 * pi

            x_candidates = o[0] + (r_point * np.cos(theta))
            y_candidates = o[1] + (r_point * np.sin(theta))

            voters_list.append(list(zip(x_candidates, y_candidates)))
            shuffle(voters_list[-1])
        return candidates_list, voters_list

    def normal(self, num_candidates, num_voters, mean=0, sigma=1.8):
        candidates_list, voters_list = [], []
        for _ in range(self.num_sampling):
            candidates_list.append(list(
                zip(norm.rvs(loc=mean, scale=sigma, size=num_candidates),
                    norm.rvs(loc=mean, scale=sigma, size=num_candidates))))
            shuffle(candidates_list[-1])

            voters_list.append(list(
                zip(norm.rvs(loc=mean, scale=sigma, size=num_voters),
                    norm.rvs(loc=mean, scale=sigma, size=num_voters))))
            shuffle(voters_list[-1])
        return candidates_list, voters_list

    def two_overlapping_circles(self, num_candidates, num_voters, r1=2, o1=(-1, 0), r2=2, o2=(1, 0)):
        candidates_list, voters_list = [], []

        for i_samples in range(self.num_sampling):
            flip = np.random.choice([0, 1])
            r = r1 * np.sqrt(uniform.rvs(size=(num_candidates + flip) // 2))
            theta = np.array(uniform.rvs(size=(num_candidates + flip) // 2)) * 2 * pi

            x_candidates = o1[0] + (r * np.cos(theta))
            y_candidates = o1[1] + (r * np.sin(theta))

            candidates_list.append(list(zip(x_candidates, y_candidates)))

            r = r1 * np.sqrt(uniform.rvs(size=(num_voters + flip) // 2))
            theta = np.array(uniform.rvs(size=(num_voters + flip) // 2)) * 2 * pi

            x_candidates = o1[0] + (r * np.cos(theta))
            y_candidates = o1[1] + (r * np.sin(theta))

            voters_list.append(list(zip(x_candidates, y_candidates)))

            r = r2 * np.sqrt(uniform.rvs(size=(num_candidates + 1 -flip) // 2))
            theta = np.array(uniform.rvs(size=(num_candidates + 1 -flip)// 2)) * 2 * pi

            x_voters = o2[0] + (r * np.cos(theta))
            y_voters = o2[1] + (r * np.sin(theta))

            candidates_list[i_samples].extend(list(zip(x_voters, y_voters)))
            # shuffle(candidates_list[i_samples])

            r = r2 * np.sqrt(uniform.rvs(size=(num_voters+ 1 -flip) // 2))
            theta = np.array(uniform.rvs(size=(num_voters+ 1 -flip) // 2)) * 2 * pi

            x_voters = o2[0] + (r * np.cos(theta))
            y_voters = o2[1] + (r * np.sin(theta))

            voters_list[i_samples].extend(list(zip(x_voters, y_voters)))
            # shuffle(voters_list[i_samples])
        return candidates_list, voters_list


def data_to_voting(voting_algorithm, data, size_of_committee, data_name, *rule_args):
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
    times = []
    for i_sample, voting in enumerate(votings):
        # if i_sample % 10 == 0:
        #     print(i_sample)
        start_time = time()
        voting_results = voting_algorithm(voting, size_of_committee, *rule_args)
        end_time = time()
        computation_time = end_time-start_time
        times.append(computation_time)
        result.append([mapping[(i_sample, x)] for x in voting_results])

    benchmark_times = {"num_sampling": len(votings), "mean_time":np.mean(times), "std_time": np.std(times)}
    with open(f"../votepy/rules_distributions/times_of_{voting_algorithm.__name__}_on_{data_name}", "w") as fp:
        json.dump(benchmark_times, fp)
    return np.array(result)


class Visualizator:
    def __init__(self, votings_results, data):
        self.votings_results = votings_results
        self.data = data

    def visualize_results(self, save_to_file=False, name="None", title=""):
        xs_winners, ys_winners = [], []
        # xs_voters, ys_voters = [], []
        # xs_candidates, ys_candidates = [], []

        voters, candidates = self.data

        def alpha_parameter(k=0.7):
            size = np.product(np.array(voters).shape) + np.product(np.array(candidates).shape) + np.product(
                self.votings_results.shape)
            return k / min(1.4, np.log10(size) + 0.1)

        fig = plt.figure(figsize=(8, 8), dpi=80)


        # for x in voters:
        #     for q in x:
        #         xs_voters.append(q[0])
        #         ys_voters.append(q[1])
        # plt.scatter(xs_voters, ys_voters, color=(0.9, 0.9, 0.9), s=3, alpha=alpha_parameter() / 10, zorder=0)
        #
        # for x in candidates:
        #     for q in x:
        #         xs_candidates.append(q[0])
        #         ys_candidates.append(q[1])
        # plt.scatter(xs_candidates, ys_candidates, color=(0.85, 0.85, 0.85), s=3, alpha=alpha_parameter() / 10, zorder=0)

        for voting_result in self.votings_results:
            for p in voting_result:
                xs_winners.append(p[0])
                ys_winners.append(p[1])
        plt.scatter(xs_winners, ys_winners, color=(0.25, 0.25, 0.25), s=5, alpha=0.08, zorder=1)
        min_x, max_x = min(xs_winners), max(xs_winners)
        min_y, max_y = min(ys_winners), max(ys_winners)

        xs_winners.sort()
        xs_winners.sort()

        deviation_min_xs = np.mean(xs_winners[:(len(xs_winners) // 100)])
        deviation_min_ys = np.mean(xs_winners[:(len(xs_winners) // 100)])


        deviation_max_xs = np.mean(xs_winners[(-len(xs_winners) // 100):])
        deviation_max_ys = np.mean(xs_winners[(-len(xs_winners) // 100):])

        final_xs_deviation = max(abs(-deviation_min_xs), abs(deviation_max_xs))
        final_ys_deviation = max(abs(-deviation_min_ys), abs(deviation_max_ys))


        plt.xlim([min_x - 0.05*(final_xs_deviation), max_x + 0.05*(final_xs_deviation)])
        plt.ylim([min_y - 0.05*(final_ys_deviation), max_y + 0.05*(final_ys_deviation)])
        # plt.legend(["Voters", "Not chosen candidates", "chosen candidates"], framealpha=1, loc=(0, -0.3))
        plt.tick_params(
            axis='both',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            left=False,
            right=False,
            labeltop=False,
            labelright=False,
            labelleft=False,
            labelbottom=False)  # labels along the bottom edge are off
        plt.title(title)
        fig.tight_layout()

        if not save_to_file:
            plt.show()
        else:
            plt.savefig(name)
            plt.clf()
            plt.cla()
            plt.close()

    def visualize_all(self, save_to_file=False, name="None", title=""):
        xs_winners, ys_winners = [], []
        xs_voters, ys_voters = [], []
        xs_candidates, ys_candidates = [], []

        voters, candidates = self.data

        def alpha_parameter(k=0.7):
            size = np.product(np.array(voters).shape) + np.product(np.array(candidates).shape) + np.product(
                self.votings_results.shape)
            return k / min(1.4, np.log10(size) + 0.1)

        fig = plt.figure(figsize=(8, 8), dpi=80)

        for x in voters:
            for q in x:
                xs_voters.append(q[0])
                ys_voters.append(q[1])
        plt.scatter(xs_voters, ys_voters, color=(0.9, 0.9, 0.9), s=3, alpha=alpha_parameter() / 10, zorder=0)

        for x in candidates:
            for q in x:
                xs_candidates.append(q[0])
                ys_candidates.append(q[1])
        plt.scatter(xs_candidates, ys_candidates, color=(0.85, 0.85, 0.85), s=3, alpha=alpha_parameter() / 10, zorder=0)

        # for voting_result in self.votings_results:
        #     for p in voting_result:
        #         xs_winners.append(p[0])
        #         ys_winners.append(p[1])
        # plt.scatter(xs_winners, ys_winners, color=(0.25, 0.25, 0.25), s=3, alpha=0.08, zorder=1)
        plt.legend(["Voters", "candidates"], framealpha=1, loc=(0, -0.3))
        plt.title(title)
        fig.tight_layout()

        if not save_to_file:
            plt.show()
        else:
            plt.savefig(name)
            plt.clf()
            plt.cla()
            plt.close()

    def results_to_distribution_plot(self, save_to_file=False, name="None", title=""):
        split = 120
        color_intensity = [[0 for _ in range(split)] for _ in range(split)]
        num_of_samples = len(self.votings_results) * len(self.votings_results[0])
        for voting_result in self.votings_results:
            for p in voting_result:
                x = min(math.floor((p[0] + 3) / 6 * split), split-1)
                y = min(math.floor((p[1] + 3) / 6 * split), split-1)
                color_intensity[x][y] += 1


        fig = plt.figure(figsize=(8, 8), dpi=80)
        plt.title(title)
        fig.tight_layout()
        eps = 0.0002

        print(num_of_samples)
        print(np.max(color_intensity))
        print(np.max(color_intensity)/(num_of_samples*eps))
        print(np.argmax(color_intensity))

        for i in range(split):
            for j in range(split):
                color_intensity[i][j] = color_intensity[i][j] * np.arctan(color_intensity[i][j]/(eps * num_of_samples))

        plt.imshow(color_intensity, cmap="gray", interpolation='bicubic')
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
    vis.visualize_all()
