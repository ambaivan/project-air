from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")  # or whatever HTML you have

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
