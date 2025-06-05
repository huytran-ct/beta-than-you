import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class PageviewByHour:
    def __init__(self, db_path: str = "hackathon.db"):
        self.db_path = db_path
    
    def get_pageview(self, ad_type: str, category: int, city_id: int,  district_id: int) -> List[Dict]:
        """Get top pages for a specific hour."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT city_name, district_name, hour, pageview
                    FROM pageview_by_hour 
                    WHERE ad_type = ?
                    AND category = ?
                    AND city_id = ?
                    AND district_id = ?
                    ORDER BY hour DESC
                ''', (ad_type, category, city_id, district_id))
                
                columns = ['city_name', 'district_name', 'hour', 'pageview']
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting top pages by hour: {e}")
            return []


class PageviewByWeek:
    def __init__(self, db_path: str = "hackathon.db"):
        self.db_path = db_path

    def get_pageview(self, ad_type: str, category: int, city_id: int,  district_id: int) -> List[Dict]:
        """Get top pages for a specific hour."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT city_name, district_name, weekday, pageview
                    FROM pageview_by_week 
                    WHERE ad_type = ?
                    AND category = ?
                    AND city_id = ?
                    AND district_id = ?
                    ORDER BY weekday DESC
                ''', (ad_type, category, city_id, district_id))
                
                columns = ['city_name', 'district_name', 'weekday', 'pageview']
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting top pages by week: {e}")
            return []
