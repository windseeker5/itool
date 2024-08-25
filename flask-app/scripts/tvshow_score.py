import requests
import sqlite3
import time

# Function to create the SQLite database and table
def create_db():
    conn = sqlite3.connect('tv_shows_score.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tv_shows (
            id INTEGER PRIMARY KEY,
            name TEXT,
            overview TEXT,
            popularity REAL,
            vote_average REAL,
            vote_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(tv_shows):
    conn = sqlite3.connect('tv_shows_score.db')
    c = conn.cursor()
    for show in tv_shows:
        c.execute('''
            INSERT OR IGNORE INTO tv_shows (id, name, overview, popularity, vote_average, vote_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (show['id'], show['name'], show['overview'], show['popularity'], show['vote_average'], show['vote_count']))
    conn.commit()
    conn.close()

# Function to fetch data from the API and store it in the database
def fetch_and_store_tv_shows():
    url = "https://api.themoviedb.org/3/tv/popular"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkYTgzNTM2NzUyN2RiNmVlMTkyNzE0Y2M4Mzg0OWUwMiIsInN1YiI6IjY1YzdiZDQ0YjZjZmYxMDE2NGE0ZjY3MiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.gNjAz5H6uYtoO3YT80t82HDVOdnCr4hkVnmuxcykFpQ"
    }

    for page in range(1, 101):  # Loop through pages 1 to 100
        response = requests.get(url, headers=headers, params={"language": "en-US", "page": page})
        if response.status_code == 200:
            tv_shows = response.json().get('results', [])
            insert_data(tv_shows)
        else:
            print(f"Failed to fetch page {page}: {response.status_code}")
        time.sleep(1)  # Sleep to avoid hitting rate limits

# Main function
def main():
    create_db()  # Create the database and table
    fetch_and_store_tv_shows()  # Fetch data and store it in the database

if __name__ == "__main__":
    main()
