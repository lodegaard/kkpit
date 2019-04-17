import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

page_layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H5('Setup')
                ],
                className='card-header stylish-color-dark text-white text-center'
                ),
                html.Div([
                    html.P('Text here'),
                    dcc.Dropdown(id='board-dropdown')
                ],
                id='setup',
                className='card-body text-center'
                )
            ],
            className='card border-light'
            )
        ],
        className='col bg-light'
        ),
    ],
    className='row bg-light'
    ),
],
id='setup-page'
)

@app.callback(
    Output('board-dropdown', 'children'),
    [Input('datastore', 'children')])
def fill_board_dropdown():