import os
import requests
import pandas as pd

class Genius:
    BASE_URL = "https://api.genius.com"

    def __init__(self, access_token):
        if access_token == "access_token":
            access_token = os.getenv("GENIUS_TOKEN", access_token)

        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def _get(self, path, params=None):
        url = f"{self.BASE_URL}{path}"
        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    def get_artist(self, search_term):
        search_data = self._get("/search", params={"q": search_term})
        hits = search_data.get("response", {}).get("hits", [])
        if not hits:
            raise ValueError(f"No results found for: {search_term}")

        artist_id = hits[0]["result"]["primary_artist"]["id"]
        artist_data = self._get(f"/artists/{artist_id}")
        return artist_data["response"]["artist"]
    def get_artists(self, search_terms):
        rows = []
        for term in search_terms:
            artist = self.get_artist(term)
            rows.append({
                "search_term": term,
                "artist_name": artist.get("name"),
                "artist_id": artist.get("id"),
                "followers_count": artist.get("followers_count")
            })
        return pd.DataFrame(rows)