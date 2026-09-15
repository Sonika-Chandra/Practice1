
from flask import Flask
from db import connect_db

app = Flask(__name__)

# Connect to MongoDB
client = connect_db()

# Select database
db = client["mydatabase"]

@app.route("/")
def home():
    return "Flask server is running!"

if __name__ == "__main__":
    app.run(debug=True)
