ParamConverter
==============

ParamConverter is a tool used to avoid having to repeat code to pull GraphObjects out of databases in response to user input.

It can be used as a `view decorator`_ to convert a parameter in the URL route, to the relevant `py2neo.ogm.Graph` object, or a list of such objects, which correspond to the value passed from the user in the URL. The best way to understand the behaviour of the decorator is to see an example such as that below.

.. _`view decorator`: http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

The examples below are taken from the testing suite, and all refer to `Widget` nodes, which have an integer ID (`Widget.unique_id`), a name (`Widget.name`) and a colour (`Widget.colour`). Whilst widget IDs and names are unique, colours are not.

The following boiler plate code is omitted from all examples.

::

  # setup the app, import relevant objects
  from flask import Flask
  from flask_ogm import OGM
  from flask_ogm.param_converter import ParamConverter
  from tests.fixtures import Widget

  app = Flask('Flask-OGM Quick Start Test App')
  app.config.update(
    OGM_GRAPH_HOST = 'localhost',
    OGM_GRAPH_USER = 'neo4j',
    OGM_GRAPH_PASSWORD = 'password'
  )
  ogm = OGM(app)


Arguments
---------

Param Converter takes the following arguments.

.. py:currentmodule:: flask_ogm.param_converter


.. automethod:: ParamConverter.__init__


Test

Quick Start: Pull Node from Graph using Primary Key
---------------------------------------------------

::

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
