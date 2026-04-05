"""
Production entry point for gunicorn.
Usage: gunicorn wsgi:app
"""
from app import app

if __name__ == '__main__':
    app.run()
