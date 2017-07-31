"""
Flask-OGM Example: Movie App
----------------------------
Tiny app designed to demonstrate using the extension on the movies
dataset. To get the data for this app, run `:play movies` in the
neo4j browser then copy and paste then execute the query which appears.
"""
from flask import Flask
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom


try:
    from flask_ogm import OGM, ParamConverter  # typical import
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_ogm import OGM, ParamConverter

# taken from the py2neo docs
class Movie(GraphObject):
    __primarykey__ = "title"

    title = Property()
    tag_line = Property("tagline")
    released = Property()

    actors = RelatedFrom("Person", "ACTED_IN")
    directors = RelatedFrom("Person", "DIRECTED")
    producers = RelatedFrom("Person", "PRODUCED")

class Person(GraphObject):
    __primarykey__ = "name"

    name = Property()
    born = Property()

    acted_in = RelatedTo(Movie)
    directed = RelatedTo(Movie)
    produced = RelatedTo(Movie)



app = Flask('Flask-OGM Movie App')

app.config.update(
    OGM_GRAPH_HOST = 'localhost',
    OGM_GRAPH_USER = 'neo4j',
    OGM_GRAPH_PASSWORD = 'password'
)

ogm = OGM(app)

@app.route('/count')
def count_all_nodes():
    return str(ogm.graph.run('MATCH (n) RETURN COUNT(n) AS c').evaluate())

@app.route('/count/movies', defaults = { 'go': Movie })
@app.route('/count/people', defaults = { 'go': Person })
def count_movies(go):
    return str(len(list(go.select(ogm.graph))))

if __name__ == '__main__':
    app.run(debug=True)
