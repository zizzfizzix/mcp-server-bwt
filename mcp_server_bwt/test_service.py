import asyncio

import pytest

from mcp_server_bwt.services.bing_webmaster import BingWebmasterService


def test_service_context_manager_returns_self_and_propagates_errors() -> None:
    """Regression for #9: the typed __aenter__/__aexit__ keep their runtime behavior."""
    service = BingWebmasterService("dummy")

    async def run() -> None:
        async with service as entered:
            assert entered is service
            assert entered.client is not None
            assert entered.sites is not None
            raise KeyError("boom")

    with pytest.raises(KeyError):
        asyncio.run(run())
