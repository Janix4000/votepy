from votepy.visualization import data_to_voting, Visualizator, Generator
from votepy.rules.k_borda_impl import k_borda
from votepy.rules.bloc_impl import bloc
from votepy.rules.sntv import sntv

if __name__ == "__main__":

    generator = Generator(num_sampling=1000)
    data1 = generator.uniform_rectangle(50, 50, a=3, b=3)
    data2 = generator.normal(50, 50)
    data3 = generator.two_overlapping_circles(50, 50)

    for idx, (name, data) in enumerate(
            [("Uniform Rectangle", data1), ("Normal Distribution", data2), ("Two Overlapping Circles", data3)]):
        for algo in [k_borda, bloc, sntv]:
            results = data_to_voting(algo, data, size_of_committee=10)
            vis = Visualizator(results, data)
            vis.visualize_results(save_to_file=True,
                                  name=f"../votepy/rules_distributions/data_{idx}_{algo.__name__}.png",
                                  title=f"{name} using {algo.__name__}")
