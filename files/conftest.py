import pandas as pd
import pytest


@pytest.fixture
def pint_price():
    return {"Congo": [['City', 'Price'],
                      ['Brazzaville', '$4.75 USD'],
                      ['Point-Noire', '$8.94 USD'],
                      ['Pointe-Noire', '$1.49 USD']]}


@pytest.fixture
def sample_df():
    def _make_df(cols):
        return pd.DataFrame(zip(*cols), columns=["city_ascii", "country"])
    return _make_df
