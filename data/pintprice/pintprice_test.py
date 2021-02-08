import pandas as pd
from pintprice import *


def test_get_soup():
    assert get_soup("asdf") is None

    congo = get_soup("Congo")
    assert "Congo" in str(congo)
    assert "USD" in str(congo)
    assert "<td>" in str(congo)
    assert type(congo) == BeautifulSoup


def test_get_prices():
    assert get_prices("asdf") is None

    congo = get_prices("Congo")
    assert len(congo) > 1
    assert type(congo) == list


def test_get_countries():
    congo = get_countries(get_soup("Congo"))

    assert "Congo" in congo
    assert "United Kingdom" in congo
    assert len(congo) > 200

    for x in ["USD", "GBP", "AUD", "CAD", "EUR"]:
        assert x not in congo


def test_tidy(pint_price):
    congo = tidy("Congo", pint_price)

    assert type(congo) == pd.core.frame.DataFrame
    assert list(congo.columns) == ["City", "Price", "Country"]
    assert list(congo.dtypes) == ["object", "float64", "object"]
