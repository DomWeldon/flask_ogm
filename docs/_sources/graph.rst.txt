.. _graph_connections:

Graph Connections
=================

Flask-OGM supports single or multiple connections to neo4j graph databases. There is a concept of a 'default' connection, which can always be referenced through ``ogm.graph``, and which is be used as the connection in web tools unless explicitly stated otherwise.

An address and authentication details - herein termed "Graph Credentials" - must be provided for every database: the host, user and password are required for every connection. The specified port and protocol are optional; by default, ``bolt`` on port ``7687`` is assumed when optional graph credentials are not passed.

Access to all graphs is provided by py2neo.database.Graph_ objects.

.. _py2neo.database.Graph: http://py2neo.org/v3/database.html#the-graph

The default database exists since, in most use cases, it is envisaged that applications will employ only one database. You can therefore set the graph credentials for the default connection as top-level configuration directives in ``app.config``, whilst connections to other databases must be specified in ``app.config['OGM_GRAPH_CREDENTIALS']`` as a dictionary of dictionaries.

Every reference to a graph has a name, which is referred to its ``bind``. In the ``OGM_GRAPH_CREDENTIALS`` dictionary, credentials for each connection should be specified as a dictionary, with its bing as they key (see :ref:`multiple_connections_binds`). The default connection's graph credentials can also be specified in this way, under the bind ``DEFAULT``. However, if default graph credentials are specified both as a bind and as individual top-level configuration directives, a  :ref:`default_graph_credentials_unclear_error` will be raised.

Since binds are dictionary keys, a bind can be any hashable value.


API
---

.. py:currentmodule:: flask_ogm


.. autoclass:: OGM
  :members:


Examples relating to the above are provided below.


Example Usage
-------------

.. _specifying_default_simple:


Single (Default) Connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to connect to a single graph is as below. Optional parameters are included with their default values.


::

  from flask import Flask
  from flask_ogm import OGM

  app = Flask('Flask OGM Single Connection Test App')

  app.config['OGM_GRAPH_HOST'] = 'localhost'
  app.config['OGM_GRAPH_USER'] = 'neo4j'
  app.config['OGM_GRAPH_PASSWORD'] = 'password'
  app.config['OGM_GRAPH_PROTOCOL'] = 'bolt' # optional
  app.config['OGM_GRAPH_PORT'] = '7687' # optional, can be string or int

  ogm = OGM(app)

  @app.route('/count')
  def count():
      """Get counts from both graphs."""
      q = 'MATCH (n) RETURN COUNT(n) AS node_count'
      return str(ogm.graph.run(q).evaluate())

.. _multiple_connections_binds:

Multiple Connections (binds)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On occasion, an application will need to use more than one database. These can be specified using binds like the example below.

::

    from flask import Flask, jsonify
    from flask_ogm import OGM

    app = Flask('Flask OGM Multiple Connection Test App')
    # set config using binds
    app.config['OGM_GRAPH_CREDENTIALS'] = {
        'LOCAL': {
          'HOST': 'localhost',
          'USER': 'neo4j',
          'PASSWORD': 'password',
          'PROTOCOL': 'bolt', # optional
          'PORT': '7687', # optional
        },
        'REMOTE': {
          'HOST': 'remote.example.com',
          'USER': 'remote_user',
          'PASSWORD': 'remote_password',
          'PROTOCOL': 'http', # non-default value
          'PORT': '7473', # non-default value
        },
    }
    # registr app
    ogm = OGM(app)

    @app.route('/counts')
    def counts():
        """Get counts from both graphs."""
        q = 'MATCH (n) RETURN COUNT(n) AS node_count'
        return jsonify({
            'remote': ogm.get_connection(bind = 'REMOTE').run(q).evaluate(),
            'local': ogm.get_connection(bind = 'LOCAL').run(q).evaluate(),
        })



Specifying the Default Connection as a Bind
+++++++++++++++++++++++++++++++++++++++++++

The default connection can also be set in this way, using the bind ``DEFAULT``, as in the example below.

::

    from flask import Flask, jsonify
    from flask_ogm import OGM

    app = Flask('Flask OGM Default as Bind Connection Test App')
    # set default config using bind
    app.config['OGM_GRAPH_CREDENTIALS'] = {
        'DEFAULT': {
          'HOST': 'localhost',
          'USER': 'neo4j',
          'PASSWORD': 'password',
          'PROTOCOL': 'bolt', # optional
          'PORT': '7687', # optional
        },
        'REMOTE': {
          'HOST': 'remote.example.com',
          'USER': 'remote_user',
          'PASSWORD': 'remote_password',
          'PROTOCOL': 'http', # non-default value
          'PORT': '7473', # non-default value
        },
    }
    # register app
    ogm = OGM(app)

    @app.route('/counts')
    def counts():
        """Get counts from both graphs."""
        q = 'MATCH (n) RETURN COUNT(n) AS node_count'
        return jsonify({
            'remote': ogm.get_connection(bind = 'REMOTE').run(q).evaluate(),
            'default': ogm.get_connection(bind = 'DEFAULT').run(q).evaluate(),
        })


If the default connection is specified in this way whilst any of the top-level default graph settings are provided, a ``DefaultGraphCredentialsUnclearError`` will be raised.

Accessing Graph Connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphs can be accessed using ``ogm.get_connection()``. If no bind is specified, the default bind is assumed.

For convenience, the property ``ogm.graph`` is provided to access the default graph, and it is envisaged that most use cases will use this property.
