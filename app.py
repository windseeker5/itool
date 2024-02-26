from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('TheMovieDB.db')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        title_filter = request.form.get('title_filter', '')
        genres = [request.form.get('genre_action', '1'),
                  request.form.get('genre_adventure', '1'),
                  request.form.get('genre_animation', '1')]
        # Add more genres as needed
    else:
        title_filter = request.args.get('title_filter', '')
        genres = [request.args.get('genre_action', '1'),
                  request.args.get('genre_adventure', '1'),
                  request.args.get('genre_animation', '1')]
        # Add more genres as needed

    # Define your query
    query = """
    SELECT id,
        poster_img,
        original_language,
        original_title,
        overview,
        popularity,
        release_date,
        vote_average,
        vote_count,
        budget,
        production_companies,
        revenue,
        runtime,
        tagline,
        genres
    FROM movies
    WHERE original_language IN ('en', 'fr')
    AND genres NOT LIKE '%Music%'
    AND genres NOT LIKE '%Documentary%'
    AND genres NOT LIKE '%Animation%'
    """

    if title_filter:
        query += f"AND original_title LIKE '%{title_filter}%' "


    # Build genre filter
    genre_conditions = []
    if '1' in genres:
        genre_conditions.append("genres LIKE '%Action%'")
    if '2' in genres:
        genre_conditions.append("genres LIKE '%Adventure%'")
    if '3' in genres:
        genre_conditions.append("genres LIKE '%Animation%'")
    # Add more genres as needed

    if genre_conditions:
        query += "AND (" + " OR ".join(genre_conditions) + ") "

    query += "ORDER BY vote_average DESC, release_date DESC;"

    cursor.execute(query)
    movies = cursor.fetchall()

    conn.close()

    return render_template('index.html', movies=movies)









if __name__ == '__main__':
    app.run(debug=True)
