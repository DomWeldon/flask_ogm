#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import py2neo
from flask import current_app

# import application context - safe vor pre v.09
try:
    from flask import _app_ctx_stack as stack
except ImportError:  # pragma: no cover
    from flask import _request_ctx_stack as stack

from flask_ogm.errors import DefaultGraphCredentialsUnclearError, \
                             GraphCredentialsIncompleteError, \
                             GraphCredentialsNotFoundError, \
                             OutOfApplicationContextError


class OGM(object):
    """Extension to add OGM and py2neo support.
    """

    DEFAULT_GRAPH_KEY = 'DEFAULT'
    GRAPH_CREDENTIALS_CONFIG_KEY = 'OGM_GRAPH_CREDENTIALS'
    # required arguments to connect to a db, arguments with a None default
    # value are required
    GRAPH_CREDENTIALS_ARGUMENTS = {
        'PORT': '7687',
        'PROTOCOL': 'bolt',
        'PASSWORD': None,
        'USER': None,
        'HOST': None,
    }
    DEFAULT_GRAPH_SIMPLE_CREDENTIALS_PREFIX = 'OGM_GRAPH'

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Provided to support creation using factory method."""
        pass

    def connect(self, bind):
        """Connect to db and create a graph object"""
        # py2neo allows > 1 graph connection
        graph_credentials = None
        config_key = self.GRAPH_CREDENTIALS_CONFIG_KEY
        if bind == self.DEFAULT_GRAPH_KEY:
            # The extension supports multiple connections to different graphs
            # however, there is a concept of the "default" graph, which for
            # most applications will be the only graph used.
            # The default graph can be specified either using five strings
            # each as seperate keys in in app.config, or as a dictionary,
            # in the 'DEFAULT' key in app.config['OGM_GRAPH_CREDENTIALS'],
            # but not both.

            # First, have any of the keys been set?
            prefix = self.DEFAULT_GRAPH_SIMPLE_CREDENTIALS_PREFIX
            simple_credentials = {
                k: current_app.config[prefix + '_' + k]
                for k in self.GRAPH_CREDENTIALS_ARGUMENTS.keys()
                if prefix + '_' + k in current_app.config
            }
            if len(simple_credentials) > 0:
                # yes
                graph_credentials = simple_credentials
                if config_key in current_app.config \
                   and 'DEFAULT' in current_app.config[config_key]:
                    # credentials have been specified here and elsewhere
                    raise DefaultGraphCredentialsUnclearError((
                        'The default graph credentials may be specified only '
                        'as single keys in app.config, or as the DEFAULT bind'
                        'in ap.config["OGM_GRAPH_CREDENTIALS"], but not both.'
                    ))

        if graph_credentials is None:
            try:
                # get the credentials provided they exist
                graph_credentials = current_app.config[config_key][bind]
            except KeyError:
                raise GraphCredentialsNotFoundError((
                    'No graph credentials were found for the graph: {0}'
                    ).format(bind))

        # inject optional params not included
        optional_credentials = {
            k: v
            for k, v in self.GRAPH_CREDENTIALS_ARGUMENTS.items()
            if v is not None
        }
        for k, v in optional_credentials.items():
            if k not in graph_credentials:
                graph_credentials[k] = v

        try:
            graph = py2neo.Graph('{0}://{1}:{2}@{3}:{4}/db/data'.format(
                *[graph_credentials[x] for x in [
                    'PROTOCOL',
                    'USER',
                    'PASSWORD',
                    'HOST',
                    'PORT'
                ]]
            ))
        except KeyError:
            # not enough arguments in the config
            raise GraphCredentialsIncompleteError((
                'At least one of the required configuration parameters'
                ' was not specificed for the graph: {0}').format(bind))

        return graph

    @property
    def graph(self):
        """Returns DEFAULT_GRAPH"""
        return self.get_connection(bind=self.DEFAULT_GRAPH_KEY)

    def get_connection(self, bind=None):
        """Return a py2neo.Graph object based on config settings"""
        # assume default if no bind specified
        if bind is None:
            bind = self.DEFAULT_GRAPH_KEY
        # credentials are bound to the application context
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'ogm_graphs'.format(bind)):
                ctx.ogm_graphs = {}
            if bind not in ctx.ogm_graphs:
                ctx.ogm_graphs[bind] = self.connect(bind=bind)

            return ctx.ogm_graphs[bind]

        raise OutOfApplicationContextError()
