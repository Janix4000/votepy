import math

import matplotlib.pyplot as plt
from scipy.stats import uniform, norm
import numpy as np
from numpy import pi
import json
from time import time
from random import shuffle
from ordinal_election import OrdinalElection
from sklearn import datasets

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
            shuffle(candidates_list[i_samples])

            r = r2 * np.sqrt(uniform.rvs(size=(num_voters+ 1 -flip) // 2))
            theta = np.array(uniform.rvs(size=(num_voters+ 1 -flip) // 2)) * 2 * pi

            x_voters = o2[0] + (r * np.cos(theta))
            y_voters = o2[1] + (r * np.sin(theta))

            voters_list[i_samples].extend(list(zip(x_voters, y_voters)))
            shuffle(voters_list[i_samples])
        return candidates_list, voters_list

    def two_half_moons(self, num_candidates, num_voters, noise = 0.15):
        candidates_list, voters_list = [], []
        for i_samples in range(self.num_sampling):
            x, _ = datasets.make_moons(n_samples=num_candidates+num_voters, noise=noise)
            x[:, 1] -= 0.25
            x[:, 1] *= 1.8
            x[:, 0] -= 0.5
            x[:, 0] *= 1.8

            voters_list.append([tuple(val) for val in x[:num_voters]])
            candidates_list.append([tuple(val) for val in x[num_voters:]])
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

    votings = [OrdinalElection(voting) for voting in votings]
    result = []
    times = []
    for i_sample, voting in enumerate(votings):
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

    def visualize_results(self, save_to_file=False, name="None", title="", figsize=(8, 8)):
        xs_winners, ys_winners = [], []

        fig = plt.figure(figsize=figsize, dpi=80)

        for voting_result in self.votings_results:
            for p in voting_result:
                xs_winners.append(p[0])
                ys_winners.append(p[1])
        plt.scatter(xs_winners, ys_winners, color=(0.25, 0.25, 0.25), s=5, alpha=0.02, zorder=1)

        plt.xlim([-3, 3])
        plt.ylim([-3, 3])

        plt.tick_params(
            axis='both',
            which='both',
            bottom=False,
            top=False,
            left=False,
            right=False,
            labeltop=False,
            labelright=False,
            labelleft=False,
            labelbottom=False)
        plt.title(title, fontsize = 24)
        fig.tight_layout()

        if not save_to_file:
            plt.show()
        else:
            plt.savefig(name)
            plt.clf()
            plt.cla()
            plt.close()

    def results_to_distribution_plot(self, save_to_file=False, name="", title=""):
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

def load_data_from_json(filename):
    with open(filename, "r") as fp:
        return json.load(fp)

def plot_data_from_jsons(filenames, save_to_file=True, name_to_save="", title=None):
    times = []
    names = []
    errors = []
    fun_name_to_repr_name= {"k_borda": "K-Borda", "greedy_monroe": "Greedy Monroe", "bloc": "Bloc", "sntv": "SNTV", "chamberlin_courant_p_algorithm" : "CC P-Algorithm", 'owa_harmonic': "OWA Harmonic", "owa_geometric_progression": "OWA Geometric Progression", "owa_arithmetic_progression": "OWA Arithmetic Progression"}
    for (filename, name) in filenames:
        data = load_data_from_json(filename)
        times.append(float(data["mean_time"]))
        errors.append(float(data["std_time"]))
        names.append(fun_name_to_repr_name[name])

    fig = plt.figure(figsize=(8, 8), dpi=80)
    plt.bar(names, times)
    plt.errorbar(names, times, yerr=errors, fmt="o", color = "red")
    plt.title(title, fontsize=24)
    plt.xlabel("Algorithm")
    plt.ylabel("Time [s]")
    fig.tight_layout()
    # plt.show()

    if not save_to_file:
        plt.show()
    else:
        plt.savefig(name_to_save)
        plt.clf()
        plt.cla()
        plt.close()

