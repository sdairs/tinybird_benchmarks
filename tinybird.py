import stat
import requests
from typing import Dict, Any
from dataclasses import dataclass
import datetime
from enum import Enum

class QueryStatus(Enum):
    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    FAIL = "FAIL"

@dataclass
class Statistics:
    elapsed: float
    rows_read: int
    bytes_read: int

@dataclass
class QueryResult:
    start_time: datetime.datetime
    end_time: datetime.datetime
    status: QueryStatus
    statistics: Statistics

class TinybirdClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.tinybird.co/v0/sql"
        self.headers = {
            "Authorization": f"Bearer {token}"
        }
    
    def query(self, sql: str) -> QueryResult:
        """
        Execute a query using the Query API
        
        Args:
            sql: SQL query to execute
            
        Returns:
            QueryResult containing timing and result data
        """
        start_time = datetime.datetime.now(datetime.timezone.utc)
        
        try:
            response = requests.get(
                self.base_url, 
                headers=self.headers,
                params={"q": sql + " FORMAT JSON"}
            )
            
            end_time = datetime.datetime.now(datetime.timezone.utc)
            
            if response.status_code == 408:  # Timeout
                return QueryResult(
                    start_time=start_time,
                    end_time=end_time,
                    status=QueryStatus.TIMEOUT,
                    statistics=Statistics(
                        elapsed=10,
                        rows_read=0,
                        bytes_read=0
                    )
                )
                
            response.raise_for_status()
            result = response.json()
            
            return QueryResult(
                start_time=start_time,
                end_time=end_time,
                status=QueryStatus.SUCCESS,
                statistics=Statistics(
                    elapsed=result.get("statistics", {}).get("elapsed", 0),
                    rows_read=result.get("statistics", {}).get("rows_read", 0),
                    bytes_read=result.get("statistics", {}).get("bytes_read", 0)
                )
            )
            
        except requests.exceptions.RequestException as e:
            end_time = datetime.datetime.now(datetime.timezone.utc)
            return QueryResult(
                start_time=start_time,
                end_time=end_time,
                status=QueryStatus.FAIL,
                statistics=Statistics(
                    elapsed=0,
                    rows_read=0,
                    bytes_read=0
                )
            )
