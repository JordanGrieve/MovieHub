from flask import Flask, render_template, session, request, redirect, url_for, flash
import sqlite3
import secrets
import os
import urllib.parse 
from urllib.parse import unquote

# Setting a key for the users
secret_key = secrets.token_hex(32)

app = Flask(__name__)

port = int(os.environ.get("PORT", 8080))

app.secret_key = secret_key

# Connecting to the movies database
def get_database_connection():
   # return sqlite3.connect('databases/movies.db')
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_movies_path = os.path.join(base_dir, 'databases', 'movies.db')
    return sqlite3.connect(db_movies_path)

def get_user_database_connection(): 
   # return sqlite3.connect('databases/users_data.db')
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_users_path = os.path.join(base_dir, 'databases', 'users.db')
    return sqlite3.connect(db_users_path)

#def get_user_database_connection():
   # try:
   #     connection = sqlite3.connect('databases/users_data.db')
   #     print("Connection:", connection)
   #     return connection
   # except sqlite3.Error as e:
    #    print(f"SQLite error while connecting to user database: {e}")
   #     raise 
   # except Exception as e:
    #    print(f"Error connecting to user database: {e}")
     #   raise


def execute_query(query, params=(), database='users_data'):
    if database == 'users_data':
        connection = get_user_database_connection()
    elif database == 'movies':
        connection = get_database_connection()
    else:
        connection = None

    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {query} with params: {params}")
        print(f"Error details: {e}")
        result = []
    finally:
        cursor.close()
        connection.close()
    return result


# Function to get all the movies in the database
def get_all_movies():
    query = 'SELECT * FROM Movies'
    return execute_query(query)

# Function to get the all movies
def get_every_movies():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT MovieID, Title, Image FROM Movies')
    every_movies = cursor.fetchall()

    cursor.close()
    connection.close()

    return every_movies

# Movies Page
# Crime Movies
def get_crime_movies():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT MovieID, Title, Image FROM Movies WHERE Genre = "Crime"') # All movies that have a genre of Crime
    crime_movies = cursor.fetchall()

    cursor.close()
    connection.close()

    return crime_movies

# Drama Movies
def get_drama_movies():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT MovieID, Title, Image FROM Movies WHERE Genre = "Drama"') # All movies that have a genre of Drama
    drama_movies = cursor.fetchall()

    cursor.close()
    connection.close()

    return drama_movies

# Sci-Fi Movies
def get_SciFi_movies():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT MovieID, Title, Image FROM Movies WHERE Genre = "Sci-Fi"') # All movies that have a genre of Sci-FI
    SciFi_movies = cursor.fetchall()

    cursor.close()
    connection.close()

    return SciFi_movies

# Fantasy Movies
def get_fantasy_movies():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT MovieID, Title, Image FROM Movies WHERE Genre = "Fantasy"') # All movies that have a genre of Fantasy
    fantasy_movies = cursor.fetchall()

    cursor.close()
    connection.close()

    return fantasy_movies
# Function to get the newest movies
def get_newest_movies(limit=5): # Setting to only draw the first 5 movies
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT MovieID, Title, Image FROM Movies ORDER BY yearReleased DESC LIMIT ?', (limit,))
    newest_movies = cursor.fetchall()

    cursor.close()
    connection.close()

    return newest_movies

# Function to get the best movies
def get_topRate_movies():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT MovieID, Title, Image, Description FROM Movies WHERE topRate = 1') # Looking for topRate = 1 in the database
    topRate_movies = cursor.fetchall()

    cursor.close()
    connection.close()

    return topRate_movies

# Function to get the classic movies
def get_classic_movies():
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT MovieID, Title, Image FROM Movies WHERE Classic = 1')
        classic_movies = cursor.fetchall()

        return classic_movies

    except Exception as e:
        print("Error fetching classic movies:", str(e))
        return None

    finally:
        cursor.close()
        connection.close()

