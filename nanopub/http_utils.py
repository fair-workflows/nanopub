"""Shared HTTP helpers.

The services nanopub talks to (the Nanopub Query servers, the registry, the
handle system) intermittently answer with transient errors that succeed on an
immediate retry. This module provides a requests Session that retries those
automatically, so callers do not have to.
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from nanopub.definitions import DEFAULT_HTTP_TIMEOUT

# Statuses that mean "the server, or a proxy in front of it, is having a
# temporary problem" - the same request may well succeed a moment later.
# 520-524 are Cloudflare-specific: hdl.handle.net sits behind Cloudflare and
# intermittently answers 520 ("unknown error") for handles that resolve fine
# on the next attempt.
TRANSIENT_STATUS_CODES = (429, 500, 502, 503, 504, 520, 521, 522, 523, 524)

DEFAULT_MAX_RETRIES = 3
# urllib3 sleeps backoff_factor * (2 ** (attempt - 1)) between attempts, so
# with 3 retries this waits 0s, 1s and 2s: enough to ride out a blip without
# stalling a caller for long when the service is genuinely down.
DEFAULT_BACKOFF_FACTOR = 0.5


class _TimeoutHTTPAdapter(HTTPAdapter):
    """Adapter that applies a default timeout to every request on the session.

    requests has no session-wide timeout setting, and a request without one
    blocks indefinitely. Retrying makes that worse, since each attempt could
    hang, so the timeout is enforced here rather than left to each call site.
    """

    def __init__(self, *args, timeout=DEFAULT_HTTP_TIMEOUT, **kwargs):
        self._timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = self._timeout
        return super().send(request, **kwargs)


def retrying_session(
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        timeout=DEFAULT_HTTP_TIMEOUT,
) -> requests.Session:
    """Build a Session that retries transient failures on idempotent requests.

    Retries cover both transport errors (connection failures, timeouts) and the
    statuses in TRANSIENT_STATUS_CODES. Only idempotent methods are retried, so
    a POST - publishing a nanopub, for instance - is never sent twice.

    Once the retries are exhausted the final response is returned as-is rather
    than raised, leaving the caller's own error handling in charge.
    """
    retry = Retry(
        total=max_retries,
        connect=max_retries,
        read=max_retries,
        status=max_retries,
        status_forcelist=TRANSIENT_STATUS_CODES,
        backoff_factor=backoff_factor,
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
        raise_on_status=False,
    )
    adapter = _TimeoutHTTPAdapter(max_retries=retry, timeout=timeout)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


_session: requests.Session = None


def get_session() -> requests.Session:
    """The shared retrying session, created on first use."""
    global _session
    if _session is None:
        _session = retrying_session()
    return _session
