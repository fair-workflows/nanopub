import re

from rdflib import RDF, RDFS, Dataset, Graph, URIRef

from nanopub import Nanopub, NanopubConf, Profile
from nanopub.serialize import NANOPUB_TRIG_FORMAT
from tests.conftest import default_conf

ORCID_ID = "https://orcid.org/0000-0000-0000-0001"

CONVENTIONAL_ORDER = ["Head", "assertion", "provenance", "pubinfo"]

# Enough to build an unsigned nanopub; signing needs the keys in ``default_conf``.
# The generated times keep the provenance and pubinfo graphs non-empty, since rdflib
# leaves empty graphs out of its output entirely.
unsigned_conf = NanopubConf(
    profile=Profile(agent_id=ORCID_ID, name="Python Tests"),
    add_prov_generated_time=True,
    add_pubinfo_generated_time=True,
)

# Graph names picked so that an ASCII sort would give the *wrong* order: sorted
# alphabetically these are assertion, head, pubinfo, provenance.
CUSTOM_NAMES_TRIG = """
@prefix np: <http://www.nanopub.org/nschema#> .
@prefix ex: <http://example.org/np#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:pubinfo { <http://example.org/np#> <http://purl.org/dc/terms/created> "2026-01-01" . }

ex:provenance { ex:assertion <http://www.w3.org/ns/prov#wasDerivedFrom> <http://example.org/x> . }

ex:assertion { <http://example.org/thing> a rdfs:Class . }

ex:Head {
    <http://example.org/np#> a np:Nanopublication ;
        np:hasAssertion ex:assertion ;
        np:hasProvenance ex:provenance ;
        np:hasPublicationInfo ex:pubinfo .
}
"""


def _graph_order(trig: str) -> list:
    """The local names of the named graphs, in the order they appear in ``trig``."""
    return [
        # Graph names appear either as <full/uri> or as a prefix:localName,
        # depending on whether the nanopub is signed.
        re.split(r"[/#:]", name.strip("<>"))[-1]
        for name in re.findall(r"^(?:GRAPH\s+)?(\S+)\s*\{", trig, flags=re.M)
    ]


def _make_nanopub(conf=None) -> Nanopub:
    assertion = Graph()
    assertion.add((URIRef("https://example.org/thing"), RDF.type, RDFS.Class))
    return Nanopub(conf=conf or unsigned_conf, assertion=assertion)


def _make_custom_named_dataset() -> Dataset:
    ds = Dataset()
    ds.parse(data=CUSTOM_NAMES_TRIG, format="trig")
    return ds


class TestGraphOrder:
    """Graphs come out as Head, assertion, provenance, pubinfo."""

    def test_graphs_are_serialized_in_conventional_order(self):
        assert _graph_order(_make_nanopub().serialize()) == CONVENTIONAL_ORDER

    def test_str_uses_conventional_order(self):
        assert _graph_order(str(_make_nanopub())) == CONVENTIONAL_ORDER

    def test_signing_does_not_change_the_order(self):
        np = _make_nanopub(default_conf)
        before = _graph_order(np.serialize())
        np.sign()
        assert _graph_order(np.serialize()) == before

    def test_order_is_stable_across_repeated_serialization(self):
        np = _make_nanopub()
        assert np.serialize() == np.serialize()

    def test_order_comes_from_the_head_graph_not_from_sorting_names(self):
        """Graph names whose ASCII order contradicts the conventional one."""
        out = _make_custom_named_dataset().serialize(format=NANOPUB_TRIG_FORMAT)
        assert _graph_order(out) == CONVENTIONAL_ORDER

    def test_ordering_survives_a_trig_round_trip(self):
        """Parsing our output back and reserializing gives the same order again."""
        first = _make_nanopub().serialize()
        reparsed = Dataset()
        reparsed.parse(data=first, format="trig")
        assert _graph_order(reparsed.serialize(format=NANOPUB_TRIG_FORMAT)) == _graph_order(first)


class TestNothingIsLost:
    """Reordering must never drop, alter or hide any RDF."""

    def test_no_quads_are_lost_or_altered(self):
        np = _make_nanopub()
        ordered = Dataset()
        ordered.parse(data=np.serialize(), format="trig")
        plain = Dataset()
        plain.parse(data=np.rdf.serialize(format="trig"), format="trig")
        assert set(ordered.quads((None, None, None, None))) == set(
            plain.quads((None, None, None, None))
        )

    def test_graphs_outside_the_head_are_kept(self):
        """A graph the Head does not mention is still serialized, after the known ones."""
        ds = _make_custom_named_dataset()
        extra = ds.graph(URIRef("http://example.org/np#extra"))
        extra.add((URIRef("http://example.org/a"), RDF.type, RDFS.Class))

        order = _graph_order(ds.serialize(format=NANOPUB_TRIG_FORMAT))
        assert order == CONVENTIONAL_ORDER

    def test_non_nanopub_rdf_is_serialized_instead_of_raising(self):
        """The ordering does not apply, but serializing must still work."""
        ds = Dataset()
        ds.graph(URIRef("http://example.org/g")).add(
            (URIRef("http://example.org/a"), RDF.type, RDFS.Class)
        )
        # The graph name may come out as a full URI or abbreviated, depending on rdflib.
        assert _graph_order(ds.serialize(format=NANOPUB_TRIG_FORMAT)) == ["g"]

    def test_empty_graphs_are_left_out(self):
        """rdflib omits empty graphs; the remaining ones still come out in order."""
        bare_conf = NanopubConf(profile=Profile(agent_id=ORCID_ID, name="Python Tests"))
        assert _graph_order(_make_nanopub(bare_conf).serialize()) == ["Head", "assertion", "pubinfo"]


class TestSerializeApi:
    """The entry points that reach the ordered serializer."""

    def test_prefixes_are_declared_once_at_the_top(self):
        out = _make_nanopub().serialize()
        prefixes = re.findall(r"^@prefix\s+(\S+)", out, flags=re.M)
        assert len(prefixes) == len(set(prefixes))
        # No prefix declaration appears after the first graph block has opened.
        assert "@prefix" not in out[out.index("{"):]

    def test_store_writes_ordered_trig(self, tmp_path):
        filepath = tmp_path / "np.trig"
        _make_nanopub().store(filepath)
        assert _graph_order(filepath.read_text()) == CONVENTIONAL_ORDER

    def test_other_formats_still_work(self):
        out = _make_nanopub().serialize(format="nquads")
        assert "https://example.org/thing" in out
