from rdflib.plugins.parsers.notation3 import SinkParser, TurtleParser, N3Parser, join, RDFSink, BadSyntax, ADDED_HASH
from rdflib.graph import Graph, Dataset, ConjunctiveGraph
from rdflib.term import Identifier
from typing import Any, MutableSequence, Union
from rdflib.parser import create_input_source
from rdflib.exceptions import ParserError

class PatchedSinkParser(SinkParser):
    def uri_ref2(self, argstr: str, i: int, res: MutableSequence[Any]) -> int:
        """
        Patched version of uri_ref2 that treats empty prefixes as normal prefixes.
        """
        qn: list[Union[Identifier, tuple[str, str]]] = []
        j = self.qname(argstr, i, qn)
        if j >= 0:
            pfx, ln = qn[0]
            if pfx is None:
                assert 0, "not used?"
                ns = (self._baseURI or "") + ADDED_HASH
            else:
                try:
                    ns = self._bindings[pfx]
                except KeyError:
                    if pfx == "_":  # Magic prefix 2001/05/30, can be changed
                        res.append(self.anonymousNode(ln))
                        return j
                    # REMOVED: The special handling for empty prefixes, now it will raise an error for unbound empty prefix
                    self.BadSyntax(argstr, i, 'Prefix "%s:" not bound' % (pfx))
            symb = self._store.newSymbol(ns + ln)
            res.append(self._variables.get(symb, symb))
            return j

        # The rest of the method is the same as the original
        i = self.skipSpace(argstr, i)
        if i < 0:
            return -1

        if argstr[i] == "?":
            v: list[Any] = []
            j = self.variable(argstr, i, v)
            if j > 0:
                res.append(v[0])
                return j
            return -1

        elif argstr[i] == "<":
            st = i + 1
            i = argstr.find(">", st)
            if i >= 0:
                uref = argstr[st:i]
                if self._baseURI:
                    uref = join(self._baseURI, uref)
                else:
                    assert ":" in uref, "With no base URI, cannot deal with relative URIs"
                if argstr[i - 1] == "#" and not uref.endswith("#"):
                    uref += "#"
                symb = self._store.newSymbol(uref)
                res.append(self._variables.get(symb, symb))
                return i + 1
            self.BadSyntax(argstr, i, "unterminated URI reference")

        elif self.keywordsSet:
            v = []
            j = self.bareWord(argstr, i, v)
            if j < 0:
                return -1
            if v[0] in self.keywords:
                self.BadSyntax(argstr, i, 'Keyword "%s" not allowed here.' % v[0])
            res.append(self._store.newSymbol(self._bindings[""] + v[0]))
            return j
        else:
            return -1


class PatchedTurtleParser(TurtleParser):
    def __init__(self, **kwargs):
        super(PatchedTurtleParser, self).__init__()

    def parse(self, source, graph, **kwargs):
        sink = RDFSink(graph)
        baseURI = graph.absolutize(source.getPublicId() or source.getSystemId() or "")
        p = PatchedSinkParser(sink, baseURI=baseURI, turtle=True)
        stream = source.getCharacterStream()
        if not stream:
            stream = source.getByteStream()
        p.loadStream(stream)
        for prefix, namespace in p._bindings.items():
            graph.bind(prefix, namespace)


class PatchedN3Parser(N3Parser):
    def __init__(self, **kwargs):
        super(PatchedN3Parser, self).__init__()

    def parse(self, source, graph, **kwargs):
        ca = getattr(graph.store, "context_aware", False)
        fa = getattr(graph.store, "formula_aware", False)
        if not ca:
            raise ParserError("Cannot parse N3 into non-context-aware store.")
        elif not fa:
            raise ParserError("Cannot parse N3 into non-formula-aware store.")

        conj_graph = Dataset(store=graph.store)
        conj_graph.default_context = graph
        conj_graph.namespace_manager = graph.namespace_manager

        sink = RDFSink(conj_graph)
        baseURI = graph.absolutize(source.getPublicId() or source.getSystemId() or "")
        p = PatchedSinkParser(sink, baseURI=baseURI, turtle=False)
        stream = source.getCharacterStream()
        if not stream:
            stream = source.getByteStream()
        p.loadStream(stream)
        for prefix, namespace in p._bindings.items():
            graph.bind(prefix, namespace)


class PatchedGraph(ConjunctiveGraph):
    def __init__(self, **kwargs):
        super(PatchedGraph, self).__init__(**kwargs)

    def parse(self, source=None, publicID=None, format=None, location=None, file=None, data=None, **args):
        if format is None:
            if location is not None:
                format = self._format_from_filename(location)
            elif file is not None:
                format = self._format_from_filename(file.name)

        if format == 'turtle':
            parser = PatchedTurtleParser()
        elif format == 'n3':
            parser = PatchedN3Parser()
        else:
            return super(PatchedGraph, self).parse(source=source, publicID=publicID, format=format, location=location, file=file, data=data, **args)

        source = create_input_source(source=source, publicID=publicID, location=location, file=file, data=data)
        parser.parse(source, self, **args)
        return self

    def _format_from_filename(self, filename):
        if filename.endswith('.ttl'):
            return 'turtle'
        elif filename.endswith('.n3'):
            return 'n3'
        return None
