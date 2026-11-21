from sqlalchemy import create_engine
from part1 import df_EI, df_klines, df_ticker
from part1 import extract, get_cmc

df_EI, df_klines, df_ticker = extract()
df_assets = get_cmc()

OPA = create_engine('postgresql+psycopg2://postgres:pw@localhost:5432/postgres')
def run_sql_file(path):
    with OPA.begin() as conn:
        conn.exec_driver_sql(open(path).read())

run_sql_file('sql/01schema3nf.sql')

# raw copies of the dataframe
df_assets.to_sql('stg_asset', OPA, if_exists='replace', index=False)
df_EI.to_sql('stg_market', OPA, if_exists='replace', index=False)
df_klines.to_sql('stg_kline', OPA, if_exists='replace', index=False)
df_ticker.to_sql('stg_ticker', OPA, if_exists='replace', index=False)


run_sql_file('sql/02load3nf.sql')
print('part 2 done')