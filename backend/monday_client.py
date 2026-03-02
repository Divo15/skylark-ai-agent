import requests
import os
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")

HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json",
    "API-Version": "2024-01"
}

def fetch_board_items(board_id: str) -> list:
    """Fetch all items from a monday.com board - LIVE API CALL"""
    
    query = """
    query ($boardId: ID!) {
      boards(ids: [$boardId]) {
        name
        items_page(limit: 500) {
          items {
            name
            column_values {
              column { title }
              text
            }
          }
        }
      }
    }
    """
    
    try:
        response = requests.post(
            "https://api.monday.com/v2",
            headers=HEADERS,
            json={
                "query": query,
                "variables": {"boardId": board_id}
            },
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if "errors" in data:
            print(f"monday.com API error: {data['errors']}")
            return []
        
        items = data["data"]["boards"][0]["items_page"]["items"]
        
        # Convert to flat dictionaries
        result = []
        for item in items:
            row = {"name": item["name"]}
            for col in item["column_values"]:
                row[col["column"]["title"]] = col["text"]
            result.append(row)
        
        print(f"Fetched {len(result)} items from board {board_id}")
        return result
    
    except requests.exceptions.Timeout:
        print("monday.com API timed out")
        return []
    except requests.exceptions.RequestException as e:
        print(f"monday.com API request failed: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching board: {e}")
        return []

def get_work_orders() -> list:
    """Fetch all work orders from monday.com"""
    print("Calling monday.com API - Work Orders board...")
    return fetch_board_items(WORK_ORDERS_BOARD_ID)

def get_deals() -> list:
    """Fetch all deals from monday.com"""
    print("Calling monday.com API - Deals board...")
    return fetch_board_items(DEALS_BOARD_ID)