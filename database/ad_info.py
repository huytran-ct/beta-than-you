import sqlite3

class AdInfoDatabase:
    def __init__(self, db_path: str = "hackathon.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """
        Initialize the database and create the table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ads (
                    ad_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    unit_price REAL NOT NULL
                )
            """)
            conn.commit()

    def create_ad(self, subject: str, body: str, unit_price: float):
        """
        Create a new ad in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ads (subject, body, unit_price)
                VALUES (?, ?, ?)
            """, (subject, body, unit_price))
            conn.commit()
            return cursor.lastrowid

    def read_ad(self, ad_id: int):
        """
        Read an ad by its ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ad_info WHERE ad_id = ?", (ad_id,))
            return cursor.fetchone()
    
    def read_ads_by_user_id(self, user_id: int):
        """
        Read ads by user ID.
        Note: This function assumes that there is a user_id column in the ads table.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ad_info WHERE account_id = ?", (user_id,))
            
            # Get column names from cursor description
            columns = [description[0] for description in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            # print(results)
            
            # Convert each row to a dictionary with column names as keys
            return [dict(zip(columns, row)) for row in results]

    def update_ad(self, ad_id: int, subject: str, body: str, unit_price: float):
        """
        Update an existing ad.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ad_info
                SET subject = ?, body = ?, unit_price = ?
                WHERE ad_id = ?
            """, (subject, body, unit_price, ad_id))
            conn.commit()
            return cursor.rowcount

    def delete_ad(self, ad_id: int):
        """
        Delete an ad by its ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ad_info WHERE ad_id = ?", (ad_id,))
            conn.commit()
            return cursor.rowcount

    def flush(self):
        """
        Remove all data from the ads table.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ad_info")
            conn.commit()
            print("All data has been removed from the ads table.")
