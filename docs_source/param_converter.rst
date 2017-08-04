ParamConverter
==============

ParamConverter is a tool used to avoid having to repeat code to pull GraphObjects out of databases in response to user input.

It can be used as a `view decorator`_ to convert a parameter in the URL route, to the relevant `py2neo.ogm.Graph` object, or a list of such objects, which correspond to the value passed from the user in the URL. The best way to understand the behaviour of the decorator is to see an example such as that below.

.._`view decorator`: http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

The examples below use examples from the movies dataset which you can import into your graph either by running the contents of `queries/create_small_movies_graph.cql` which is available in the `flask_ogm` repository on GitHub, or which can be imported by running `:play movies` in the Neo4J browser.

Quick Start: Pull a Move Out of the Graph
-----------------------------------------
