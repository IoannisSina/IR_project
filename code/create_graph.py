import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
import csv
from ast import literal_eval


B = nx.Graph()

with open('data/songs.csv') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        line_count += 1
        if line_count > 0:
            if row['singer_ids'] == '[]' or row['songwriter_ids'] == '[]':
                continue

            for singer_id in literal_eval(row['singer_ids']):
                if not B.has_node(str(singer_id) + '-Si'):
                    B.add_node((str(singer_id) + '-Si'), bipartite=0)

            for songwriter_id in literal_eval(row['songwriter_ids']):
                if not B.has_node((str(songwriter_id) + '-So')):
                    B.add_node((str(songwriter_id) + '-So'), bipartite=1)

            for singer_id in literal_eval(row['singer_ids']):
                singer_node = str(singer_id) + '-Si'

                for songwriter_id in literal_eval(row['songwriter_ids']):
                    songwriter_node = str(songwriter_id) + '-So'

                    if B.has_edge(singer_node, songwriter_node):
                        B[singer_node][songwriter_node]['weight'] += 100
                    else:
                        B.add_edge(singer_node, songwriter_node, weight = 1)


# top = nx.bipartite.sets(B)[0]
# pos=nx.planar_layout(B)

width_multiplier = .1
weights = [B[u][v]["weight"]*width_multiplier for u, v in B.edges() if u != v]
nx.draw(B, with_labels = True, width=weights)
plt.show()
