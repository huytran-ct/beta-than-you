import sqlite3
from datetime import datetime

class OrdersDatabase:
    def __init__(self, db_path: str = "hackathon.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """
        Initialize the database and create the orders table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    ad_id INTEGER NOT NULL,
                    ad_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    city_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    account_id INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL
                )
            """)
            conn.commit()

    def create_order(self, ad_id: int, ad_type: str, category: str, city_id: int, 
                     price: float, account_id: int, start_date: str, end_date: str):
        """
        Create a new order in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (ad_id, ad_type, category, city_id, price, account_id, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ad_id, ad_type, category, city_id, price, account_id, start_date, end_date))
            conn.commit()
            return cursor.lastrowid

    def read_order(self, ad_id: int):
        """
        Read an order by its ad_id.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE ad_id = ?", (ad_id,))
            result = cursor.fetchone()
            
            if result:
                # Get column names from cursor description
                columns = [description[0] for description in cursor.description]
                # Convert row to dictionary
                return [dict(zip(columns, result))]
            return []
    
    def read_orders_by_ad_id(self, ad_id: int):
        """
        Read orders by ad_id.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE ad_id = ?", (ad_id,))
            
            # Get column names from cursor description
            columns = [description[0] for description in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            
            # Convert each row to a dictionary with column names as keys
            return [dict(zip(columns, row)) for row in results]

    def read_orders_by_account_id(self, account_id: int):
        """
        Read orders by account ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE account_id = ?", (account_id,))
            
            # Get column names from cursor description
            columns = [description[0] for description in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            
            # Convert each row to a dictionary with column names as keys
            return [dict(zip(columns, row)) for row in results]

    def update_order(self, ad_id: int, ad_type: str = None, category: str = None, 
                     city_id: int = None, price: float = None, account_id: int = None,
                     start_date: str = None, end_date: str = None):
        """
        Update an existing order.
        Only updates fields that are not None.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current order data
            current_order = self.read_order(ad_id)
            if not current_order:
                return 0  # Order doesn't exist
            
            # Update only the fields provided
            updated_values = {
                "ad_type": ad_type if ad_type is not None else current_order["ad_type"],
                "category": category if category is not None else current_order["category"],
                "city_id": city_id if city_id is not None else current_order["city_id"],
                "price": price if price is not None else current_order["price"],
                "account_id": account_id if account_id is not None else current_order["account_id"],
                "start_date": start_date if start_date is not None else current_order["start_date"],
                "end_date": end_date if end_date is not None else current_order["end_date"]
            }
            
            cursor.execute("""
                UPDATE orders
                SET ad_type = ?, category = ?, city_id = ?, price = ?, account_id = ?, start_date = ?, end_date = ?
                WHERE ad_id = ?
            """, (updated_values["ad_type"], updated_values["category"], updated_values["city_id"], 
                  updated_values["price"], updated_values["account_id"], updated_values["start_date"], 
                  updated_values["end_date"], ad_id))
            conn.commit()
            return cursor.rowcount

    def delete_order(self, ad_id: int):
        """
        Delete an order by its ad_id.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders WHERE ad_id = ?", (ad_id,))
            conn.commit()
            return cursor.rowcount

    def get_active_orders(self, current_date=None):
        """
        Get all active orders (where current date is between start_date and end_date).
        """
        if current_date is None:
            current_date = datetime.now().strftime('%Y-%m-%d')
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders 
                WHERE start_date <= ? AND end_date >= ?
            """, (current_date, current_date))
            
            # Get column names from cursor description
            columns = [description[0] for description in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            
            # Convert each row to a dictionary with column names as keys
            return [dict(zip(columns, row)) for row in results]

    def flush(self):
        """
        Remove all data from the orders table.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders")
            conn.commit()
            print("All data has been removed from the orders table.")
