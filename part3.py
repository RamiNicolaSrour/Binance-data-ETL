import pandas as pd
from decimal import Decimal
from google.cloud import bigquery
from sqlalchemy import create_engine
#conneciotn to postgresql 3nf

PROJECT, LOCATION = "xxxx-xxxx-xxxxx-xx", 'XX'
OPA = create_engine("postgresql+psycopg2://postgres:pw@localhost:5432/postgres")
bq = bigquery.Client(project=PROJECT, location=LOCATION)

for name in ('staging', 'analytics'):
    ds = bigquery.Dataset(f"{PROJECT}.{name}")
    ds.location = LOCATION
    bq.create_dataset(ds, exists_ok=True)

# join here, fusion step
queries = {
    'stg_asset': """select asset_id, asset_symbol, cmc_id, asset_name, asset_type, logo_url from asset""",
    "STG_MARKET": """
      SELECT m.market_id, m.symbol, b.asset_symbol as base_asset, q.asset_symbol as quote_asset,
      m.base_asset_id, m.quote_asset_id, m.base_asset_precision,
      m.quote_asset_precision, m.status
      from market m
      join asset b on b.asset_id = m.base_asset_id
      join asset q on q.asset_id = m.quote_asset_id""",
    "STG_KLINE": """
      SELECT k.*, m.base_asset_id, m.quote_asset_id
      from kline k join market m on m.market_id = k.market_id""",
    "stg_date": 'select * from date',
    "stg_time": 'select * from time_table',
    "STG_TICKER": """
       SELECT t.*, m.base_asset_id, m.quote_asset_id
       from ticker_24h t join market m on m.market_id = t.market_id""",
}

# cleaning rules
rules = {
    'STG_KLINE': dict(keys=['market_id', 'time_key', 'open_time'],
                      group=['market_id', 'time_key'],
                      prices=['open_price', 'high_price', 'low_price', 'close_price']),
    'STG_TICKER': dict(keys=['market_id', 'captured_at'],
                       group=['market_id'],
                       prices=['last_price']),
}

k = 3.0

def clean(df, keys, group, prices):
    df = df.drop_duplicates(subset=keys).copy()
    df[prices] = df[prices].astype(float)
    keep = pd.Series(True, index=df.index)
    for c in prices:
        g =df.groupby(group)[c]
        q1, q3 = g.transform(lambda s: s.quantile(0.1)), g.transform(lambda s: s.quantile(0.9))
        keep &= df[c].between(q1 - k *(q3-q1), q3+k * (q3-q1)) & (df[c] > 0)
    return df[keep]

for table, q in queries.items():
    df = pd.read_sql(q, OPA)
    raw = len(df)
    if table in rules:
        df = clean(df, **rules[table])
    for c in df.columns:
        if df[c].map(lambda v: isinstance(v, Decimal)).any():
            df[c] = df[c].astype(float)
    bq.load_table_from_dataframe(
        df, f"{PROJECT}.staging.{table.lower()}",
        job_config = bigquery.LoadJobConfig(write_disposition='WRITE_TRUNCATE')).result()
    print(f"{table}: raw {raw} -> {len(df)} rows")

    # build star schema
bq.query(open('sql/04starschema.sql').read()).result()
print("Part 3 done")