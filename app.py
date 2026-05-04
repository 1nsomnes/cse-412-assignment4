import os
import time
import psycopg2
from flask import Flask, render_template, request, jsonify

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "assignment4_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def make_indexes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trades(ticker);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_traders_broker ON traders(broker);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_trader_id ON trades(trader_id);")
    conn.commit()
    cur.close()
    conn.close()


make_indexes()


def run_query(mode, sql, params):
    conn = get_conn()
    cur = conn.cursor()
    try:
        if mode == "no_index":
            cur.execute("SET LOCAL enable_indexscan = off;")
            cur.execute("SET LOCAL enable_bitmapscan = off;")

        explain_sql = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql
        t0 = time.perf_counter()
        cur.execute(explain_sql, params)
        plan = cur.fetchone()[0]
        try:
            exec_ms = float(plan[0]["Execution Time"])
        except Exception:
            exec_ms = (time.perf_counter() - t0) * 1000.0

        cur.execute(sql, params)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        conn.commit()
        return exec_ms, cols, rows
    finally:
        cur.close()
        conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json(force=True)
    mode = data.get("mode", "indexed")
    qtype = data.get("query_type", "single")
    term = data.get("search_term", "")

    if qtype == "single":
        sql = "SELECT trade_id, trader_id, ticker, side, quantity, price, executed_at FROM trades WHERE ticker = %s ORDER BY executed_at DESC LIMIT 5"
        params = (term,)
    else:
        sql = ("SELECT t.trade_id, tr.full_name, tr.broker, t.ticker, t.side, t.quantity, t.price, t.executed_at "
               "FROM trades t JOIN traders tr ON t.trader_id = tr.trader_id "
               "WHERE tr.broker = %s ORDER BY t.executed_at DESC LIMIT 5")
        params = (term,)

    exec_ms, cols, rows = run_query(mode, sql, params)

    out_rows = []
    for r in rows:
        out_rows.append([str(x) if x is not None else "" for x in r])

    return jsonify({
        "execution_time_ms": exec_ms,
        "columns": cols,
        "rows": out_rows,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
