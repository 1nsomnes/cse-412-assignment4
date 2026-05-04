DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS traders;

CREATE TABLE traders (
    trader_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(120),
    country VARCHAR(40),
    account_type VARCHAR(20),
    broker VARCHAR(40),
    risk_score INT,
    balance NUMERIC(14,2),
    opened_date DATE,
    is_active BOOLEAN
);

CREATE TABLE trades (
    trade_id SERIAL PRIMARY KEY,
    trader_id INT REFERENCES traders(trader_id),
    ticker VARCHAR(10),
    side VARCHAR(4),
    order_type VARCHAR(20),
    exchange VARCHAR(20),
    quantity INT,
    price NUMERIC(12,4),
    fee NUMERIC(8,2),
    executed_at TIMESTAMP
);
