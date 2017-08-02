import os
from py2neo import Graph

if __name__ == '__main__':
    graph = Graph('bolt://neo4j:password@localhost:7687/db/data')
    directory = os.path.dirname(__file__)
    query_file = os.path.join(directory, '../queries/create_small_movies_graph.cql')
    with open(query_file, 'r') as _:
        q = _.read()
    graph.run(q).evaluate()
