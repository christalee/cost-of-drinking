import pickle
from unittest.mock import patch

import pandas as pd
from bs4 import BeautifulSoup
from pintprice import *

html = open('congo.htm', 'r', encoding="windows-1252")


@patch("pintprice.request.urlopen", return_value=html)
def test_get_soup(mock_soup):
    # assert get_soup("asdf") is None
    mock_soup.return_value.status = 200

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


@patch("pintprice.get_soup", return_value=BeautifulSoup(html, 'html.parser'))
def test_get_countries(mock_soup):
    congo = get_countries(mock_soup("Congo"))

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
