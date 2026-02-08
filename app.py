from flask import Flask
import psycopg2
import time

app = Flask(__name__)

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host="postgres-db",
                database="flaskdb",
                user="admin",
                password="secret"
            )
            return conn
        except:
            print("Waiting for database...")
            time.sleep(2)

@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY);")
    cur.execute("INSERT INTO visits DEFAULT VALUES;")
    cur.execute("SELECT COUNT(*) FROM visits;")
    count = cur.fetchone()[0]
    cur.close()
    conn.commit()
    conn.close()
    return f"Hello! This page has been visited {count} times."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

