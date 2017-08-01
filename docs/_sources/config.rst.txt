Configuration
=============

A list of all configuration values is provided below for reference.

Simple Default Graph Credentials
--------------------------------

Used to quickly and conveniently specify graph credentials for the default graph.

``OGM_GRAPH_HOST``
~~~~~~~~~~~~~~~~~~

The hostname or IP address of the default graph database to connect to.

``OGM_GRAPH_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~

The password for this user.


``OGM_GRAPH_PORT``
~~~~~~~~~~~~~~~~~~

*Optional*: defaults to ``7687``

Port number to connect to the host on. The value provided is converted to a string using ``str.format`` and so can be specified as either an integer or a string.

``OGM_GRAPH_PROTOCOL``
~~~~~~~~~~~~~~~~~~~~~~

*Optional*: defaults to ``bolt``

Other supported protocols are: ``http``.


``OGM_GRAPH_USER``
~~~~~~~~~~~~~~~~~~

Username to provide for authentication to the database.


Graph Credentials in Binds
--------------------------

``OGM_GRAPH_CREDENTIALS``
~~~~~~~~~~~~~~~~~~~~~~~~~

A dictionary of dictionaries containing the graph credentials of the different connections used. The dictionary should take the form below:

::

  app.config['OGM_GRAPH_CREDENTIALS'] = {
      'BIND_NAME': {
          'HOST': 'localhost',
          'USER': 'neo4j',
          'PASSWORD': 'password',
          'PORT': '7687', # optional
          'PROTOCOL': 'bolt', # optional
      },
      # ..
  }


The default graph connection's credentials can be specified in this way (so long as they are not also specified as simple top level parameters), but not accessed in this way if specified as simple credentials. See :ref:`graph_connections`
