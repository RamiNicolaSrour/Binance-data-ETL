select m.symbol, b.asset_symbol as base, q.asset_symbol as quote
from market m
join asset b on  b.asset_id = m.base_asset_id
join asset q on  q.asset_id = m.quote_asset_id
limit 10;