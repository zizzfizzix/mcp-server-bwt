import re
from datetime import datetime, timezone
from typing import Any

from bing_webmaster_tools import utils
from bing_webmaster_tools.models import base

_original_parse = utils.parse_timestamp_from_api


def _utc_parse_timestamp_from_api(value: Any) -> datetime:
    """Parse a timestamp from a .NET JSON date string into a UTC timezone-aware datetime."""
    if not isinstance(value, str):
        raise TypeError(f"Expected {value} to be string")
    match = re.search(r"/Date\((-?\d+)(?:[+-]\d{4})?\)/", value)
    if match:
        timestamp = int(match.group(1)) / 1000
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    res = _original_parse(value)
    if res.tzinfo is None:
        return res.replace(tzinfo=timezone.utc)
    return res


# Monkey-patch bing_webmaster_tools date parsing to return UTC timezone-aware datetimes.
# This prevents FastMCP / Pydantic from serializing dates without timezone info,
# which breaks RFC 3339 date-time JSON schema validation in MCP clients (Claude Desktop, Antigravity).
utils.parse_timestamp_from_api = _utc_parse_timestamp_from_api
base.parse_timestamp_from_api = _utc_parse_timestamp_from_api
