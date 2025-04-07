from flask import Flask, render_template
import wrangle_data
import plotly
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Get list of figure dicts from your wrangle_data.py
    figures = wrangle_data.return_figures()

    # Convert Plotly dicts to JSON for embedding in HTML
    ids = [f'chart-{i}' for i, _ in enumerate(figures)]
    chart_json = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    # Pass figure JSON and chart IDs to the template
    return render_template(
        'index.html',
        ids=ids,
        chartJSON=chart_json
    )

if __name__ == '__main__':
    app.run(debug=True)
