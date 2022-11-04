from votepy.generic_ilp import Gurobi
from votepy.visualization import data_to_voting, Visualizator, Generator
from votepy.rules.k_borda import k_borda
from votepy.bloc import bloc
from votepy.sntv import sntv
from votepy.rules.chamberlin_courant import chamberlin_courant_ilp
from votepy.owa import owa_ilp
from votepy.rules.greedy_monroe import greedy_monroe

if __name__ == "__main__":

    generator = Generator(num_sampling=1000)
    data1 = generator.uniform_rectangle(50, 50, a=3, b=3)
    data2 = generator.normal(50, 50)
    data3 = generator.two_overlapping_circles(50, 50)

    for idx, (name, data) in enumerate(
            [("Uniform Rectangle", data1), ("Normal Distribution", data2), ("Two Overlapping Circles", data3)]):
        for algo in [k_borda, bloc, sntv, greedy_monroe, lambda a,b: chamberlin_courant_ilp(a,b,solver=Gurobi), lambda a,b: owa_ilp(a,b,[1.0/i for i in range(1,11)],solver=Gurobi)]:
            print(idx)
            results = data_to_voting(algo, data, size_of_committee=10)
            vis = Visualizator(results, data)
            vis.visualize_results(save_to_file=True,
                                  name=f"../votepy/rules_distributions/data_{idx}_{algo.__name__}.png",
                                  title=f"{name} using {algo.__name__}")
