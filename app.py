import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import tempfile

import plotly.express as px
import pandas as pd

from algorithm.chromatogram import Chromatogram

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),
    dcc.Graph(id='chromatogram')
])

@app.callback(Output('chromatogram', 'figure'),
              Input('upload-data', 'contents'), prevent_initial_call=True)
def update_chromatogram(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        try:
            with tempfile.NamedTemporaryFile(mode='w+b', suffix=".CDF") as f:
                f.write(base64.b64decode(content_string))
                f.seek(0)
                print(f.name)
                chromatogram = Chromatogram(f.name)
                df = pd.DataFrame({'time': [chromatogram.times[i]/60 for i in range(
                    chromatogram.maxscan)], 'Intensity': chromatogram.ion_current})
                fig = px.line(df, x='time', y='Intensity')
                fig.update_layout(transition_duration=500)
                return fig
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8000)