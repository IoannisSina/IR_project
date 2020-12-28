import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
import csv
from ast import literal_eval
import os
from scipy import stats
from sklearn.metrics import ndcg_score
import random


def create_graph(file):

    B = nx.DiGraph()

    with open('songs/{}'.format(file)) as csv_file:
        csv_reader = csv.DictReader(csv_file)

        line_count = 0
        for row in csv_reader:
            line_count += 1
            if line_count > 0:

                singers_list = [str(singer_id) + '-Si' for singer_id in literal_eval(row['singer_ids'])]
                songwriters_list = [str(songwriter_id) + '-So' for songwriter_id in literal_eval(row['songwriter_ids'])]
                pageviews = int(row['pageviews'])

                edge_weight = 1

                # Nodes
                for singer_id in singers_list:
                    if not B.has_node(singer_id):
                        B.add_node(singer_id, bipartite=0)

                for songwriter_id in songwriters_list:
                    if not B.has_node(songwriter_id):
                        B.add_node(songwriter_id, bipartite=1)

                # Edges singer - songwriter
                for singer_node in singers_list:
                    for songwriter_node in songwriters_list:
                        if not B.has_edge(singer_node, songwriter_node):
                            B.add_edge(singer_node, songwriter_node, weight = 0)
                        B[singer_node][songwriter_node]['weight'] += edge_weight

                # Edges singer - singer
                for singer_node1 in singers_list:
                    for singer_node2 in singers_list:
                        if not B.has_edge(singer_node1, singer_node2):
                            B.add_edge(singer_node1, singer_node2, weight = 0)
                        B[singer_node1][singer_node2]['weight'] += edge_weight
                        if not B.has_edge(singer_node2, singer_node1):
                            B.add_edge(singer_node2, singer_node1, weight = 0)
                        B[singer_node2][singer_node1]['weight'] += edge_weight

                # Edges songwriter - songwriter
                for songwriter_node1 in songwriters_list:
                    for songwriter_node2 in songwriters_list:
                        if not B.has_edge(songwriter_node1, songwriter_node2):
                            B.add_edge(songwriter_node1, songwriter_node2, weight = 0)
                        B[songwriter_node1][songwriter_node2]['weight'] += edge_weight
                        if not B.has_edge(songwriter_node2, songwriter_node1):
                            B.add_edge(songwriter_node2, songwriter_node1, weight = 0)
                        B[songwriter_node2][songwriter_node1]['weight'] += edge_weight

    try:
        songwriters_length = len([n for n, d in B.nodes(data=True) if d["bipartite"] == 1])

        pr = nx.pagerank(B)
        my_scores = [(int(k.replace('-So','')), v) for k,v in pr.items() if 'So' in k]

        # _, a = nx.hits(B)
        # my_ranking = {k.replace('-So',''):v for k,v in a.items() if 'So' in k}


        with open('features/{}'.format(file)) as f:
            csv_reader = csv.reader(f)
            next(csv_reader)
            ground_truth = {int(songwriter_id):float(feature) for songwriter_id, feature in csv_reader}


        true_scores = []

        for (songwriter_id, my_score) in sorted(my_scores, key=lambda tup: tup[1], reverse=True):
            true_score = ground_truth[songwriter_id]

            if true_score == 0 or my_score == 0:
                continue

            true_scores.append(true_score)

        final_songwriters_length = len(true_scores)


        my_score = ndcg_score(np.asarray([sorted(true_scores, reverse=True)]), np.asarray([true_scores]))
        random.shuffle(true_scores)
        random_score = ndcg_score(np.asarray([sorted(true_scores, reverse=True)]), np.asarray([true_scores]))

        # print(stats.spearmanr(true_scores, my_scores))
        # true_scores = sorted(true_scores, reverse=False)


        # -----------------------------------------------
        # -------------------HEURISTIC-------------------
        # -----------------------------------------------
        df = pd.read_csv('songs/{}'.format(file), index_col=0)

        df.songwriter_ids = df.songwriter_ids.apply(literal_eval)
        df = df[['songwriter_ids', 'popularity']].explode('songwriter_ids')
        df = df.groupby('songwriter_ids').mean()


        heuristic_scores = [tuple(x) for x in df.to_records(index=True)]
        true_scores = []

        for (songwriter_id, heuristic_score) in sorted(heuristic_scores, key=lambda tup: tup[1], reverse=True):
            true_score = ground_truth[songwriter_id]

            if true_score == 0 or heuristic_score == 0:
                continue

            true_scores.append(true_score)

        heuristic_score = ndcg_score(np.asarray([sorted(true_scores, reverse=True)]), np.asarray([true_scores]))

        return (file, my_score, random_score, heuristic_score, songwriters_length, final_songwriters_length, )


    except Exception as e:
        print('ERROR')
        print(e)
    print('------')


    # -----------------------------------------------
    # ---------------------GRAPH---------------------
    # -----------------------------------------------

    # color_map = []
    # one_side_nodes = []

    # for node in B:
    #     strnode = str(node)
    #     if strnode.endswith("Si"):
    #         color_map.append('red')
    #         one_side_nodes.append(node)
    #     else:
    #         color_map.append('gray')

    # max_weight = -1
    # for (node1,node2,data) in B.edges(data=True):
    #     max_weight = max(max_weight, data['weight'])

    # width_multiplier = 1/max_weight
    # weights = [B[u][v]["weight"]*width_multiplier for u, v in B.edges() if u != v]
    # nx.draw(B, width=weights, node_color=color_map, pos=nx.bipartite_layout(B, one_side_nodes), node_size=10) # with_labels = True
    # plt.savefig(figures_dir + filepath.replace('songs/', '').replace('.csv', '') + '.png')
    # plt.clf()


if __name__ == '__main__':

    results_dir = 'songs/'
    figures_dir = 'figures/'

    # create_graph('songs/Rock.csv', figures_dir)

    results = []

    for file in os.listdir(results_dir):
        res = create_graph(file)
        results.append(res)


    with open('results/ndcg-1-full.csv','w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['file', 'my_score', 'random_score', 'heuristic_score', 'songwriters_length', 'final_songwriters_length'])
        for row in results:
            csv_out.writerow(row)
