"""Tests for the retrying HTTP session.

These run against a throwaway HTTP server on localhost rather than mocks, so
they exercise the real urllib3 retry machinery: the responses, the retried
methods and the give-up behaviour are all the genuine article.
"""
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
import requests
from requests.adapters import HTTPAdapter

from nanopub.definitions import DEFAULT_HTTP_TIMEOUT
from nanopub.http_utils import (
    DEFAULT_MAX_RETRIES,
    TRANSIENT_STATUS_CODES,
    retrying_session,
)


class _ScriptedHandler(BaseHTTPRequestHandler):
    """Answers with the statuses queued in the server's `script`, in order."""

    def _respond(self):
        self.server.requests.append((self.command, self.path))
        # Drain any request body, or the client sees a connection reset
        # instead of our response.
        body_length = int(self.headers.get("Content-Length") or 0)
        if body_length:
            self.rfile.read(body_length)
        if self.server.script:
            status = self.server.script.pop(0)
        else:
            status = 200
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"values": []}')

    do_GET = _respond
    do_POST = _respond

    def log_message(self, *args):
        pass  # keep the test output quiet


@pytest.fixture
def scripted_server():
    """A local server that replays a scripted list of status codes."""
    server = HTTPServer(("127.0.0.1", 0), _ScriptedHandler)
    server.script = []
    server.requests = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


@pytest.fixture
def session():
    # No backoff: these tests care about the retry behaviour, not the waiting.
    return retrying_session(backoff_factor=0)


def _url(server, path="/handle"):
    host, port = server.server_address
    return f"http://{host}:{port}{path}"


def test_retries_520_then_succeeds(scripted_server, session):
    """The failure that made the FDO handle test flake: Cloudflare 520."""
    scripted_server.script = [520, 520]

    response = session.get(_url(scripted_server))

    assert response.status_code == 200
    assert len(scripted_server.requests) == 3  # two failures, then the success


@pytest.mark.parametrize("status", TRANSIENT_STATUS_CODES)
def test_retries_every_transient_status(scripted_server, session, status):
    scripted_server.script = [status]

    response = session.get(_url(scripted_server))

    assert response.status_code == 200
    assert len(scripted_server.requests) == 2


def test_does_not_retry_client_errors(scripted_server, session):
    """A 404 is the server's real answer, so it must not be retried."""
    scripted_server.script = [404]

    response = session.get(_url(scripted_server))

    assert response.status_code == 404
    assert len(scripted_server.requests) == 1


def test_returns_last_response_when_retries_run_out(scripted_server, session):
    """Give up with the real response, so callers keep their error handling."""
    scripted_server.script = [520] * (DEFAULT_MAX_RETRIES + 1)

    response = session.get(_url(scripted_server))

    assert response.status_code == 520
    assert len(scripted_server.requests) == DEFAULT_MAX_RETRIES + 1
    with pytest.raises(requests.HTTPError):
        response.raise_for_status()


def test_does_not_retry_post(scripted_server, session):
    """Publishing must never be resent: a retried POST could publish twice."""
    scripted_server.script = [503]

    response = session.post(_url(scripted_server), data=b"x")

    assert response.status_code == 503
    assert len(scripted_server.requests) == 1


def test_applies_a_default_timeout(scripted_server, session, monkeypatch):
    """Every request carries a timeout, even though the caller passed none.

    Recorded on the base adapter, i.e. below the layer that injects it, so this
    sees what actually goes out on the wire.
    """
    sent = {}
    original_send = HTTPAdapter.send

    def recording_send(self, request, **kwargs):
        sent["timeout"] = kwargs.get("timeout")
        return original_send(self, request, **kwargs)

    monkeypatch.setattr(HTTPAdapter, "send", recording_send)
    session.get(_url(scripted_server))

    assert sent["timeout"] == DEFAULT_HTTP_TIMEOUT


def test_caller_timeout_wins(scripted_server, session, monkeypatch):
    """An explicit timeout is not overridden by the session default."""
    sent = {}
    original_send = HTTPAdapter.send

    def recording_send(self, request, **kwargs):
        sent["timeout"] = kwargs.get("timeout")
        return original_send(self, request, **kwargs)

    monkeypatch.setattr(HTTPAdapter, "send", recording_send)
    session.get(_url(scripted_server), timeout=17)

    assert sent["timeout"] == 17
