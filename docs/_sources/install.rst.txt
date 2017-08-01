Installation
============

You can install Flask-OGM by adding it to your project and initializing it like a standard module off github.

::

  $ pip install -e git+git@github.com:DomWeldon/flask-ogm.git


Quick Start
-----------

You can now create an application and access your graph using the ``ogm.graph`` interface. You must specify the connection credentials in your application's configuration, port and protocol are optional, but host, user and password are required.

::

  from flask import Flask
  from flask_ogm import OGM

  app = Flask('Flask-OGM Quick Start Test App')
  app.config.update(
    OGM_GRAPH_HOST = 'localhost',
    OGM_GRAPH_USER = 'neo4j',
    OGM_GRAPH_PASSWORD = 'password'
  )
  ogm = OGM(app)

  @app.route('/count')
  def node_count():
      return str(graph.run(
        'MATCH (n) RETURN COUNT (n) AS node_count'
      ).evaluate())

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
