import pytest
from rdflib import ConjunctiveGraph, URIRef
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from aicode.rdflib.plugins.serializers.patched_turtle import PatchedGraph

def test_original_serializer_issue():
    """
    This test confirms the serializer bug in rdflib 6.3.2.
    The serializer incorrectly prefers a relative URI over a prefixed name
    when the base URI is a parent of the resource URI.
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

    # Use the specific base for serialization that triggers the bug.
    base = "http://example.com/term1/term2"

    # Serialize
    serialized_turtle = g.serialize(format="turtle", base=base)

    # The incorrect output is that the serializer produces a relative URI (<subject>)
    # instead of using the bound empty prefix (:subject).
    assert "<subject>" in serialized_turtle
    assert ":subject" not in serialized_turtle


def test_patched_serializer_fix():
    """
    This test confirms that the patched serializer correctly prefers a
    prefixed name over a relative URI.
    """
    g = PatchedGraph()
    # Bind the empty prefix to a namespace
    g.bind("", "http://example.com/term1/term2/")

    # Add a triple with a URI that is inside the bound namespace
    g.add((
        URIRef("http://example.com/term1/term2/subject"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/term1/term2/Object")
    ))

    # Use the specific base for serialization that was thought to trigger the bug.
    base = "http://example.com/term1/term2"

    # Serialize
    serialized_turtle = g.serialize(base=base)

    # The correct output is that the serializer uses the bound empty prefix.
    assert ":subject" in serialized_turtle
    assert "<subject>" not in serialized_turtle
