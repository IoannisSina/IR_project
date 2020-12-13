import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
import csv
from ast import literal_eval
import os


def create_graph(filepath, figures_dir):

    counter_zeros = 0
    B = nx.DiGraph()

    with open(filepath) as csv_file:
        csv_reader = csv.DictReader(csv_file)

        line_count = 0
        for row in csv_reader:
            line_count += 1
            if line_count > 0:
                if row['singer_ids'] in ['[]','0'] or row['songwriter_ids'] in ['[]','0']:
                    counter_zeros += 1
                    continue

                singers_list = literal_eval(row['singer_ids'])
                songwriters_list = literal_eval(row['songwriter_ids'])

                # Nodes
                for singer_id in singers_list:
                    if not B.has_node(str(singer_id) + '-Si'):
                        B.add_node((str(singer_id) + '-Si'), bipartite=0)

                for songwriter_id in songwriters_list:
                    if not B.has_node((str(songwriter_id) + '-So')):
                        B.add_node((str(songwriter_id) + '-So'), bipartite=1)

                # Edges
                for singer_id in singers_list:
                    singer_node = str(singer_id) + '-Si'

                    for songwriter_id in songwriters_list:
                        songwriter_node = str(songwriter_id) + '-So'

                        if B.has_edge(singer_node, songwriter_node):
                            B[singer_node][songwriter_node]['weight'] += 1
                        else:
                            B.add_edge(singer_node, songwriter_node, weight = 1)

    try:
        h,a = nx.hits(B)
        print(filepath)
        print(sorted(h.items(), key=lambda x:x[1], reverse=True)[:50])
        print(sorted(a.items(), key=lambda x:x[1], reverse=True)[:50])
    except Exception as e:
        print(filepath)
        print(e)
    print('------')


    color_map = []
    one_side_nodes = []

    for node in B:
        strnode = str(node)
        if strnode.endswith("Si"):
            color_map.append('red')
            one_side_nodes.append(node)
        else:
            color_map.append('gray')


    max_weight = -1
    for (node1,node2,data) in B.edges(data=True):
        max_weight = max(max_weight, data['weight'])

    width_multiplier = 1/max_weight
    weights = [B[u][v]["weight"]*width_multiplier for u, v in B.edges() if u != v]
    nx.draw(B, width=weights, node_color=color_map, pos=nx.bipartite_layout(B, one_side_nodes), node_size=10) # with_labels = True
    plt.savefig(figures_dir + filepath.replace('songs/', '').replace('.csv', '') + '.png')
    plt.clf()

    # print(counter_zeros)
    # print(line_count)
    # print(nx.is_directed(B))
    # print(nx.density(B))
    # print(nx.info(B))


if __name__ == '__main__':

    results_dir = 'songs/'
    figures_dir = 'figures/'

    # create_graph('songs/Pop.csv', figures_dir)

    for file in os.listdir(results_dir):
        filepath = os.path.join(results_dir, file)
        create_graph(filepath, figures_dir)
