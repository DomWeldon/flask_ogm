ParamConverter
==============

ParamConverter is a tool used to avoid having to repeat code to pull GraphObjects out of databases in response to user input.

It can be used as a `view decorator`_ to convert a parameter in the URL route, to the relevant `py2neo.ogm.Graph` object, or a list of such objects, which correspond to the value passed from the user in the URL. The best way to understand the behaviour of the decorator is to see an example such as that below.

.. _`view decorator`: http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

The examples below are taken from the testing suite, and all refer to `Widget` nodes, which have an integer ID (`Widget.unique_id`), a name (`Widget.name`) and a colour (`Widget.colour`). Whilst widget IDs and names are unique, colours are not.

The following boiler plate code is omitted from all examples.

Argument Reference
------------------

.. py:currentmodule:: flask_ogm.param_converter


.. automethod:: ParamConverter.__init__


Example Usage
-------------

Boilerplate Used in Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following boilerplate code (setting up the example app, connecting to the database, and importing `ParamConverter` and `Widget` model) should be assumed in all examples.

::

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


The Widget object is taken from the unit tests for the module.


Quick Start: Pull Node from Graph using Primary Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need only specify the name of your parameter and a callable to find it. By default, the `py2neo.ogm.GraphObject.select()` is used if only a GraphObject is specified. By default, if a node if not found, an HTTP `404 NOT FOUND` error will be raised.

::

  @app.route('/widget_by_id/<int:widget>')  # IDs are integers
  @ParamConverter(graph_object=Widget, param='widget')
  def get_widget_by_id(widget):
    """Pull node using Widget.__primarykey__, in our case
    `Widget.unique_id`"""
    return jsonify({'widget': widget.as_dict()})

Pull Node From Graph Using Specified Property
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify `select_on` to search on a given node property.

::

  @app.route('/widget_by_name/<widget>')  # names are strings
  @ParamConverter(graph_object=Widget, param='widget', select_on='name')
  def get_widget_by_name(widget):
    """Select a widget by name, using default controller and custom
    attr."""
    return jsonify({'widget': widget.as_dict()})


Specify Object Using Import Reference and/or Attribute Name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rather than importing the graph object, or a constructor, you can specify the graph object using an import reference, with an optional string to select by an attribute.

::

  @app.route('/widget_by_id2/<widget>')  # names are strings
  @ParamConverter(graph_object='tests.fixtures.Widget',
                param='widget',
                constructor='select')
  def get_widget_by_id2(widget):
    """Specify graph_object.constructor using import strings"""
    return jsonify({'widget': widget.as_dict()})


Use a Custom Constructor Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also create or specify custom constructor methods, which again can be passed either as callables, or strings containing import references.

::

  def get_widget_by_composite_id(graph, composite_id):
      """Example constructor method, if for some reason you needed to
      perform an operation on the input before searching for the node in
      the database.
      """
      # composite id takes form widget:1
      unique_id = int(composite_id.split(':')[-1])
      # constructors must return an iterable
      return Widget.select(graph, unique_id)


  @app.route('/widget_by_composite_id/<widget>')
  @ParamConverter(param='widget',
                  constructor=get_widget_by_composite_id)
  def get_widget_by_id2(widget):
    """Specify graph_object.constructor using import strings"""
    return jsonify({'widget': widget.as_dict()})


Not Found: Specify Callable
~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, `ParamConverter` will raise an HTTP `404 NOT FOUND` exception if the node is not found, but custom behaviours can be specified in a callable, or as a string or integer.

::

  def custom_not_found_callable():
      return 'Whoops! Widget not found!'


  @app.route('/widget_by_id4/<int:widget>')
  @ParamConverter(graph_object=Widget,
                  param='widget',
                  on_not_found=custom_not_found_callable)
  def not_found_specify_custom_callable(widget):
      return jsonify({'widget': widget.as_dict()})


Not Found: Specify String / Non-HTTP Status Code Integer Response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not found responses can also be plain strings. If an integer is passed which does not relate to an exception in the `werkzeug.exceptions` library (e.g. `-1` or `0`), then it will be cast to a string and returned as the response.

::

  @app.route('/widget_by_id5/<int:widget>')
  @ParamConverter(graph_object=Widget,
                  param='widget',
                  on_not_found='Sorry, no widget found!')
  def not_found_specify_string(widget):
      return jsonify({'widget': widget.as_dict()})


Not Found: Specify HTTP Status Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If an http status code is supplied as an integer, this response will be returned, so long as the status code is found within `werkzeug.exceptions`

::

  @app.route('/widget_by_id6/<int:widget>')
  @ParamConverter(graph_object=Widget,
                  param='widget',
                  on_not_found=418)
  def not_found_specify_http_status(widget):
      """On not found: HTTP 418 I'M A TEAPOT"""
      return jsonify({'widget': widget.as_dict()})



Returning More than One Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`ParamConverter` can also return a list of widgets, for example searching on a given property, in this case colour.

::

  @app.route('/widgets_by_colour/<widgets_by_colour>')
  @ParamConverter(graph_object=Widget,
                  param='widgets_by_colour',
                  select_on='colour',
                  single=False)
  def get_widgets_by_colour(widgets_by_colour):
      """Return a list of nodes"""
      return jsonify({
          'widgets': [w.as_dict() for w in widgets_by_colour]
      })


Checking Only One Node Is Returned
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to be confident that only one node was found, you can check this using the `check_unique` option. If more than one node is found when this option is set to `True`, then `on_more_than_one` will be called, if nothing is specified for `on_more_than_one`, then an HTTP `500 INTERNAL ERROR` will be returned. `on_more_than_one` takes the same form as `on_not_found`.

::

  @app.route('/only_widget_with_colour/<widget>')
  @ParamConverter(graph_object=Widget,
                  param='widget',
                  select_on='colour',
                  single=True,
                  check_unique=True)
  def get_widgets_by_colour_unique(widget):
      """Return a list of nodes"""
      return jsonify({
          'widget': widget.as_dict()
      })


Reinjecting Old Param
~~~~~~~~~~~~~~~~~~~~~

Often it is helpful to know the original value of `param`, since you may not be able to know it from the graph objects returned. In such instances you can specify a keyword argument for the search term to be reinjected as. Presently, this must be specified as a defailt in the route of the view, this will be changed in future versions.

::

  @app.route('/search_widgets_by_name/<searched_widgets>',
             defaults={'search_term': None})
  @ParamConverter(graph_object=Widget,
                  constructor='search_on_name',
                  param='searched_widgets',
                  single=False,
                  inject_old_kwarg_as='search_term')
  def search_widgets_by_name(searched_widgets=None, search_term=None):
      """Return both the search term and the widgets"""
      return jsonify({
          'search_term': search_term,
          'widgets': [w.as_dict() for w in searched_widgets]
      })
