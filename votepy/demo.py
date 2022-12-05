from votepy.visualization import data_to_voting, Visualizator, Generator
from votepy.rules.k_borda import k_borda
from votepy.rules.bloc import bloc
from votepy.rules.sntv import sntv
from votepy.rules.greedy_monroe import greedy_monroe
from votepy.rules.owa import owa_hurwicz

if __name__ == "__main__":

    generator = Generator(num_sampling=1)
    data1 = generator.uniform_rectangle(50, 50)
    data2 = generator.normal(10, 10)
    data3 = generator.two_overlapping_circles(10, 10)

    for idx, (name, data) in enumerate(
            # [("Uniform Rectangle", data1), ("Normal Distribution", data2), ("Two Overlapping Circles", data3)]
        [("Uniform Rectangle", data1)]
    ):
        for algo in [owa_hurwicz]:
            # print("hehe")
            results = data_to_voting(algo, data, 3, name, 0.3)
            vis = Visualizator(results, data)
            # vis.results_to_distribution_plot(save_to_file=True,
            #                       name=f"../votepy/rules_distributions/data_{idx}_{algo.__name__}.png",
            #                       title=f"{name} using {algo.__name__}")
            vis.visualize_results(save_to_file=True,
                                  name=f"../votepy/rules_distributions/data_{idx}_{algo.__name__}.png",
                                  title=f"{name} using {algo.__name__}")
