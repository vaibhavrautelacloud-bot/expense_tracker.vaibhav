"""reports.py - data analysis with Pandas."""
import pandas as pd
import database

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def load_month(user, month, year):
    """Return a DataFrame of this user's expenses in the given month/year."""
    conn = database.get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE username=? "
        "AND strftime('%m', date)=? AND strftime('%Y', date)=?",
        conn, params=(user, f"{int(month):02d}", str(year)))
    conn.close()
    return df


def monthly_summary(user, month, year):
    """Return a dictionary of results, or None if there is no data."""
    df = load_month(user, month, year)
    if df.empty:
        return None
    top = df.loc[df["amount"].idxmax()]
    by_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    return {
        "total": float(df["amount"].sum()),
        "count": len(df),
        "highest_amount": float(top["amount"]),
        "highest_category": top["category"],
        "by_category": by_category,
    }


def month_total(user, month, year):
    summary = monthly_summary(user, month, year)
    return 0.0 if summary is None else summary["total"]


def export_csv(user, filepath):
    """File handling: save this user's expenses into a CSV file."""
    conn = database.get_connection()
    df = pd.read_sql_query(
        "SELECT date, category, amount, description FROM expenses "
        "WHERE username=? ORDER BY date", conn, params=(user,))
    conn.close()
    df.to_csv(filepath, index=False)
    return len(df)