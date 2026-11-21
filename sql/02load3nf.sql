insert into asset (asset_symbol, cmc_id, asset_name, asset_type, logo_url)
select asset_symbol, cmc_id, asset_name, asset_type, logo_url from stg_asset
on conflict (asset_symbol) do nothing;

insert into market (symbol, base_asset_id, quote_asset_id, base_asset_precision, quote_asset_precision, status, is_spot_trading_allowed)
select s.symbol, b.asset_id, q.asset_id, s.base_asset_precision, s.quote_asset_precision, s.status, s.is_spot_trading_allowed
from stg_market s
join asset b on b.asset_symbol = s.base_asset
join asset q on q.asset_symbol = s.quote_asset
on conflict (symbol) do nothing;

insert into time_table (interval)
select distinct interval from stg_kline
on conflict (interval) do nothing;

insert into date (date_key, calendar_date, year, quarter, month, week, day)
select to_char(d, 'YYYYMMDD')::int, d::date, extract(year from d)::int, extract (quarter from d)::int,
        extract(month from d)::int, extract(week from d)::int, extract(day from d)::int
from generate_series(date '2022-01-01', current_date, interval '1 day') as d
on conflict (date_key) do nothing;

insert into kline (market_id, time_key, date_key, open_time, open_price, high_price, low_price,
                   close_price, close_time, volume, quote_asset_volume, number_of_trades,
                   taker_buy_base_asset_volume, taker_buy_quote_asset_volume)
select m.market_id, t.time_key,
        to_char(k.open_time , 'yyyymmdd')::int,
        k.open_time,
        k.open_price::numeric, k.high_price::numeric, k.low_price::numeric, k.close_price::numeric, k.close_time, k.volume::numeric,
        k.quote_asset_volume::numeric, k.number_of_trades,
        k.taker_buy_base_asset_volume::numeric, k.taker_buy_quote_asset_volume::numeric
from stg_kline k
join market m on m.symbol = k.symbol
join time_table t on t.interval = k.interval
on conflict (market_id, time_key, open_time) do nothing;

insert into ticker_24h (market_id, price_change_per, last_price,
                        last_qty, open_price, high_price, low_price,
                        volume, quote_volume, open_time, close_time, "count", captured_at)
select m.market_id, t.price_change_per::numeric, t.last_price::numeric,
       t.last_qty::numeric, t.open_price::numeric, t.high_price::numeric,
       t.low_price::numeric, t.volume::numeric, t.quote_volume::numeric,
       t.open_time,
       t.close_time,
       t.count, t.captured_at
from stg_ticker t
join market m on m.symbol = t.symbol
on conflict (market_id, captured_at) do nothing;