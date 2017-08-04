"""
Flask-OGM
-------------

Add support for the py2neo library to access neo4j in your flask app.
"""
from setuptools import setup
from flask_ogm import __author__, \
                      __email__, \
                      __license__, \
                      __package__, \
                      __version__

setup(
    name='Flask-OGM',
    version='0.1.0a',
    url='http://www.flask-ogm.org',
    license='Apache License, Version 2.0',
    author='Dom Weldon',
    author_email='dom.weldon@gmail.com',
    description='Add support for the py2neo Object Graph Mapper to your app',
    long_description=__doc__,
    py_modules=['flask_ogm'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'py2neo',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='py.test',
    tests_require=['pytest'],
    setup_requires=['pytest-runner']
)