# Get Movie Reviews from users
def get_movie_reviews(movie_id):
    query = 'SELECT UserID, ReviewText FROM Reviews WHERE MovieID = ?'
    connection = get_user_database_connection()
    cursor = connection.cursor()
    cursor.execute(query, (movie_id,))
    movie_reviews = cursor.fetchall()
    cursor.close()
    connection.close()
    return movie_reviews

# Setting users favorites - 2 foreign keys 
def add_to_favorites_db(user_id, movie_id):
    connection = get_user_database_connection()
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Favorites (UserID, MovieID) VALUES (?, ?)', (user_id, movie_id))

    connection.commit()
    connection.close()

# Remove users favorites 
def remove_from_favorites_db(user_id, movie_id):
    connection = get_user_database_connection()
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Favorites WHERE UserID = ? AND MovieID = ?', (user_id, movie_id))

    connection.commit()
    connection.close()


@app.route('/add_to_favorites/<int:movie_id>', methods=['POST'])
def add_to_favorites(movie_id):
    user_id = session.get('user_id')

    if user_id:
        # Check if the movie is already in favorites
        is_favorite = is_movie_in_favorites(user_id, movie_id)

        if is_favorite:
            # Movie is already in favorites, remove it
            remove_from_favorites_db(user_id, movie_id)
            flash('Movie removed from favorites!', 'success')
        else:
            # Movie is not in favorites, add it
            add_to_favorites_db(user_id, movie_id)
            flash('Movie added to favorites!', 'success')
    else:
        flash('You must be logged in to add movies to favorites.', 'error')

    return redirect(url_for('root'))


def is_movie_in_favorites(user_id, movie_id):
    connection = get_user_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Favorites WHERE UserID = ? AND MovieID = ?', (user_id, movie_id))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None




# Movie Details Page
@app.route('/movie_detail/<int:movie_id>/<path:movie_title>', methods=['GET', 'POST'])
def movie_detail(movie_id, movie_title):
    decoded_title = unquote(movie_title)
    
    if request.method == 'POST':
        review_text = request.form.get('review_text')
        user_id = session.get('user')

        if user_id:
            # Save the review to the database
            save_review(user_id, movie_id, review_text)
        else:
            flash('You must be logged in to submit a review.', 'error')

    movie_reviews = get_movie_reviews(movie_id)
    movie_details = get_movie_details_by_id_and_title(movie_id, decoded_title)
    topRate_movies = get_topRate_movies()

    return render_template('movie_detail.html', movie_details=movie_details, topRate_movies=topRate_movies, reviews=movie_reviews,)

# Function to save a review to the database
def save_review(user_id, movie_id, review_text):
    connection = get_user_database_connection()
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Reviews (UserID, MovieID, ReviewText) VALUES (?, ?, ?)',
                   (user_id, movie_id, review_text))

    connection.commit()
    connection.close()



def get_movie_details_by_id_and_title(movie_id, movie_title):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Movies WHERE MovieID = ?', (movie_id,))
    movie_details = cursor.fetchone()

    cursor.close()
    connection.close()

    if movie_details is not None:
        return {
            'movieID': movie_details[0],
            'Title': movie_details[1],
            'Description': movie_details[2],
            'Actors': movie_details[3],
            'Director': movie_details[4],
            'yearRelease': movie_details[5],
            'Duration': movie_details[6],
            'Genre': movie_details[7],
            'Image': movie_details[8],
        }
    else:
        return None

# Index Page
@app.route("/")
def root():
    movies = get_all_movies()
    newest_movies = get_newest_movies()
    classic_movies = get_classic_movies()
    topRate_movies = get_topRate_movies()
    return render_template('index.html', movies=movies, newest_movies=newest_movies, classic_movies=classic_movies, topRate_movies=topRate_movies)

