
import argparse
import sqlite3
import sys
import pandas as pd

DB_DEFAULT = "mlb_history.db"

def list_tables(conn):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    tables = [row[0] for row in cur.fetchall()]
    if tables:
        print("Tables:")
        for t in tables:
            print("  ", t)
    else:
        print("No tables found.")

def show_schema(conn, table):
    cur = conn.execute(f"PRAGMA table_info('{table}');")
    cols = cur.fetchall()
    if not cols:
        print(f"Table '{table}' does not exist.")
        return
    print(f"Schema for {table}:")
    print("  cid | name       | type     | notnull | dflt_value | pk")
    for cid, name, ctype, notnull, dflt, pk in cols:
        print(f"  {cid:>3} | {name:<10} | {ctype:<8} | {notnull:^7} | {dflt!r:<10} | {pk}")

def run_query(conn, sql):
    try:
        df = pd.read_sql_query(sql, conn)
        if df.empty:
            print("Query executed but no rows returned.")
        else:
            print(df.to_string(index=False))
    except Exception as e:
        print("SQL error:", e)

def repl(conn):
    print("Enter SQL --> .tables or .schema <table> or exit or another other command\n")
    while True:
        try:
            line = input("db> ").strip()
        except EOFError:
            break
        if not line:
            continue
        cmd = line.lower()
        if cmd in ("exit", "quit", ".exit", ".quit"):
            break
        if cmd == ".tables":
            list_tables(conn)
        elif cmd.startswith(".schema"):
            parts = line.split()
            if len(parts) != 2:
                print("Usage: .schema <table>")
            else:
                show_schema(conn, parts[1])
        else:
            run_query(conn, line)
    print("Goodbye! See Ya Later!")

def main():
    parser = argparse.ArgumentParser(
        description="Interactive/query tool for mlb_history.db"
    )
    parser.add_argument(
        "sql", nargs="*", help="If provided, executes this SQL and exits"
    )
    parser.add_argument(
        "-d", "--db", default=DB_DEFAULT,
        help=f"Path to SQLite DB (default '{DB_DEFAULT}')"
    )
    args = parser.parse_args()

    try:
        conn = sqlite3.connect(args.db)
    except Exception as e:
        print(f"Failed to open database '{args.db}':", e)
        sys.exit(1)

    if args.sql:
        run_query(conn, " ".join(args.sql))
    else:
        list_tables(conn)
        repl(conn)

    conn.close()

if __name__ == "__main__":
    main()

