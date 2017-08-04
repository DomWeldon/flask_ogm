"""
Flask-OGM
-------------

Add support for the py2neo library to access neo4j in your flask app.
"""
from setuptools import setup

__author__ = 'Dom Weldon <dom.weldon@gmail.com>'
__email__ = 'dom.weldon@gmail.com'
__license__ = 'Apache License, Version 2.0'
__package__ = 'flask_ogm'
__version__ = '1.1.0a5'

setup(
    name='flask_ogm',
    version=__version__,
    url='http://www.flask-ogm.org',
    license='Apache License, Version 2.0',
    author='Dom Weldon',
    author_email='dom.weldon@gmail.com',
    description='Add support for the py2neo Object Graph Mapper to your app',
    long_description=__doc__,
    py_modules=['flask_ogm'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'py2neo',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
    ],
    keywords='graph database py2neo web development neo4j flask',
    test_suite='py.test',
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    python_requires='>=2.7',
    download_url='https://github.com/domweldon/flask-ogm/archive/1.1.0.tar.gz'
)
