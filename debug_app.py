#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Flask to show debug info
os.environ['FLASK_DEBUG'] = '1'

from app import app

# Enable debug mode
app.config['DEBUG'] = True

if __name__ == '__main__':
    print("Starting Flask app in debug mode...")
    app.run(host='127.0.0.1', port=5005, debug=True)