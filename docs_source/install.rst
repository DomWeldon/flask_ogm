Installation
============

`flas_ogm` can be downloaded from PyPI and installed using `pip`.

::

  $ pip install flask_ogm


Quick Start
-----------

You can now create an application and access your graph using the ``ogm.graph`` interface. You must specify the connection credentials in your application's configuration, port and protocol are optional, but host, user and password are required. You can also use the `ParamConverter` to pull objects out of your database, as seen in the example below.

::

  from flask import Flask
  from flask_ogm import OGM
  # optionally import ParamConverter to pull objercts out of the graph
  from flask_ogm.param_converter import ParamConverter
  from py2neo.ogm import GraphObject, Property

  app = Flask('Flask-OGM Quick Start Test App')
  app.config.update(
    OGM_GRAPH_HOST='localhost',
    OGM_GRAPH_USER='neo4j',
    OGM_GRAPH_PASSWORD='password'
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


Copy the above into an application (changing the configuration as required), and navigate to http://localhost:5000/count to see the count of the number of nodes in your database.

To configure your connection(s) to your graph(s) with more precision, see :ref:`graph_connections`.

Registering Flask-OGM in your App
---------------------------------

You can register Flask-OGM in your app using either the standard method as shown in the Quick Start, or the factory method like below.

::

  >>>> from flask import Flask
  >>>> from flask_ogm import OGM
  >>>> app = Flask('Flask-OGM Factory Method Test App')
  >>>> ogm = OGM()
  >>>> ogm.init_app(app)
  >>>> app.config.update(
    OGM_GRAPH_HOST = 'localhost',
    OGM_GRAPH_USER = 'neo4j',
    OGM_GRAPH_PASSWORD = 'password'
  )
  >>>> with app.app_context():
          print(ogm.graph.run(
            'MATCH (n) RETURN COUNT(n) AS node_count'
          ).evaluate())

  1,234
