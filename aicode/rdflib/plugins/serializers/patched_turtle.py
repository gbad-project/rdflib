from rdflib.plugins.serializers.turtle import TurtleSerializer, SUBJECT, VERB
from rdflib.graph import ConjunctiveGraph
from rdflib.term import Literal, URIRef
from rdflib.namespace import RDF
from rdflib.plugin import register, Serializer

class PatchedTurtleSerializer(TurtleSerializer):

    def __init__(self, store):
        super(PatchedTurtleSerializer, self).__init__(store)
        self.VERB = VERB  # Make VERB attribute accessible
        self._GEN_QNAME_FOR_DT = False # Make _GEN_QNAME_FOR_DT attribute accessible


    def label(self, node, position):
        if node == RDF.nil:
            return "()"
        if position == self.VERB and node in self.keywords:
            return self.keywords[node]
        if isinstance(node, Literal):
            return node._literal_n3(
                use_plain=True,
                qname_callback=lambda dt: self.getQName(dt, self._GEN_QNAME_FOR_DT),
            )

        # Try to get a qname for the URI FIRST
        qname = self.getQName(node, position == self.VERB)
        if qname is not None:
            return qname

        # If no qname, THEN fall back to relativizing the URI
        if not isinstance(node, URIRef):
            return node.n3()

        node = self.relativize(node)
        return node.n3()


class PatchedGraph(ConjunctiveGraph):
    def __init__(self, **kwargs):
        super(PatchedGraph, self).__init__(**kwargs)

    def serialize(self, **kwargs):
        # Use the 'patched_turtle' format for serialization
        if 'format' not in kwargs:
            kwargs['format'] = 'patched_turtle'
        return super(PatchedGraph, self).serialize(**kwargs)

# Register the patched serializer with a unique name
register(
    "patched_turtle",
    Serializer,
    "aicode.rdflib.plugins.serializers.patched_turtle",
    "PatchedTurtleSerializer",
)
