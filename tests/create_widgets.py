import os
from py2neo import Graph

if __name__ == '__main__':
    graph = Graph('bolt://neo4j:password@localhost:7687/db/data')
    directory = os.path.dirname(__file__)
    files = [
        '../queries/create_small_movies_graph.cql',
        '../queries/create_widgets.cql',
    ]
    for f in files:
        query_file = os.path.join(
            directory,
            f)
        with open(query_file, 'r') as _:
            q = _.read()
        graph.run(q).evaluate()
