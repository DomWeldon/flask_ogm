Index of Errors
===============

A list of possible exceptions raised is provided below to aid with debugging problems.

Graph Credentials Errors
------------------------

The below errors relate to connecting to and using the database.

.. _default_graph_credentials_unclear_error:

``DefaultGraphCredentialsUnclearError``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Raised when you have specified your default graph credentials both as a bind, and as simple top level ``app.config`` values. Pick one or the other. See :ref:`graph_connections`


``GraphCredentialsIncompleteError``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Raised when some, but not all, of the required arguments (``HOST``, ``USER``, ``PASSWORD``) are provided for a bind (or the default bind), but not all. You should ensure all three of these values are provided.

When specifying the default bind using simple top-level configuration directives (see :ref:`specifying_default_simple`), the required parameters are ``OGM_GRAPH_HOST``, ``OGM_GRAPH_USER`` and ``OGM_GRAPH_PASSWORD``.


``GraphCredentialsNotFoundError``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Raised when the graph credentials for a bind (including the default bind) have not been found. You should ensure that the details are provided in ``app.config``, and that the binds are spelled correctly. See :ref:`graph_connections`.


``OutOfApplicationContextError``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Raised when ``ogm.get_connection()`` has been called, but no ``app_context`` is available. You should ensure that you call the function inside a valid application context.

When using web tools like the `ogm.param_converter` decorator, ensure that you pass references to the graph as binds not ``Graph`` objects. Likewise, when testing, ensure that you conduct graph operations within an application context.
