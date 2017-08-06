"""Flask-OGM Example: Movie App
-------------------------------
Tiny app designed to demonstrate using the extension on the movies
dataset. To get the data for this app, run `:play movies` in the
neo4j browser then copy and paste then execute the query which appears.
"""
from flask import Flask, jsonify
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom

try:
    # typical import
    from flask_ogm import OGM
    from flask_ogm.param_converter import ParamConverter
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)
    from flask_ogm import OGM
    from flask_ogm.param_converter import ParamConverter


class ExampleGraphObject(GraphObject):
    """Adds a count method to the graph object
    """
    @classmethod
    def count_nodes(cls, graph):
        """Count total number of nodes using cypher query.
        """
        q = 'MATCH (n:{0}) RETURN COUNT(n) AS count'.format(
            cls.__primarylabel__
        )
        return graph.run(q).evaluate()


class Movie(ExampleGraphObject):
    """Taken from the py2neo docs."""
    __primarykey__ = "title"

    title = Property()
    tag_line = Property("tagline")
    released = Property()

    actors = RelatedFrom("Person", "ACTED_IN")
    directors = RelatedFrom("Person", "DIRECTED")
    producers = RelatedFrom("Person", "PRODUCED")

    def as_dict(self):
        return {
            'title': self.title,
            'tag_line': self.tag_line,
            'released': self.released,
        }


class Person(ExampleGraphObject):
    """Taken from the py2neo docs."""
    __primarykey__ = "name"

    name = Property()
    born = Property()

    acted_in = RelatedTo(Movie)
    directed = RelatedTo(Movie)
    produced = RelatedTo(Movie)

    def as_dict(self):
        return {
            'name': self.name,
            'born': self.born,
        }


# setup the test app
app = Flask(__name__)
app.config.update(
    OGM_GRAPH_HOST='localhost',
    OGM_GRAPH_USER='neo4j',
    OGM_GRAPH_PASSWORD='password'
)

# initialize our graph
ogm = OGM(app)


@app.route('/count/movies', defaults={'go': Movie})
@app.route('/count/people', defaults={'go': Person})
def count_objects(go):
    """Count the total number of nodes of this type"""
    return jsonify({
        'primary_label': go.__primarylabel__,
        'total': go.count_nodes(ogm.graph)
    })


@app.route('/movie/<movie>')
@ParamConverter(graph_object=Movie, param='movie', select_on='title')
def get_movie(movie):
    return jsonify({
        'movie': movie.as_dict(),
        'actors': [p.as_dict() for p in movie.actors],
        'producers': [p.as_dict() for p in movie.producers],
        'directors': [p.as_dict() for p in movie.directors],
    })


@app.route('/person/<person>')
@ParamConverter(graph_object=Person, param='person', select_on='name')
def get_person(person):
    return jsonify({
        'person': person.as_dict(),
        'directed': [m.as_dict() for m in person.directed],
        'produced': [m.as_dict() for m in person.produced],
        'acted_in': [m.as_dict() for m in person.acted_in],
    })


@app.route('/movies/by/year/<int:movies>')
@ParamConverter(graph_object=Movie, param='movies', select_on='released',
                single=False)
def get_films_in_year(movies):
    return jsonify([
        m.as_dict()
        for m in movies
    ])


if __name__ == '__main__':
    app.run(debug=True)
