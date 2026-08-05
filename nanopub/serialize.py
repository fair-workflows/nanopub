"""Serialization of nanopublications with their graphs in conventional order.

rdflib's TriG serializer emits named graphs in store-iteration order, which is
arbitrary and differs between an unsigned and a signed nanopub. Nanopublications
are conventionally written as Head, assertion, provenance, pubinfo; this module
restores that order.

The order is resolved from the Head graph (``np:hasAssertion``,
``np:hasProvenance``, ``np:hasPublicationInfo``) rather than by sorting graph
URIs: a plain sort matches the convention only by accident of capitalisation and
breaks for differently named graphs.

The serializer is registered with rdflib under the ``nanopub-trig`` format, so it
also works on a bare Dataset::

    dataset.serialize(format="nanopub-trig")
"""
import logging
from typing import Any, IO, List, Optional, Sequence

from rdflib import Dataset, URIRef, plugin
from rdflib.graph import Graph
from rdflib.plugins.serializers.trig import TrigSerializer
from rdflib.serializer import Serializer

from nanopub.utils import MalformedNanopubError, NanopubMetadata, extract_np_metadata

logger = logging.getLogger(__name__)

#: Name this serializer is registered under with rdflib.
NANOPUB_TRIG_FORMAT = "nanopub-trig"


def nanopub_graph_order(metadata: NanopubMetadata) -> List[URIRef]:
    """The conventional graph order of a nanopub: Head, assertion, provenance, pubinfo."""
    return [metadata.head, metadata.assertion, metadata.provenance, metadata.pubinfo]


def _resolve_graph_order(store: Any) -> List[URIRef]:
    """Derive the conventional graph order from the Head graph of ``store``.

    Returns an empty order (i.e. leave the graphs alone) for anything that is not
    a single well-formed nanopub, so that serializing never fails on RDF the
    ordering simply does not apply to.
    """
    if not getattr(store, "context_aware", False):
        return []
    try:
        return nanopub_graph_order(extract_np_metadata(store))
    except MalformedNanopubError:
        logger.debug("No single nanopub found; serializing graphs in store order")
    except Exception:
        # Ordering is cosmetic: never let it stop the RDF from being written out.
        logger.warning("Could not determine the nanopub graph order", exc_info=True)
    return []


def _ordered_contexts(contexts: Sequence[Graph], order: Sequence[URIRef]) -> List[Graph]:
    """Sort ``contexts`` to follow ``order``, keeping any others at the end.

    Graphs the Head does not mention (and the default graph) keep their original
    relative order after the named ones, so nothing is ever dropped or hidden.
    """
    remaining = list(contexts)
    ordered = []
    for identifier in order:
        for i, context in enumerate(remaining):
            if context.identifier == identifier:
                ordered.append(remaining.pop(i))
                break
    ordered.extend(remaining)
    return ordered


class NanopubTrigSerializer(TrigSerializer):
    """TriG serializer emitting Head, assertion, provenance and pubinfo in that order.

    Pass ``graph_order`` to ``serialize()`` to supply the order directly; without
    it the order is resolved from the Head graph.
    """

    def __init__(self, store: Graph) -> None:
        super().__init__(store)
        # ``preprocess()`` reassigns ``self.store`` to each context in turn, so keep
        # our own handle on the dataset to resolve the order from.
        self._nanopub_store = store

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        spacious: Optional[bool] = None,
        graph_order: Optional[Sequence[URIRef]] = None,
        **kwargs: Any,
    ) -> None:
        if graph_order is None:
            graph_order = _resolve_graph_order(self._nanopub_store)
        self.contexts = _ordered_contexts(self.contexts, graph_order)
        super().serialize(stream, base=base, encoding=encoding, spacious=spacious, **kwargs)


def serialize_nanopub_trig(
    rdf: Dataset,
    destination: Any = None,
    metadata: Optional[NanopubMetadata] = None,
    **kwargs: Any,
) -> Any:
    """Serialize ``rdf`` to TriG with the graphs in conventional order.

    Pass ``metadata`` when it is already known, to save re-reading the Head graph.
    """
    if metadata is not None:
        kwargs.setdefault("graph_order", nanopub_graph_order(metadata))
    return rdf.serialize(destination, format=NANOPUB_TRIG_FORMAT, **kwargs)


plugin.register(NANOPUB_TRIG_FORMAT, Serializer, "nanopub.serialize", "NanopubTrigSerializer")
