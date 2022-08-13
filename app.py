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
    dcc.Graph(id='chromatogram'),
    dcc.Graph(id='mass-spectrum')
])

chromatogram = None


def string_to_chromatogram(contents):
    global chromatogram
    content_type, content_string = contents.split(',')
    try:
        with tempfile.NamedTemporaryFile(mode='w+b', suffix=".CDF") as f:
            f.write(base64.b64decode(content_string))
            f.seek(0)
            chromatogram = Chromatogram(f.name)
    except Exception as e:
        print(e)



@app.callback(Output('mass-spectrum', 'figure'),
              Input('chromatogram', 'clickData'),
              prevent_initial_call=True)
def update_mass_spectrum(click):
    """
{
   "points":[
      {
         "curveNumber":0,
         "pointNumber":1203,
         "pointIndex":1203,
         "x":13.488432884216309,
         "y":422233.84375,
         "bbox":{
            "x0":715.83,
            "x1":717.83,
            "y0":245.05,
            "y1":247.05
         }
      }
   ]
}
    """
    if click:
        scan_number = int(click['points'][0]['x'])
        mass_spectrum = chromatogram.get_raw_MS(scan_number)
        max_mass = int(max(mass_spectrum.masses)) + 1
        ms_info = mass_spectrum.get_MS()
        ms_info_rounded = {int(round(m,0)): ms_info[m] for m in ms_info}
        mz = [i for i in range(max_mass)]
        a = [ms_info_rounded[i] if i in ms_info_rounded else 0 for i in range(max_mass)]

        #fig = px.bar(x=mz, y=a, title='Mass Spectrum', color='#6666ff')
        df = pd.DataFrame(data={'mz': mz, 'a': a})
        fig = px.bar(df, x='mz', y='a', title='Mass Spectrum')
        fig.update_layout(transition_duration=500)
        return fig

@app.callback(Output('chromatogram', 'figure'),
              Input('upload-data', 'contents'),
              prevent_initial_call=True)
def update_chromatogram(contents):
    if contents is not None:
        try:
            string_to_chromatogram(contents)
            if(chromatogram):
                df = pd.DataFrame({'time': [chromatogram.times[i]/60 for i in range(
                    chromatogram.maxscan)], 'Intensity': chromatogram.ion_current})
                fig = px.line(df, x='time', y='Intensity')
                fig.update_layout(transition_duration=500)
                return fig
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
