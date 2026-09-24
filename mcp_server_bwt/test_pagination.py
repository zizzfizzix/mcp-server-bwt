import pytest

from mcp_server_bwt.tools.bing_webmaster import (
    DEFAULT_PAGE_SIZE,
    PAGE_SIZE_ENV,
    paginate,
    resolve_page_size,
)

ROWS = list(range(5))


@pytest.mark.parametrize(
    ("offset", "limit", "expected"),
    [
        (0, 2, ([0, 1], 5, 2)),  # first page
        (2, 2, ([2, 3], 5, 4)),  # middle page
        (4, 2, ([4], 5, None)),  # last, short page
        (3, 2, ([3, 4], 5, None)),  # last page ending exactly at the end
        (5, 2, ([], 5, None)),  # offset at the end
        (9, 2, ([], 5, None)),  # offset past the end
        (0, None, (ROWS, 5, None)),  # unbounded
        (2, None, ([2, 3, 4], 5, None)),  # unbounded from an offset
    ],
)
def test_paginate(
    offset: int, limit: int | None, expected: tuple[list[int], int, int | None]
) -> None:
    """#39: slices, totals and next offsets cover every page position."""
    assert paginate(ROWS, offset, limit) == expected


def test_paginate_empty_list() -> None:
    assert paginate([], 0, 50) == ([], 0, None)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, DEFAULT_PAGE_SIZE),
        ("", DEFAULT_PAGE_SIZE),
        ("0", None),
        ("1", 1),
        (" 120 ", 120),
        ("500", 500),
    ],
)
def test_resolve_page_size(value: str | None, expected: int | None) -> None:
    """#39: the env var tunes the default page size, 0 disables paging."""
    environ = {} if value is None else {PAGE_SIZE_ENV: value}
    assert resolve_page_size(environ) == expected


@pytest.mark.parametrize("value", ["-1", "501", "ten", "1.5"])
def test_resolve_page_size_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError, match=PAGE_SIZE_ENV):
        resolve_page_size({PAGE_SIZE_ENV: value})
