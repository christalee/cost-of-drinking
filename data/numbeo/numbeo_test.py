import pandas as pd
from numbeo import *


def test_clean(sample_df):
    t1 = [['a', 'b', 'c', 'd'], ['A', 'B', 'C', "D"]]
    t2 = [['test', 'b', 'c', 'd'], ['A', 'B', 'C', "D"]]
    t3 = [['a', 'b', 'c', 'd'], ['A', 'TEST', 'C', "D"]]
    t4 = [['a', 'b', 'c', 'd'], ['A', 'B', 'TEST', "D"]]
    t5 = [['a', 'b', 'c', 'D'], ['A', 'B', 'C', "D"]]
    t6 = [['t', 'b', 'c', 'd'], ['A', 'B', 'C', "D"]]
    t7 = [['test', 'b', 'c', 'd'], ['t', 'B', 'C', "D"]]

    assert clean(sample_df(t1), find_str="a", edit_str="test").equals(sample_df(t2))
    assert clean(sample_df(t1), find_str="B", find_col="country", edit_str="TEST").equals(sample_df(t3))
    assert clean(sample_df(t1), find_str="c", edit_str="TEST", edit_col="country").equals(sample_df(t4))
    assert clean(sample_df(t1), find_str="D", find_col="country", edit_col="city_ascii").equals(sample_df(t5))
    assert clean(sample_df(t2), find_str="t").equals(sample_df(t6))
    assert clean(sample_df(t2), find_str="t", edit_col="country").equals(sample_df(t7))


def test_read_numbeo():
    n = read_numbeo()

    assert len(n) > 600
    assert type(n) == pd.core.frame.DataFrame
    assert list(n.columns) == ['city', 'beer_market', 'beer_pub', 'bread', 'coffee']
    assert list(n.dtypes) == ['object'] + ['float64'] * 4


def test_read_city_data():
    c = read_city_data()

    assert len(c) > 26500
    assert type(c) == pd.core.frame.DataFrame
    assert list(c.columns) == ['city_ascii', 'country', 'region', 'latitude', 'longitude',
                               'population', 'iso2', 'iso3', 'admin_name', 'city']
    assert list(c.dtypes) == ['object'] * 3 + ['float64'] * 3 + ['object'] * 4

    assert len(c[c["city_ascii"] == "Natal"]) == 1
    assert len(c[c['country'] == "Bahamas"]) > 0
    assert len(c[c['country'] == "South Korea"]) > 0


# def test_numbeo_correct():
#     n = read_numbeo()
#     nc = numbeo_correct(n)
#
#     assert len(nc) == len(n)


def test_read_expat():
    e = read_expat()

    assert len(e) > 550
    assert list(e.columns) == ['city_ascii', 'country', 'beer_market', 'bread', 'coffee', 'beer_pub']
    assert list(e.dtypes) == ['object'] * 2 + ['float64'] * 4


# def test_n_e_correct():
#     n = read_numbeo()
#     nc = numbeo_correct(n)
#
#     pass
