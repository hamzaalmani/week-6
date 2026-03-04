import requests
import pandas as pd


class Genius:
    """A simple wrapper for the Genius API."""

    BASE_URL = "http://api.genius.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request to the Genius API and return the JSON response."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def _search(self, search_term: str, per_page: int = 5) -> list:
        """Return a list of hits for search_term from the Genius search endpoint."""
        data = self._get("/search", params={"q": search_term, "per_page": per_page})
        return data["response"]["hits"]

    def _extract_primary_artist_id(self, hits: list) -> int:
        """Return the primary-artist ID from the first hit."""
        return hits[0]["result"]["primary_artist"]["id"]

    # ------------------------------------------------------------------ #
    # Exercise 2
    # ------------------------------------------------------------------ #

    def get_artist(self, search_term: str) -> dict:
        """
        Search Genius for search_term and return the JSON dictionary
        for the most-likely primary artist found in the first hit.
        """
        hits = self._search(search_term)
        artist_id = self._extract_primary_artist_id(hits)
        data = self._get(f"/artists/{artist_id}")
        return data["response"]

    # ------------------------------------------------------------------ #
    # Exercise 3
    # ------------------------------------------------------------------ #

    def get_artists(self, search_terms: list) -> pd.DataFrame:
        """
        Call get_artist() for each term in search_terms and return
        a DataFrame with one row per artist.
        """
        rows = []
        for term in search_terms:
            try:
                response = self.get_artist(term)
                artist = response.get("artist", {})
                rows.append({
                    "search_term": term,
                    "artist_name": artist.get("name"),
                    "artist_id": artist.get("id"),
                    "followers_count": artist.get("followers_count"),
                })
            except Exception:
                rows.append({
                    "search_term": term,
                    "artist_name": None,
                    "artist_id": None,
                    "followers_count": None,
                })
        return pd.DataFrame(
            rows,
            columns=["search_term", "artist_name", "artist_id", "followers_count"]
        )
    
    # ------------------------------------------------------------------ #
    # Bonus Question
    # ------------------------------------------------------------------ #

def _fetch_artist_worker(args: tuple) -> dict:
    """Multiprocessing worker — must be top-level for pickling."""
    search_term, access_token = args
    genius = Genius(access_token=access_token)
    try:
        response = genius.get_artist(search_term)
        artist = response.get("artist", {})
        return {
            "search_term": search_term,
            "artist_name": artist.get("name"),
            "artist_id": artist.get("id"),
            "followers_count": artist.get("followers_count"),
        }
    except Exception:
        return {
            "search_term": search_term,
            "artist_name": None,
            "artist_id": None,
            "followers_count": None,
        }


if __name__ == "__main__":
    from multiprocessing import Pool

    ACCESS_TOKEN = "m01l5yNjuQeHMI13Kp9j-ZbbpPk6wWCBDgmxtGjlG8eoaB8DxJjXO7XG7Vd1TmFw"

    # Step 1: load artists from txt file
    with open("artists.txt", "r") as f:
        search_terms = [line.strip() for line in f if line.strip()]

    # Step 2: fetch with multiprocessing
    args = [(term, ACCESS_TOKEN) for term in search_terms]
    with Pool(8) as p:
        results = p.map(_fetch_artist_worker, args)

    # Step 3: save to CSV
    df = pd.DataFrame(results, columns=["search_term", "artist_name", "artist_id", "followers_count"])
    df.to_csv("artists_data.csv", index=False)
    print(f"Saved {len(df)} rows to artists_data.csv")

