# Flask-OGM

[![Build Status](https://travis-ci.org/DomWeldon/flask-ogm.svg?branch=master)](https://travis-ci.org/DomWeldon/flask-ogm) [![Coverage Status](https://coveralls.io/repos/github/DomWeldon/flask-ogm/badge.svg?branch=master)](https://coveralls.io/github/DomWeldon/flask-ogm?branch=master)

Quickly and easily setup and use the [py2neo](http://py2neo.org/v3/http://py2neo.org/v3/) driver to access neo4j in your flask app, and start pulling objects out of the graph and into your views with `@ParamConverter`.

## Documentation

Full docs are available online at http://www.flask-ogm.org/.


## Getting Started

Setting up Flask-OGM takes only a minute.

### Installation


`flas_ogm` can be downloaded from PyPI and installed using `pip`.


    $ pip install flask_ogm


### Example Application

You can now create an application and access your graph using the `ogm.graph` interface. You must specify the connection credentials in your application's configuration, port and protocol are optional, but host, user and password are required. You can also use the `ParamConverter` to pull objects out of your database, as seen in the example below.

    from flask import Flask
    from flask_ogm import OGM
    # optionally import ParamConverter to pull objercts out of the graph
    from flask_ogm.param_converter import ParamConverter
    from py2neo.ogm import GraphObject, Property

    app = Flask('Flask-OGM Quick Start Test App')
    app.config.update(
      OGM_GRAPH_HOST = 'localhost',
      OGM_GRAPH_USER = 'neo4j',
      OGM_GRAPH_PASSWORD = 'password'
    )
    ogm = OGM(app)


    # simple example
    @app.route('/count')
    def node_count():
        """Example running a cypher query. Return node count."""
        return str(graph.run(
          'MATCH (n) RETURN COUNT (n) AS node_count'
        ).evaluate())


    # using ParamConverter
    # we need a model to pull out of the graph
    class Movie(GraphObject):
        title = Property()  # only one property shown in quick start


    @app.route('/movie/<movie>')
    @ParamConverter(graph_object=Movie, param='movie', search_on='title')
    def get_movie_by_title(movie)
        """Example using ParamConverter.
        Search for movie based on Title, if found, return movie title,
        if no movie found, ParamConverter will return a 404, and this
        code will not be executed.
        """
        return str(movie.title)  # simple as that

    if __name__ == '__main__':
        app.run(debug=True)

## Author

Package was created and is maintained by Dom Weldon (<dom.weldon@gmail.com>). Pull requests are welcome.
