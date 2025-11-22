import pytest
from rdflib import ConjunctiveGraph, URIRef

# Turtle fixture with a base URI and an empty prefix with a trailing slash
turtle_fixture = """
@base <http://example.com/term1/term2> .
@prefix : <http://example.com/term1/term2/> .

:subject a :Object .
"""

def test_original_parser_correct_behavior():
    """
    This test confirms that the original parser correctly handles the empty prefix,
    by treating it as a normal prefix.
    """
    g = ConjunctiveGraph()
    g.parse(data=turtle_fixture, format="turtle")

    # Expected URI with the correct handling of the empty prefix
    expected_subject = URIRef("http://example.com/term1/term2/subject")
    expected_object = URIRef("http://example.com/term1/term2/Object")

    # Check if the subject is in the graph
    assert (expected_subject, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), expected_object) in g
