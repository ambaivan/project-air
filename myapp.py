from flask import Flask, render_template
from wrangling_scripts.wrangle_data import return_figures
import plotly
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Get list of figure dicts from your wrangle_data.py
    figures = return_figures()

    # Convert Plotly dicts to JSON for embedding in HTML
    ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]
    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    # Pass figure JSON and chart IDs to the template
    return render_template(
        'index.html',
        ids=ids,
        figuresJSON=figuresJSON
    )

if __name__ == '__main__':
    app.run(debug=True)
