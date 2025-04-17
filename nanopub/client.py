"""
This module includes a client for the nanopub server.
"""

import random
import warnings
from typing import List, Tuple, Union

import rdflib
import requests

from nanopub import namespaces
from nanopub.definitions import (
    DUMMY_NANOPUB_URI,
    NANOPUB_QUERY_URLS,
    NANOPUB_REGISTRY_URLS,
    TEST_NANOPUB_QUERY_URL,
    TEST_NANOPUB_REGISTRY_URL,
)
from nanopub.nanopub import Nanopub
from nanopub.nanopub_conf import NanopubConf
from nanopub.utils import log

DUMMY_NAMESPACE = rdflib.Namespace(DUMMY_NANOPUB_URI + "/")
NP_URI = DUMMY_NAMESPACE[""]


class NanopubClient:
    """
    Provides utility functions for searching published nanopublications.

    Args:
        use_test_server (bool): Toggle using the test nanopub server.
        use_server (str): Provide the URL of a nanopub server to use
    """

    def __init__(
        self,
        use_test_server=False,
        use_server=NANOPUB_REGISTRY_URLS[0],
    ):
        self.use_test_server = use_test_server
        if use_test_server:
            self.query_urls = [TEST_NANOPUB_QUERY_URL]
            self.use_server = TEST_NANOPUB_REGISTRY_URL
        else:
            self.query_urls = NANOPUB_QUERY_URLS
            self.use_server = use_server
            if use_server not in NANOPUB_REGISTRY_URLS:
                log.warn(f"{use_server} is not in our list of nanopub servers. {', '.join(NANOPUB_REGISTRY_URLS)}\nMake sure you are using an existing Nanopub server.")


    def find_nanopubs_with_text(
        self, text: str, pubkey: str = None, filter_retracted: bool = True
    ):
        """Text search.

        Search the nanopub servers for any nanopubs matching the
        given search text.

        Args:
            text (str): The text to search on
            pubkey (str): Public key that the matching nanopubs should be signed with
            filter_retracted (bool): Toggle filtering for publications that are
                retracted. Default is True, returning only publications that are not retracted.

        Yields:
            results (dict): dicts depicting matching nanopublications.
                Each dict holds: 'np': the nanopublication uri,
                'date': date of creation of the nanopublication,
                'description': A description of the nanopublication (if found in RDF).

        """
        if len(text) == 0:
            return []
        endpoint = "RAMJaSqIk4-qgCud7Kf-ltdE3i8DVP239uQv-BiTGvwUU/fulltext-search-on-labels-all"
        params = {"query": text}
        if pubkey:
            params["pubkey"] = pubkey
        if filter_retracted:
            endpoint = "RAWruhiSmyzgZhVRs8QY8YQPAgHzTfl7anxII1de-yaCs/fulltext-search-on-labels"
        return self._search(endpoint=endpoint, params=params)


    def find_nanopubs_with_pattern(
        self,
        subj: str = None,
        pred: str = None,
        obj: str = None,
        filter_retracted: bool = True,
        pubkey: str = None,
    ):
        """Pattern search.

        Search the nanopub servers for any nanopubs matching the given RDF pattern. You can leave
        parts of the triple to match anything by not specifying subj, pred, or obj arguments.

        Args:
            subj (str): URI of the subject that you want to match triples on.
            pred (str): URI of the predicate that you want to match triples on.
            obj (str): URI of the object that you want to match triples on.
            pubkey (str): Public key that the matching nanopubs should be signed with
            filter_retracted (bool): Toggle filtering for publications that are
                retracted. Default is True, returning only publications that are not retracted.

        Yields:
            results (dict): dicts depicting matching nanopublications.
                Each dict holds: 'np': the nanopublication uri,
                'date': date of creation of the nanopublication,
                'description': A description of the nanopublication (if found in RDF).

        """
        params = {}
        endpoint = "RAuE9jU8LLwco-iJHiNjzQgEHfx5j-XkbzlutT59cQYiU/find_nanopubs_with_pattern"
        if subj:
            params["subj"] = subj
        if pred:
            params["pred"] = pred
        if obj:
            params["obj"] = obj
        if pubkey:
            params["pubkey"] = pubkey
        if filter_retracted:
            endpoint = "RAIDPTdWRrYy-TOcdEVmGi7JHwn8fBriVphmsCy3mn4r0/find_valid_nanopubs_with_pattern"

        yield from self._search(endpoint=endpoint, params=params)


    def find_things(
        self,
        type: str,
        searchterm: str = "*:*",
        pubkey: str = None,
        filter_retracted: bool = True,
    ):
        """Search things (experimental).

        Search for any nanopublications that introduce a concept of the given type, that contain
        text with the given search term.

        Args:
            type (str): A URI denoting the type of the introduced concept
            searchterm (str): The term that you want to search on
            pubkey (str): Public key that the matching nanopubs should be signed with
            filter_retracted (bool): Toggle filtering for publications that are
                retracted. Default is True, returning only publications that are not retracted.

        Yields:
            results (dict): dicts depicting matching nanopublications.
                Each dict holds: 'np': the nanopublication uri,
                'date': date of creation of the nanopublication,
                'description': A description of the nanopublication (if found in RDF).

        """
        if searchterm == "":
            raise ValueError(f"Searchterm can not be an empty string: {searchterm}")
        endpoint = "RA99xFu2qrCrpOYc1zc7h0SYV4m6Z4OE530dguEhYeoOM/find-things"
        params = dict()
        params["type"] = type
        params["query"] = searchterm
        if pubkey:
            params["pubkey"] = pubkey
        if filter_retracted:
            endpoint = "RARqGauUpDMEA1o4KBSKC8AeP694qJjpbf7x7FOWHDfM8/find-valid-things"

        yield from self._search(endpoint=endpoint, params=params)


    def find_retractions_of(
        self, source: Union[str, Nanopub], valid_only=True
    ) -> List[str]:
        """Find retractions of given URI

        Find all nanopublications that retract a certain nanopublication.

        Args:
            source (str or nanopub.Publication): URI or Nanopub object to find retractions for
            valid_only (bool): Toggle returning only valid retractions, i.e. retractions that are
                signed with the same public key as the publication they retract. Default is True.

        Returns:
            List of uris that retract the given URI
        """

        if isinstance(source, Nanopub):
            if source.is_test_publication and not self.use_test_server:
                warnings.warn(
                    "You are trying to find retractions on the production server, "
                    "whereas this publication lives on the test server"
                )
            elif not source.is_test_publication and self.use_test_server:
                warnings.warn(
                    "You are trying to find retractions on the test server, "
                    "whereas this publication lives on the production server"
                )
            uri = source.source_uri
        else:
            uri = source

        if valid_only:
            source_publication = Nanopub(
                source_uri=uri,
                conf=NanopubConf(use_test_server=self.use_test_server)
            )
            public_key = source_publication.signed_with_public_key
            if public_key is None:
                raise ValueError("The source publication is not signed with a public key")
        else:
            public_key = None

        results = self.find_nanopubs_with_pattern(
            pred=namespaces.NPX.retracts,
            obj=rdflib.URIRef(uri),
            pubkey=public_key,
            filter_retracted=False,
        )
        return [result["np"] for result in results]


    @staticmethod
    def _query_api(params: dict, endpoint: str, query_url: str) -> requests.Response:
        """Query a specific Nanopub Query endpoint."""
        headers = {"Accept": "application/json"}
        url = query_url + endpoint
        return requests.get(url, params=params, headers=headers)


    def _query_api_try_servers(
        self, params: dict, endpoint: str
    ) -> Tuple[requests.Response, str]:
        """Query the Nanopub Query endpoint.

        Query a Nanopub Query endpoint (for example: 'RARqGauUpDMEA1o4KBSKC8AeP694qJjpbf7x7FOWHDfM8/find-valid-things').
        Try several of the Nanopub Query servers.

        Returns:
            tuple of: r: request response, query_url: url of the Nanopub Query server used.
        """
        r = None
        random.shuffle(self.query_urls)  # To balance load across servers
        for query_url in self.query_urls:
            r = self._query_api(params, endpoint, query_url)
            if r.status_code == 502:  # Server is likely down
                warnings.warn(
                    f"Could not get response from {query_url}, trying other servers"
                )
            else:
                r.raise_for_status()  # For non-502 errors we don't want to try other servers
                return r, query_url
        resp = ""
        if r:
            resp = f" Last response: {r.status_code}:{r.reason}"
        raise requests.HTTPError(
            f"Could not get response from any of the Nanopub Query servers "
            f"endpoints.{resp}"
        )


    def _search(self, endpoint: str, params: dict):
        """
        General nanopub server search method. User should use e.g. find_nanopubs_with_text,
        find_things etc.

        Args:
            endpoint: garlic endpoint to query, for example: find_things
            params: dictionary with parameters for get request

        Raises:
            JSONDecodeError: in case response can't be serialized as JSON, this can happen due to a
                virtuoso error.
        """
        # First try different servers
        r, query_url = self._query_api_try_servers(params, endpoint)
        # If we have found a Nanopub Query server we should use that for further queries (so
        # pagination works properly)
        r = self._query_api(params, endpoint, query_url)
        r.raise_for_status()

        # Check if JSON was actually returned. HTML can be returned instead
        # if e.g. virtuoso errors on the backend (due to spaces in the search
        # string, for example).
        try:
            results = r.json()
        except ValueError as e:
            # Try to give a more understandable error to user when the response
            # is not JSON...
            raise ValueError(
                "The server returned HTML instead of the requested JSON. "
                "This is usually caused by the triple store (e.g. virtuoso) "
                "throwing an error for the given search query."
            ) from e

        bindings = results["results"]["bindings"]
        for result in bindings:
            yield self._parse_search_result(result)


    @staticmethod
    def _parse_search_result(result: dict):
        """
        Parse a nanopub search result (i.e. referring to one matching nanopublication).
        Rename 'v' to 'description', select only date, np, label and description fields
        and unnest them.
        """
        parsed = dict()
        parsed["np"] = result["np"]["value"]

        if "v" in result:
            parsed["description"] = result["v"]["value"]
        elif "description" in result:
            parsed["description"] = result["description"]["value"]
        else:
            parsed["description"] = ""
        if "label" in result:
            parsed["label"] = result["label"]["value"]
        parsed["date"] = result["date"]["value"]
        return parsed
