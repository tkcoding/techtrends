import sqlite3

from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging

# Count all database connections
# Define the Flask application
app = Flask(__name__)
app.config['connection_count'] = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    # print(app.config['connection_count'])
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    app.config['connection_count'] = app.config['connection_count'] + 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    connection.close()
    return post




# Define the main route of the web application
@app.route("/")
def index():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    return render_template("index.html", posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.debug('Article with id "{id}" does not exist!'.format(id=post_id))
        return render_template("404.html"), 404
    else:
        logging.debug('Article "{title}" retrieved!'.format(title=post["title"]))
        return render_template("post.html", post=post)


# Define the About Us page
@app.route("/about")
def about():
    logging.debug("About page rendered!")
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            connection = get_db_connection()
            connection.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
            )
            connection.commit()
            connection.close()
            logging.debug('Article "{title}" created!'.format(title=title))
            return redirect(url_for("index"))
    return render_template("create.html")


# Define healthz endpoint
@app.route("/healthz")
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute("SELECT * FROM posts")
        connection.close()
        return {"result": "OK - healthy"}
    except Exception:
        return {"result": "ERROR - unhealthy"}, 500


# Define metrics endpoint
@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    post_count = len(posts)
    data = {"db_connection_count": app.config['connection_count'], "post_count": post_count}
    return data


# start the application on port 3111
if __name__ == "__main__":
    ## stream logs to a file
    logname = "app.log"
    logging.basicConfig(
        filename=logname,
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    app.run(host="0.0.0.0", port="3111")
