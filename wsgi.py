from app import app

# WSGI entrypoint for production servers.
# Many WSGI servers expect a module named `wsgi` exposing the Flask `app`.

if __name__ == "__main__":
    # For local testing you can run: python wsgi.py
    # This will use Waitress if installed.
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=8000)
    except Exception:
        # Fallback to Flask's dev server if Waitress isn't available.
        app.run(host="0.0.0.0", port=8000)
