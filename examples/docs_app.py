from flask import Flask, jsonify
from flask_ogm import OGM
from flask_ogm.param_converter import ParamConverter
from tests.fixtures import Widget

app = Flask('Flask-OGM Documentation App')
app.config.update(
    OGM_GRAPH_HOST='localhost',
    OGM_GRAPH_USER='neo4j',
    OGM_GRAPH_PASSWORD='password'
)
ogm = OGM(app)


@app.route('/widget_by_id/<int:widget>')  # IDs are integers
@ParamConverter(graph_object=Widget, param='widget')
def get_widget_by_id(widget):
    """Pull node using Widget.__primarykey__, in our case
    `Widget.unique_id`"""
    return jsonify({'widget': widget.as_dict()})


@app.route('/widget_by_name/<widget>')  # names are strings
@ParamConverter(graph_object=Widget, param='widget', select_on='name')
def get_widget_by_name(widget):
    """Select a widget by name, using default controller and custom
    attr."""
    return jsonify({'widget': widget.as_dict()})


def get_widget_by_composite_id(graph, composite_id):
    """Example constructor method, if for some reason you needed to
    perform an operation on the input before searching for the node in
    the database.
    """
    # composite id takes form widget:1
    unique_id = int(composite_id.split(':')[-1])
    return Widget.select(graph, unique_id)


@app.route('/widget_by_composite_id/<widget>')
@ParamConverter(param='widget',
                constructor=get_widget_by_composite_id)
def get_widget_by_id2(widget):
    """Specify graph_object.constructor using import strings"""
    return jsonify({'widget': widget.as_dict()})


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


def custom_not_found_callable():
    return 'Whoops! Widget not found!'


@app.route('/widget_by_id4/<int:widget>')
@ParamConverter(graph_object=Widget,
                param='widget',
                on_not_found=custom_not_found_callable)
def not_found_specify_custom_callable(widget):
    return jsonify({'widget': widget.as_dict()})


@app.route('/widget_by_id5/<int:widget>')
@ParamConverter(graph_object=Widget,
                param='widget',
                on_not_found='Sorry, no widget found!')
def not_found_specify_string(widget):
    return jsonify({'widget': widget.as_dict()})


@app.route('/widget_by_id6/<int:widget>')
@ParamConverter(graph_object=Widget,
                param='widget',
                on_not_found=418)
def not_found_specify_http_status(widget):
    """On not found: HTTP 418 I'M A TEAPOT"""
    return jsonify({'widget': widget.as_dict()})


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
