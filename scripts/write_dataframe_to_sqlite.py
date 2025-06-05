import pandas as pd
import sqlite3

def write_dataframe_to_sqlite(df: pd.DataFrame, db_path: str, table_name: str):
    """
    Write a Pandas DataFrame to an SQLite database.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to write data into.
    """
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Data written to table '{table_name}' in database '{db_path}'.")

if __name__ == "__main__":
    # Example DataFrame
    ad_info_df = pd.read_csv("data/ad_info.csv")
    ad_performance_df = pd.read_csv("data/pty_ad_performance.csv")
    orders_df = pd.read_csv("data/orders.csv")

    # Write DataFrame to SQLite database
    write_dataframe_to_sqlite(ad_info_df, "hackathon.db", "ad_info")
    write_dataframe_to_sqlite(ad_performance_df, "hackathon.db", "ad_performance")
    write_dataframe_to_sqlite(orders_df, "hackathon.db", "orders")
    print("DataFrame written to SQLite database successfully.")
