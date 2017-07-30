from py2neo.ogm import GraphObject, Property

class Widget(GraphObject):
    unique_id = Property()
    name = Property()

    @classmethod
    def custom_constructor(cls, graph, property):
        return list(graph.run(
            'MATCH (n:Widget:Fixture) WHERE n.name = {name} RETURN n',
            { name: proprty }
            ).data())
