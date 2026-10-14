import os

from flask import Flask

app = Flask(__name__)


# https://hanamaru8700.com/uvblog/src/flask_app/
# $ curl -LsS https://hanamaru8700.com/uvblog/src/flask_app/
#   /virtual/hanacore/public_html/hanamaru8700.com/uvblog/src/flask_app,
#   Hello from Flask inside CORESERVER with uv!
@app.route("/")
def hello():
    current_dir = os.path.dirname(__file__)
    print(f"{current_dir},")
    print("Hello from Flask inside CORESERVER with uv!")
    return ""


# https://hanamaru8700.com/uvblog/src/flask_app/index.cgi/user/gare
# $ curl -LsS https://hanamaru8700.com/uvblog/src/flask_app/user/lio
#   Hello, lio!(hanaflask-pro) 
@app.route("/user/<name>")
def user(name):
    return f"Hello, {name}!"
