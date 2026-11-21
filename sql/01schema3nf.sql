create schema if not exists CRYPTS;
create table if not exists asset (
    asset_id SERIAL primary key,
    asset_symbol     varchar(20) not null unique,
    cmc_id      integer unique,
    asset_name   varchar(100),
    asset_type  varchar(50),
    logo_url    text
);

create table if not exists market (
    market_id           SERIAL primary key,
    symbol              varchar(30) not null unique,
    base_asset_id       int not null references asset(asset_id),
    quote_asset_id      int not null references asset(asset_id),
    base_asset_precision   int,
    quote_asset_precision int,
    status              varchar(20),
    is_spot_trading_allowed     boolean 
);

create table if not exists time_table (
    time_key SERIAL primary key,
    interval    varchar(5) not null unique
);

create table if not exists date (
    date_key SERIAL primary key,
    calendar_date date not null unique,
    year integer not null,
    quarter integer not null,
    month integer not null,
    week integer not null,
    day integer not null
);

create table if not exists kline (
    kline_id          serial primary key,
    market_id           int references market(market_id),
    time_key         int references time_table(time_key),
    date_key         int references date(date_key),
    open_time           timestamp not null,
    open_price          numeric(38,12),
    high_price          numeric(38,12),
    low_price          numeric(38,12),
    close_price          numeric(38,12),
    volume         numeric(38,12),
    close_time          timestamp,
    quote_asset_volume          numeric(38,12),
    number_of_trades        bigint,
    taker_buy_base_asset_volume     numeric(38,12),
    taker_buy_quote_asset_volume     numeric(38,12),
    unique        (market_id, time_key, open_time)
);

create table if not exists ticker_24h (
    price24hr_id     serial primary key,
    market_id           int references market(market_id),
    price_change_per          numeric(38,12),
    last_price          numeric(38,12),
    last_qty       numeric(38,12),
    open_price          numeric(38,12),
    high_price          numeric(38,12),
    low_price          numeric(38,12),
    volume          numeric(38,12),
    quote_volume          numeric(38,12),
    open_time        timestamp,
    close_time        timestamp,
    count        bigint,
    captured_at timestamp,
    UNIQUE (market_id, captured_at)
);