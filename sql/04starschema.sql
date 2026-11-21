-- dimensions tables

create or replace table analytics.dim_asset as
select asset_id as asset_key, asset_symbol, cmc_id, asset_name, asset_type, logo_url
from staging.stg_asset;


create or replace table analytics.dim_market as
select market_id as market_exchange_key, symbol, base_asset, quote_asset,
       base_asset_precision, quote_asset_precision, status
from staging.stg_market;

create or replace table analytics.dim_date as
select date_key, calendar_date, year, quarter, month, week, day
from staging.stg_date;

create or replace table analytics.dim_time as
select time_key, `interval`
from staging.stg_time;

-- the fact tables
create or replace table analytics.fact_kline as
select kline_id as kline_key, market_id as market_exchange_key, base_asset_id as base_asset_key,
       quote_asset_id as quote_asset_key, date_key, time_key,
       open_time, open_price, high_price, low_price, close_price,
       volume, close_time, quote_asset_volume, number_of_trades,
       taker_buy_base_asset_volume, taker_buy_quote_asset_volume
from staging.stg_kline;

create or replace table analytics.fact_ticker24hr as
select price24hr_id as price24hr_key, market_id as market_exchange_key,
       base_asset_id as base_asset_key, quote_asset_id as quote_asset_key,
       cast(format_date('%Y%m%d', DATE(captured_at)) as int64) as date_key,
       price_change_per, last_price, last_qty, open_price, high_price, low_price,
       volume, quote_volume, open_time, close_time, count, captured_at
from staging.stg_ticker;