# CSE 412 Assignment 4

Flask web app for CSE 412 Assignment 4 that shows the difference between indexed and non indexed search queries on a postgres database. The dataset is a fake stock trade ledger that I partially wrote some data generation for in the last assignment. 

## What it does
There are two tables, `traders` and `trades`. The app lets you search trades by ticker (single table) and join trades with traders filtering by broker. You can run each search with or without using the index. The page shows the execution time in ms and the top 5 rows.

The UI is a simple table set up in HTML and populated using Flask's render template API.  

## Setup

Make sure Postgres is running locally (I am running the default set up for the class).

1. Create the virtual env and install stuff (you don't have to use a venv but i recommend it, especially if you grade a lot of stuff):
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create the database:
```
createdb -U postgres assignment4_db
```

3. Load the schema:
```
psql -U postgres -d assignment4_db -f schema.sql
```

4. Load the data:
```
python data_generation.py
```

5. Run the app:
```
python app.py
```

Open http://localhost:5050 in a browser. 


## Env vars (optional)
Make sure to set your environment variables, they have the following key-value pairs for my setup
- DB_HOST (default localhost)
- DB_NAME (default assignment4_db)
- DB_USER (default postgres)
- DB_PASSWORD (default empty)
