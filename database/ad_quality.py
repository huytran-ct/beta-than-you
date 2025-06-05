import sqlite3
from typing import Dict, List, Optional, Tuple
import json
from utils.utils import convert_json_format

class AdQualityDatabase:
    def __init__(self, db_path: str = "hackathon.db"):
        self.db_path = db_path
    
    def get_ad_quality_score(self, ad_id: str) -> Optional[Dict]:
        """Get the quality score dictionary for a specific ad."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT ad_quality_score FROM ad_quality WHERE ad_id = ?',
                    (ad_id,)
                )
                result = cursor.fetchone()
                if result:
                    return json.loads(convert_json_format(result[0]))
                return None
        except Exception as e:
            print(f"Error getting ad quality score: {e}")
            return None