import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import datetime
import trello
import json
from collections import namedtuple
from settings import api_key, app_token, kanban_board_id
client = trello.TrelloClient(api_key, token=app_token)

from app import app, server
import kanban_analysis

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    # Header
    html.Nav([
        html.Div(
            [
            html.A([
                html.H1('KPI'),
                ],
                className='navbar-brand',
                href='#'
            )],
            
            className='container',
        )],
        className='navbar navbar-dark stylish-color-dark',
    ),

    html.Div(className='container'),

],
className='bg-light'
)

@app.callback(Output('container', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    print(pathname)
    return kanban_analysis.page_layout


if __name__ == '__main__':
    print('Starting app...')

    app.run_server(debug=True, port=8055, host='0.0.0.0')
