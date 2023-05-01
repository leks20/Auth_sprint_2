from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, ssl_context=("ssl/cert.pem", "ssl/key.pem"))