# Movies Page
@app.route('/movies')
def movies():
    movies = get_all_movies()
    newest_movies = get_newest_movies()
    topRate_movies = get_topRate_movies()
    every_movies = get_every_movies()
    crime_movies = get_crime_movies()
    drama_movies = get_drama_movies()
    SciFi_movies = get_SciFi_movies()
    fantasy_movies = get_fantasy_movies()
    return render_template('movies.html', movies=movies, newest_movies=newest_movies, topRate_movies=topRate_movies, every_movies=every_movies, crime_movies=crime_movies, drama_movies=drama_movies, SciFi_movies=SciFi_movies, fantasy_movies=fantasy_movies)

# About Page
@app.route('/about')
def about():
    movies = get_all_movies()
    return render_template('about.html', movies=movies)

# FAQ Page
@app.route('/faq')
def faq():
    movies = get_all_movies()
    return render_template('faq.html', movies=movies)


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        connection = sqlite3.connect('databases/users_data.db')
        cursor = connection.cursor()

        username = request.form['username']
        password = request.form['password']

        query = "SELECT UserID, username, password FROM USERS WHERE username=? and password=?"
        cursor.execute(query, (username, password))

        results = cursor.fetchall()

        if len(results) == 0:
            print("wrong details - try again.")
            flash('Invalid username or password. Please try again.', 'error')
            return render_template('login.html')  # Return to the login page with an error message
        else:
            user_id, username, _ = results[0]  # Assuming the result structure is (UserID, Username, Password)
            # Set the user_id and username in the session upon successful login
            session['user_id'] = user_id
            session['user'] = username
            return redirect(url_for('root'))

    return render_template('login.html')


# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.pop('user', None)

    # Redirect to the root (index)
    return redirect(url_for('root'))


def get_user_favorite_movies(user_id):
    connection = get_user_database_connection()

    cursor = connection.cursor()
    try:
        cursor.execute('SELECT MovieID FROM Favorites WHERE UserID = ?', (user_id,))
        result = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error executing query: SELECT MovieID FROM Favorites WHERE UserID = ? with params: {user_id}")
        print(f"Error details: {e}")
        result = []
    finally:
        cursor.close()

    return result


def get_movie_details_by_id(movie_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT * FROM Movies WHERE MovieID = ?', (int(movie_id),))
        movie_details = cursor.fetchone()
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        movie_details = None
    finally:
        cursor.close()
        connection.close()

    if movie_details is not None:
        return {
            'movieID': movie_details[0],
            'Title': movie_details[1],
            'Description': movie_details[2],
            'Actors': movie_details[3],
            'Director': movie_details[4],
            'yearRelease': movie_details[5],
            'Duration': movie_details[6],
            'Genre': movie_details[7],
            'Image': movie_details[8],
        }
    else:
        return None

# User's Account Page
@app.route('/account')
def account():
    user_id = session.get('user_id')
    topRate_movies = get_topRate_movies()

    if user_id:
        favorite_movie_ids = get_user_favorite_movies(user_id)
        favorite_movies_count = len(favorite_movie_ids)

        return render_template('account.html', topRate_movies=topRate_movies, favorite_movie_ids=favorite_movie_ids, favorite_movies_count=favorite_movies_count, get_movie_details_by_id=get_movie_details_by_id)
    
    return render_template('account.html', topRate_movies=topRate_movies, get_movie_details_by_id=get_movie_details_by_id)




# Create a User
def create_user(username, password):
    connection = sqlite3.connect('databases/users_data.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (username, password))
    connection.commit()
    connection.close()

#Sign Up Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        if user_exists(username):
            flash('Username already exists. Please choose another.', 'error')
        else:
            # Create a new user if not
            create_user(username, password)
            flash('Registration successful! You can now log in.', 'success')

    return render_template('signup.html')

    return render_template('signup.html')


def user_exists(username):
    connection = sqlite3.connect('databases/users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT username FROM Users WHERE username = ?', (username,))
    result = cursor.fetchall()
    connection.close()
    return len(result) > 0


def add_review(user_id, movie_id, rating, ReviewText):
    query = 'INSERT INTO Reviews (UserID, MovieID, Rating, ReviewText) VALUES (?, ?, ?, ?)'
    execute_query(query, (user_id, movie_id, rating, ReviewText), database='users')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
