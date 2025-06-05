import sqlite3
import json
from typing import List, Dict, Any, Optional


class AdsRegisterDatabase:
    """
    Database class for managing user ad registrations.
    Stores relationships between users and their registered ads.
    """
    
    def __init__(self, db_path: str = "hackathon.db"):
        """
        Initialize the AdsRegisterDatabase.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        """
        Initialize the database and create the ads_register table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ads_register (
                    user_id INTEGER PRIMARY KEY,
                    list_ad_ids TEXT NOT NULL,
                    list_titles TEXT NOT NULL
                )
            """)
            conn.commit()

    def _serialize_list(self, data: List[Any]) -> str:
        """
        Serialize a list to JSON string for database storage.
        
        Args:
            data: List to serialize.
            
        Returns:
            JSON string representation of the list.
        """
        return json.dumps(data)

    def _deserialize_list(self, data: str) -> List[Any]:
        """
        Deserialize JSON string back to a list.
        
        Args:
            data: JSON string to deserialize.
            
        Returns:
            Deserialized list.
        """
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return []

    def create_user_registration(self, user_id: int, ad_ids: List[int], titles: List[str]) -> bool:
        """
        Create a new user ad registration.
        
        Args:
            user_id: Unique identifier for the user.
            ad_ids: List of ad IDs associated with the user.
            titles: List of ad titles corresponding to the ad IDs.
            
        Returns:
            True if registration was created successfully, False otherwise.
            
        Raises:
            ValueError: If ad_ids and titles lists have different lengths.
        """
        if len(ad_ids) != len(titles):
            raise ValueError("ad_ids and titles lists must have the same length")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ads_register (user_id, list_ad_ids, list_titles)
                    VALUES (?, ?, ?)
                """, (user_id, self._serialize_list(ad_ids), self._serialize_list(titles)))
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def read_user_registration(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Read user ad registration by user ID.
        
        Args:
            user_id: The user ID to search for.
            
        Returns:
            Dictionary containing user registration data or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ads_register WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'user_id': row[0],
                    'list_ad_ids': self._deserialize_list(row[1]),
                    'list_titles': self._deserialize_list(row[2])
                }
            return None

    def update_user_registration(self, user_id: int, ad_ids: List[int], titles: List[str]) -> int:
        """
        Update an existing user ad registration.
        
        Args:
            user_id: The user ID to update.
            ad_ids: New list of ad IDs.
            titles: New list of ad titles.
            
        Returns:
            Number of rows affected.
            
        Raises:
            ValueError: If ad_ids and titles lists have different lengths.
        """
        if len(ad_ids) != len(titles):
            raise ValueError("ad_ids and titles lists must have the same length")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ads_register
                SET list_ad_ids = ?, list_titles = ?
                WHERE user_id = ?
            """, (self._serialize_list(ad_ids), self._serialize_list(titles), user_id))
            conn.commit()
            return cursor.rowcount

    def add_ad_to_user(self, user_id: int, ad_id: int, title: str) -> bool:
        """
        Add a single ad to an existing user registration.
        
        Args:
            user_id: The user ID to update.
            ad_id: The ad ID to add.
            title: The ad title to add.
            
        Returns:
            True if ad was added successfully, False otherwise.
        """
        try:
            # Get current registration
            current_registration = self.read_user_registration(user_id)
            
            if current_registration:
                # Add to existing lists
                ad_ids = current_registration['list_ad_ids']
                titles = current_registration['list_titles']
                
                # Check if ad_id already exists
                if ad_id not in ad_ids:
                    ad_ids.append(ad_id)
                    titles.append(title)
                    return self.update_user_registration(user_id, ad_ids, titles) > 0
                return True  # Ad already exists
            else:
                # Create new registration
                return self.create_user_registration(user_id, [ad_id], [title])
        except Exception:
            return False

    def remove_ad_from_user(self, user_id: int, ad_id: int) -> bool:
        """
        Remove a single ad from a user registration.
        
        Args:
            user_id: The user ID to update.
            ad_id: The ad ID to remove.
            
        Returns:
            True if ad was removed successfully, False otherwise.
        """
        try:
            current_registration = self.read_user_registration(user_id)
            
            if current_registration:
                ad_ids = current_registration['list_ad_ids']
                titles = current_registration['list_titles']
                
                # Find and remove the ad
                if ad_id in ad_ids:
                    index = ad_ids.index(ad_id)
                    ad_ids.pop(index)
                    titles.pop(index)
                    return self.update_user_registration(user_id, ad_ids, titles) > 0
                
            return False
        except Exception:
            return False

    def delete_user_registration(self, user_id: int) -> int:
        """
        Delete a user registration by user ID.
        
        Args:
            user_id: The user ID to delete.
            
        Returns:
            Number of rows affected.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ads_register WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount

    def get_all_registrations(self) -> List[Dict[str, Any]]:
        """
        Get all user registrations.
        
        Returns:
            List of dictionaries containing all user registration data.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ads_register")
            rows = cursor.fetchall()
            
            return [
                {
                    'user_id': row[0],
                    'list_ad_ids': self._deserialize_list(row[1]),
                    'list_titles': self._deserialize_list(row[2])
                }
                for row in rows
            ]

    def get_users_by_ad_id(self, ad_id: int) -> List[int]:
        """
        Get all user IDs that have registered for a specific ad.
        
        Args:
            ad_id: The ad ID to search for.
            
        Returns:
            List of user IDs that have registered for the specified ad.
        """
        user_ids = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, list_ad_ids FROM ads_register")
            rows = cursor.fetchall()
            
            for row in rows:
                ad_ids = self._deserialize_list(row[1])
                if ad_id in ad_ids:
                    user_ids.append(row[0])
                    
        return user_ids

    def flush(self) -> None:
        """
        Remove all data from the ads_register table.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ads_register")
            conn.commit()
            print("All data has been removed from the ads_register table.")
