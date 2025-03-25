from flask import Flask, render_template
import os
from app import app  # Import Flask instance from app.py

# Serve the HTML template
@app.route('/')
def index():
    return render_template('main.html')  # Ensure main.html is inside the "templates" folder

if __name__ == "__main__":
    # Create uploads directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads"), exist_ok=True)
    app.run(debug=True)
