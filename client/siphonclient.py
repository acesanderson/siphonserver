import requests
import json


class SiphonClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")

    def get_status(self):
        """Get server status"""
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = SiphonClient()
    try:
        status = client.get_status()
        print(json.dumps(status, indent=2))
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server at http://localhost:8080")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
