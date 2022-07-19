import sqlite3, functools, logging, sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Def decorator to count total amount of connections to the database
def conn_counter(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        app.config['CONN_NUM'] += 1
        return func(*args, **kw)
    return wrapper

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
@conn_counter
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['CONN_NUM'] = 0
app.config['DEBUG'] = True

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('404')
        return render_template('404.html'), 404
    else:
        app.logger.info(dict(post).get('title'))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# Return healthy json
@app.route('/healthz', methods=('GET', 'POST'))
def healthz():
    return jsonify({'result': 'OK - Healthy'})

@app.route('/metrics', methods=('GET', 'POST'))
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('select count(*) as conn_num from posts where true').fetchone()
    connection.close()
    return jsonify({'db_connection_count': app.config['CONN_NUM'],
        'post_count': dict(post_count).get('conn_num')})

# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(
            stream=sys.stdout,
            format='%(levelname)s: %(name)s: %(asctime)s - %(message)s',
            level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
