"""
Utility functions for the Blog Collector.
Provides centralized session management with retry logic for robust HTTP requests.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Tuple


def get_retry_session(
    retries: int = 3,
    backoff_factor: float = 1.0,
    status_forcelist: Tuple[int, ...] = (500, 502, 503, 504),
    session: Optional[requests.Session] = None,
) -> requests.Session:
    """
    Get a requests.Session object with automatic retry logic configured.

    Args:
        retries: Number of total retries to attempt.
        backoff_factor: Factor to apply between attempts (sleep = backoff_factor * (2 ^ (retry - 1))).
        status_forcelist: HTTP status codes to force a retry on.
        session: Optional existing session to configure. If None, a new one is created.

    Returns:
        requests.Session: Configured session object.
    """
    session = session or requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'])
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
