import pytest
from main import parse_google_sheet_url


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://docs.google.com/spreadsheets/d/abc123/edit?gid=0#gid=0",
            ("abc123", 0)
        ),
        (
            "https://docs.google.com/spreadsheets/d/xyz789/edit#gid=5",
            ("xyz789", 5)
        ),
        (
                "https://docs.google.com/spreadsheets/d/bcr231/edit?gid=1",
                ("bcr231", 1)
        ),
        (
            "https://docs.google.com/spreadsheets/d/aaa111/edit",
            ("aaa111", 0)
        )
    ]
)
def test_parse_google_sheet_url(url, expected):
    assert parse_google_sheet_url(url) == expected


def test_parse_google_sheet_url_invalid():
    import pytest
    from main import parse_google_sheet_url

    with pytest.raises(ValueError):
        parse_google_sheet_url("https://docs.google.com/spreadsheets/invalid_url")
