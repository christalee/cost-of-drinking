import pandas as pd
from data.numbeo.numbeo import clean


def pp_correct(pp):
    pp = clean(pp, find_str="ManäMa", edit_str="Manama")
    pp = clean(pp, find_str="Jakarta")
    pp = clean(pp, find_str="Quenec City", edit_str="Quebec City")
    pp = clean(pp, find_str="Washonhton", edit_str="Washington")
    pp = clean(pp, find_str="Newcastle Upon Tyne", edit_str="Newcastle upon Tyne")
    pp = clean(pp, find_str="Marrakesh", edit_str="Marrakech")
    pp = clean(pp, find_str="Bengaluru", edit_str="Bangalore")
    pp = clean(pp, find_str="Taipei")
    pp = clean(pp, find_str="Thessalonika", edit_str="Thessaloniki")
    pp = clean(pp, find_str="Rijeka")
    pp = clean(pp, find_str="Guatemala", edit_str="Guatemala City")
    pp = clean(pp, find_str="Dimashq", edit_str="Damascus")
    pp = clean(pp, find_str="Rio De Janeiro", edit_str="Rio de Janeiro")
    pp = clean(pp, find_str="Dar Es Salaam", edit_str="Dar es Salaam")
    pp = clean(pp, find_str="Goiã¢Nia", edit_str="Goiania")
    pp = clean(pp, find_str="Palma De Mallorca", edit_str="Palma de Mallorca")
    pp = clean(pp, find_str="Constanța", edit_str="Constanta")
    pp = clean(pp, find_str="Dnepropetrovsk", edit_str="Dnipro")
    pp = clean(pp, find_str="Fredricton", edit_str="Fredericton")
    pp = clean(pp, find_str="Rochester, Ny", edit_str="Rochester")
    pp = clean(pp, find_str="Salem, Or", edit_str="Salem")
    pp = clean(pp, find_str="St John", edit_str="St. John's")
    pp = clean(pp, find_str="Stoke-On-Trent", edit_str="Stoke-on-Trent")
    pp = clean(pp, find_str="Malã©", edit_str="Male")
    pp = clean(pp, find_str="Santa Cruz De Tenerife", edit_str="Santa Cruz de Tenerife")
    pp = clean(pp, find_str="Yangon", edit_str="Rangoon")
    pp = clean(pp, find_str="Rangoon", edit_col="country", edit_str="Burma")
    pp = clean(pp, find_str="Heraklion", edit_str="Irakleio")
    pp = clean(pp, find_str="Dumaguete")
    pp = clean(pp, find_str="Makati")
    pp = clean(pp, find_str="Santa Cruz de Tenerife", edit_str="Santa Cruz")
    pp = clean(pp, find_str="Pattaya", edit_str="Phatthaya")
    pp = clean(pp, find_str="Arbil", edit_str="Erbil")
    pp = clean(pp, find_str="Georgetown", edit_str="George Town")
    pp = clean(pp, find_str="St Petersburg", edit_str="Saint Petersburg")
    pp = clean(pp, find_str="Rostov")
    pp = clean(pp, find_str="Zaporizhzhya", edit_str="Zaporizhzhia")

    pp = clean(pp, find_col="country", find_str="Bosnia", edit_str="Bosnia And Herzegovina")
    pp = clean(pp, find_col="country", find_str="Cz", edit_str="Czechia")
    pp = clean(pp, find_col="country", find_str="Ivory", edit_str="Côte D’Ivoire")
    pp = clean(pp, find_col="country", find_str="Russia")
    pp = clean(pp, find_col="country", find_str="Korea S", edit_str="South Korea")
    pp = clean(pp, find_col="country", find_str="Byelorussia", edit_str="Belarus")

    return pp


def read_db():
    # load in deutschebank data
    db_beer = pd.read_csv("data/deutschebank/beer-clean.csv").drop(columns=['Unnamed: 0']).rename(columns={"price": "beer_pub"})
    db_cafe = pd.read_csv("data/deutschebank/cappuccino-clean.csv").drop(columns=['Unnamed: 0']).rename(columns={"price": "coffee"})

    # merge deutschebank data together
    db = pd.merge(db_beer, db_cafe, how="outer", on=["city_ascii", "country", "region", "latitude", "longitude", "population"])
    db = db.reindex(columns=["city_ascii",
                             "country",
                             "region",
                             "latitude",
                             "longitude",
                             "population",
                             "coffee",
                             "beer_pub"])
    return db


def db_correct(db):
    db = clean(db, find_str="Manhattan", edit_str="New York")
    db = clean(db, find_str="Delhi")
    db = clean(db, find_col="country", find_str="Korea, South", edit_str="South Korea")

    return db


def df_clean():
    place_cols = ["city_ascii", "admin_name", "country", "region", "latitude", "longitude", "population"]

    df_clean = df_all[place_cols]
    for x in ['pub', 'market', 'bread', 'coffee']:
        x_cols = list(filter(lambda y: x in y, df_all.columns))
        df_clean["avg_" + x] = df_all[x_cols].mean(axis=1).apply(lambda x: round(x, 2))

    df_clean['total'] = df_clean[['avg_pub', 'avg_market', 'avg_bread', 'avg_coffee']].sum(axis=1)

    return df_clean


def main():
    # load in numbeo & expatistan data
    n_e = pd.read_csv('data/numbeo/n_e_clean.csv').drop(columns=["Unnamed: 0"])

    # load & correct pintprice data
    pp = pd.read_csv("data/pintprice/pintprice.csv").drop(columns=['Unnamed: 0']).dropna()
    pp = pp_correct(pp)

    # merge pintprice and previous data
    on_cols = ['city_ascii', 'country']
    df_all = pd.merge(n_e, pp, how="left", on=on_cols)
    df_all = df_all.rename(columns={"beer_pub": "beer_pub_pp"})

    # load & correct deutschebank data
    db = read_db()
    db = db_correct(db)

    # merge deutschebank and previous data
    cols = ['city_ascii', 'country', "coffee", "beer_pub"]
    df_all = pd.merge(df_all, db[cols], how="outer", on=['city_ascii', 'country'])
    df_all = df_all.rename(columns={"coffee": "coffee_db", "beer_pub": "beer_pub_db"})

    df_all.to_csv("df_all.csv")
    df_all.to_json("df_all.json")

    df_clean = df_clean()
    df_clean.to_json("df_final.json")


if __name__ == "__main__":
    main()
