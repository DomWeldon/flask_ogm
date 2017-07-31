"""
Flask-OGM Example
-----------------
Tiny app designed to demonstrate using the extension.
"""
from flask import Flask
from py2neo.ogm import GraphObject
try:
    from flask_ogm import OGM, ParamConverter  # typical import
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_ogm import OGM, ParamConverter


app = Flask('Flask-OGM Example App')

app.config.update(
    OGM_GRAPH_HOST = 'localhost',
    OGM_GRAPH_USER = 'neo4j',
    OGM_GRAPH_PASSWORD = 'password'
)

ogm = OGM(app)

@app.route('/')
def helloWorld():
    return str(ogm.graph.run('MATCH (n) RETURN COUNT(n) AS c').evaluate())

if __name__ == '__main__':
    app.run(debug=True)
