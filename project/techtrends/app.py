import sqlite3, functools, logging, sys, os

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


CONN_NUM = 0

# Def decorator to count total amount of connections to the database
def conn_counter(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        global CONN_NUM
        CONN_NUM += 1
        return func(*args, **kw)
    return wrapper

# Function to get a database connection.
# This function connects to database with the name `database.db`
@conn_counter
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to close db connection and reduce counter
def close_connection(conn_obj):
    global CONN_NUM
    conn_obj.close
    CONN_NUM -= 1

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    #connection.close()
    close_connection(connection)
    return post

# Define the Flask application
app = Flask(__name__)
app.config['DEBUG'] = True

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    #connection.close()
    close_connection(connection)
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error('Non-existing post')
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
            #connection.close()
            close_connection(connection)
            return redirect(url_for('index'))

    return render_template('create.html')

# Return healthy json
@app.route('/healthz', methods=('GET', 'POST'))
def healthz():
    #try:
    #    with open('filepath')
    #    return {OK}
    #except FileNotFoundError:
    #    return {Error}, 500
    
    db_file = 'database.db'
    if os.path.exists(db_file):
        return jsonify({'result': 'OK - Healthy'})
    else:
        return jsonify({'result': 'Error - Missing {}'.format(db_file)}), 500

@app.route('/metrics', methods=('GET', 'POST'))
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('select count(*) as post_count from posts where true').fetchone()
    curr_conn_num = CONN_NUM
    #connection.close()
    close_connection(connection)
    return jsonify({'db_connection_count': curr_conn_num,
        'post_count': dict(post_count).get('post_count')})


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
    )
    app.run(host='0.0.0.0', port='3111')
