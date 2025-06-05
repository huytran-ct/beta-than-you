import sqlite3
from datetime import datetime

class AdPerformanceDatabase:
    def __init__(self, db_path: str = "hackathon.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """
        Initialize the database and create the ad_performance table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ad_performance (
                    ad_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    adview INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (ad_id, date)
                )
            """)
            conn.commit()

    def create_performance_record(self, ad_id: int, date: str, adview: int):
        """
        Create a new ad performance record in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ad_performance (ad_id, date, adview)
                VALUES (?, ?, ?)
            """, (ad_id, date, adview))
            conn.commit()
            return cursor.rowcount

    def read_performance_by_ad_and_date(self, ad_id: int, date: str):
        """
        Read ad performance by ad_id and date.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ad_performance WHERE ad_id = ? AND date = ?", (ad_id, date))
            result = cursor.fetchone()
            
            if result:
                # Get column names from cursor description
                columns = [description[0] for description in cursor.description]
                # Convert row to dictionary
                return dict(zip(columns, result))
            return None

    def read_performance_by_ad_id(self, ad_id: int):
        """
        Read all performance records for a specific ad_id.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ad_performance WHERE ad_id = ? ORDER BY date", (ad_id,))
            
            # Get column names from cursor description
            columns = [description[0] for description in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            
            # Convert each row to a dictionary with column names as keys
            return [dict(zip(columns, row)) for row in results]

    def read_performance_by_date(self, date: str):
        """
        Read all performance records for a specific date.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ad_performance WHERE date = ? ORDER BY ad_id", (date,))
            
            # Get column names from cursor description
            columns = [description[0] for description in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            
            # Convert each row to a dictionary with column names as keys
            return [dict(zip(columns, row)) for row in results]

    def update_adview(self, ad_id: int, date: str, adview: int):
        """
        Update the adview count for a specific ad and date.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ad_performance
                SET adview = ?
                WHERE ad_id = ? AND date = ?
            """, (adview, ad_id, date))
            conn.commit()
            return cursor.rowcount

    def increment_adview(self, ad_id: int, date: str = None):
        """
        Increment the adview count for a specific ad and date by 1.
        If date is not provided, uses current date.
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ad_performance (ad_id, date, adview)
                VALUES (?, ?, 1)
                ON CONFLICT(ad_id, date) DO UPDATE SET
                adview = adview + 1
            """, (ad_id, date))
            conn.commit()
            return cursor.rowcount

    def delete_performance_record(self, ad_id: int, date: str):
        """
        Delete a performance record by ad_id and date.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ad_performance WHERE ad_id = ? AND date = ?", (ad_id, date))
            conn.commit()
            return cursor.rowcount

    def delete_performance_by_ad_id(self, ad_id: int):
        """
        Delete all performance records for a specific ad_id.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ad_performance WHERE ad_id = ?", (ad_id,))
            conn.commit()
            return cursor.rowcount

    def get_total_adviews_by_ad(self, ad_id: int):
        """
        Get the total adviews for a specific ad across all dates.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(adview) as total_adviews FROM ad_performance WHERE ad_id = ?", (ad_id,))
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0

    def flush(self):
        """
        Remove all data from the ad_performance table.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ad_performance")
            conn.commit()
            print("All data has been removed from the ad_performance table.")
