import os
import random
import string
import psycopg2
from datetime import datetime, timedelta

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "assignment4_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

NUM_TRADERS = 25000
NUM_TRADES = 1500000

first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
               "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
               "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Wei",
               "Hiroshi", "Anika", "Diego", "Fatima", "Lukas", "Olga", "Pedro"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
              "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
              "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
              "Chen", "Tanaka", "Patel", "Singh", "Mueller", "Rossi", "Kowalski"]

countries = ["USA", "UK", "Canada", "Germany", "France", "Japan", "India", "Brazil",
             "Australia", "Mexico", "South Korea", "Netherlands", "Singapore", "Italy"]

account_types = ["Individual", "Joint", "Retirement", "Corporate", "Margin"]

brokers = ["Fidelity", "Schwab", "Robinhood", "ETrade", "TDAmeritrade", "Vanguard",
           "Interactive", "Webull", "Merrill", "Wells", "JPMorgan", "Citi",
           "MorganStanley", "GoldmanSachs", "AllyInvest", "SoFi", "Public",
           "Tradestation", "Tastyworks", "Saxo", "IG", "Plus500", "eToro",
           "Degiro", "Avanza", "Nordnet", "HL", "Comdirect", "Flatex",
           "Questrade", "Wealthsimple", "FreeTrade", "Trading212", "Lightyear",
           "Revolut", "Stake", "Selfwealth", "CMC", "BMO", "TDDirect"]
for ch1 in string.ascii_uppercase:
    for ch2 in string.ascii_uppercase:
        if len(brokers) < 200:
            brokers.append("Firm" + ch1 + ch2)

popular_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "WMT",
                   "DIS", "NFLX", "BA", "INTC", "AMD", "PYPL", "ORCL", "CSCO", "PEP", "KO",
                   "NKE", "MCD", "GS", "BAC", "C", "T", "VZ", "PFE", "JNJ", "XOM"]

extra_tickers = []
for a in string.ascii_uppercase:
    for b in string.ascii_uppercase:
        if len(extra_tickers) < 250:
            extra_tickers.append(a + b + "X")
        if len(extra_tickers) < 250:
            extra_tickers.append(a + b + "Z")

tickers = popular_tickers + extra_tickers

sides = ["BUY", "SELL"]
order_types = ["MARKET", "LIMIT", "STOP", "STOP_LIMIT"]
exchanges = ["NYSE", "NASDAQ", "AMEX", "LSE", "TSE"]


def main():
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute("TRUNCATE trades, traders RESTART IDENTITY CASCADE;")
    conn.commit()

    print("inserting traders...")
    trader_rows = []
    for i in range(NUM_TRADERS):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        full_name = fn + " " + ln
        email = (fn.lower() + "." + ln.lower() + str(random.randint(1, 9999)) + "@mail.com")
        country = random.choice(countries)
        acct = random.choice(account_types)
        broker = random.choice(brokers)
        risk = random.randint(1, 10)
        bal = round(random.uniform(500, 250000), 2)
        days_back = random.randint(30, 3000)
        opened = datetime.now().date() - timedelta(days=days_back)
        active = random.random() > 0.15
        trader_rows.append((full_name, email, country, acct, broker, risk, bal, opened, active))

    args_str = ",".join(
        cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", r).decode("utf-8")
        for r in trader_rows
    )
    cur.execute(
        "INSERT INTO traders (full_name,email,country,account_type,broker,risk_score,balance,opened_date,is_active) VALUES "
        + args_str
    )
    conn.commit()

    cur.execute("SELECT trader_id FROM traders;")
    trader_ids = [r[0] for r in cur.fetchall()]

    print("inserting trades...")
    batch = []
    base_time = datetime.now() - timedelta(days=365)
    inserted = 0
    for i in range(NUM_TRADES):
        tid = random.choice(trader_ids)
        tk = random.choice(tickers)
        sd = random.choice(sides)
        ot = random.choice(order_types)
        ex = random.choice(exchanges)
        qty = random.randint(1, 1000)
        pr = round(random.uniform(5, 800), 4)
        fee = round(random.uniform(0.5, 25), 2)
        exec_at = base_time + timedelta(seconds=random.randint(0, 365 * 24 * 3600))
        batch.append((tid, tk, sd, ot, ex, qty, pr, fee, exec_at))

        if len(batch) >= 5000:
            args_str = ",".join(
                cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", r).decode("utf-8")
                for r in batch
            )
            cur.execute(
                "INSERT INTO trades (trader_id,ticker,side,order_type,exchange,quantity,price,fee,executed_at) VALUES "
                + args_str
            )
            conn.commit()
            inserted += len(batch)
            print("  ", inserted, "trades")
            batch = []

    if batch:
        args_str = ",".join(
            cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", r).decode("utf-8")
            for r in batch
        )
        cur.execute(
            "INSERT INTO trades (trader_id,ticker,side,order_type,exchange,quantity,price,fee,executed_at) VALUES "
            + args_str
        )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM traders;")
    print("traders:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM trades;")
    print("trades:", cur.fetchone()[0])

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
