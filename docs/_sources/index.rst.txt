.. Flask-OGM documentation master file, created by
   sphinx-quickstart on Sat Jul 29 20:37:57 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask-OGM: Documentation
========================

.. image:: https://travis-ci.org/DomWeldon/flask_ogm.svg?branch=master
  :target: https://travis-ci.org/DomWeldon/flask_ogm

.. image:: https://coveralls.io/repos/github/DomWeldon/flask_ogm/badge.svg?branch=master
  :target: https://coveralls.io/github/DomWeldon/flask_ogm?branch=master


Flask-OGM provides an interface between a flask application and the py2neo_ driver for the neo4j_ graph database. This allows you to use its OGM (Object Graph Model) interface, and to execute cypher queries using py2neo as a driver.

The ``ParamConverter`` tool also provides a quick and convenient method to pull nodes out of the graph and and making them available as OGM Graph Objects in views; the tool is fully customizable, but by default will return a 404 if no such node is found.

.. _py2neo: http://py2neo.org/v3/
.. _neo4j: https://neo4j.com/

Other features will be added shortly as time goes on to assist with developing Flask apps using py2neo.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   install
   graph
   param_converter
   config
   errors



Options
-------
* :ref:`search`
