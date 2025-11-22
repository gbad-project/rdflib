import pytest
from rdflib import ConjunctiveGraph, URIRef
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

def test_original_serializer_correct_behavior():
    """
    This test confirms that the rdflib serializer correctly prefers a
    prefixed name over a relative URI when both are possible.
    """
    g = ConjunctiveGraph()
    # Bind the empty prefix to a namespace
    g.bind("", "http://example.com/term1/term2/")

    # Add a triple with a URI that is inside the bound namespace
    g.add((
        URIRef("http://example.com/term1/term2/subject"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/term1/term2/Object")
    ))

    # Use a base for serialization that is a parent of the resource URI,
    # making a relative URI representation possible.
    base = "http://example.com/"

    # Serialize
    serialized_turtle = g.serialize(format="turtle", base=base)

    # The correct output is that the serializer uses the bound empty prefix.
    assert ":subject" in serialized_turtle
    assert "<term1/term2/subject>" not in serialized_turtle
