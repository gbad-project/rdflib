import pytest
from rdflib import Graph, URIRef, ConjunctiveGraph
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from aicode.rdflib.plugins.parsers.patched_notation3 import PatchedGraph
from rdflib.plugins.parsers.notation3 import BadSyntax

# N3 fixture with an unbound empty prefix
n3_fixture = """
@base <http://example.com/term1/term2> .

:subject a :Object .
"""

def test_original_parser_issue():
    """
    This test confirms that the original N3 parser incorrectly resolves an unbound
    empty prefix by appending a hash to the base URI.
    """
    # N3 parser requires a ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=n3_fixture, format="n3", publicID="http://example.com/term1/term2")

    expected_subject = URIRef("http://example.com/term1/term2#subject")
    expected_object = URIRef("http://example.com/term1/term2#Object")

    assert (expected_subject, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), expected_object) in g

def test_patched_parser_fix():
    """
    This test confirms that the patched parser raises a BadSyntax error for an
    unbound empty prefix in N3 mode, which is the correct behavior.
    """
    g = PatchedGraph()
    with pytest.raises(BadSyntax):
        g.parse(data=n3_fixture, format="n3")
