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
from data import actionfetcher, boardfetcher
from data import progresschartprocessor, cardstatprocessor, actionprocessor

Range = namedtuple('Range', ['start', 'end'])
def parse_date_input(start_date, end_date):
    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    else:
        last_week = datetime.datetime.today() - datetime.timedelta(days=7)
        start_date = datetime.datetime(last_week.year, last_week.month, last_week.day, last_week.hour, last_week.second)

    if end_date is not None:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 23, 59)
    else:
        today = datetime.datetime.today()
        end_date = datetime.datetime(today.year, today.month, today.day, 23, 59)

    return Range(start_date, end_date)

colors = {
    'To do':            'rgb(224,102,102)',
    'To do-light':      'rgb(234,153,153)',
    'Doing':            'rgb(246,178,107)',
    'Doing-light':      'rgb(249,203,156)',
    'For review':       'rgb(147,196,125)',#'rgb(246,178,107)',
    'For review-light': 'rgb(182,215,168)',
    'On hold':          'rgb(102,102,102)',#'rgb(194,123,160)',
    'On hold-light':    'rgb(153,153,153)',
    'Done':             'rgb(109,158,235)',
    'Done-light':       'rgb(164,194,244)',
    'WIP':              'rgb(102,102,102)',
    'WIP-light':        'rgb(153,153,153)',
}

app.layout = html.Div([
    # Header
    html.Nav([
        html.Div(
            [
            html.A([
                html.H1('XG Transcoder KPI'),
                ],
                className='navbar-brand',
                href='#'
            )],
            
            className='container',
        )],
        className='navbar navbar-dark stylish-color-dark',
    ),
    html.Div([
        html.Div([
            html.Div([
                dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed=datetime.date(2019, 1, 1),
                    max_date_allowed=datetime.date.today(),
                    initial_visible_month=datetime.date.today(),
                    end_date=datetime.date.today(),
                    display_format='Do, MMM YY',
                    start_date_placeholder_text='DO, MMM YY',
                    first_day_of_week=1
                )
            ],
            className='col text-center'
            )
        ],
        className='row'
        ),

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('Cumulative Flow Diagram')
                    ],
                    className='card-header stylish-color-dark text-white text-center'
                    ),
                    html.Div(
                    id='cfd',
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

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('Burn Down')
                    ],
                    className='card-header stylish-color-dark text-white text-center'
                    ),
                    html.Div(
                    id='burn-down',
                    className='card-body text-center'
                    )
                ],
                className='card border-light'
                )
            ],
            className='col-md-6 col-sm-12 col-xs-24'
            ),
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('Burn Up')
                    ],
                    className='card-header stylish-color-dark text-white text-center'
                    ),
                    html.Div(
                    id='burn-up',
                    className='card-body text-center'
                    )
                ],
                className='card border-light'
                )
            ],
            className='col-md-6 col-sm-12 col-xs-24'
            )
        ],
        className='row'
        ),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('Work in progress')
                    ],
                    className='card-header stylish-color-dark text-white text-center'
                    ),
                    html.Div(
                    id='cards-per-list',
                    className='card-body text-center'
                    )
                ],
                className='card border-light'
                )
            ],
            className='col-md-6 col-sm-12 col-xs-24'
            ),
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('Work in progress')
                    ],
                    className='card-header stylish-color-dark text-white text-center'
                    ),
                    html.Div(
                    id='cards-per-member',
                    className='card-body text-center'
                    )
                ],
                className='card border-light'
                )
            ],
            className='col-md-6 col-sm-12 col-xs-24'
            )
        ],
        className='row'
        ),

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H5('Cycle time analysis')
                    ],
                    className='card-header stylish-color-dark text-white text-center'
                    ),
                    html.Div(
                    id='cta',
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

        html.Div([
            
        ],
        className='row'
        ),
    ],
    className='container'
    ),

    html.Div(id='datastore', style={'display': 'none'}),
],
className='bg-light'
)

@app.callback(
    Output('datastore', 'children'),
    [dash.dependencies.Input('date-range', 'start_date'),
     dash.dependencies.Input('date-range', 'end_date')])
def fetch_data(start_date, end_date):
    actionFetcher = actionfetcher.ActionFetcher(client)
    #listFetcher = boardfetcher.BoardListFetcher(client)
    memberFetcher = boardfetcher.BoardMemberFetcher(client)

    actions = actionFetcher.fetch_raw(kanban_board_id)
    #lists = listFetcher.fetch(kanban_board_id)
    members = memberFetcher.fetch(kanban_board_id)

    dataset = {
        'range': parse_date_input(start_date, end_date),
        'members': members,
        #'lists': lists,
        'actions': actions
    }
    
    return json.dumps(dataset, default=str)

@app.callback(
    dash.dependencies.Output('cfd', 'children'),
    [Input('datastore', 'children')])
def update_cfd_graph(json_data):
    data = json.loads(json_data)
    r = Range(datetime.datetime.strptime(data["range"][0], '%Y-%m-%d %H:%M:%S'), datetime.datetime.strptime(data["range"][1], '%Y-%m-%d %H:%M:%S'))
    
    members = data["members"]
    actions = data["actions"]

    board = client.get_board(kanban_board_id)
    processor = actionprocessor.CfdProcessor()
    data = processor.getCfdData(actions, board.get_lists('open'))
    
    plot_data = []
    for series in ['Done', 'On hold', 'For review', 'Doing', 'To do']:
        plot_data.append(dict(
            x=[x for x in data[series].keys() if x>r.start and x<r.end],
            y=[data[series][x] for x in data[series].keys() if x>r.start and x<r.end],
            name=series,
            hoverinfo='x+y+name',
            mode='lines',
            line=dict(
                width=0.5,
                color=colors[series]    
            ),
            stackgroup='one',
        ))
    
    return dcc.Graph(
        id='cfd-graph',
        figure=dict(
            data=plot_data, 
            layout=dict(
                showlegend=False,
                margin=dict(
                    t=40,
                    l=40,
                    r=40,
                    b=40
                ),
                xaxis=dict(showgrid=False)
            ),
        ),
        config=dict(displayModeBar=False),
    )

@app.callback(
    dash.dependencies.Output('burn-down', 'children'),
    [Input('datastore', 'children')])
def update_burndown_graph(json_data):
    data = json.loads(json_data)
    r = Range(datetime.datetime.strptime(data["range"][0], '%Y-%m-%d %H:%M:%S'), datetime.datetime.strptime(data["range"][1], '%Y-%m-%d %H:%M:%S'))
    
    members = data["members"]
    actions = data["actions"]

    board = client.get_board(kanban_board_id)
    processor = actionprocessor.BurnDownProcessor()
    data = processor.getBurnDownData(actions, board.get_lists('open'))
    
    plot_data = []
    plot_data.append(dict(
        x=[x for x in data.keys() if x>r.start and x<r.end],
        y=[data[x]for x in data.keys() if x>r.start and x<r.end],
        name='Work in progress',
        hoverinfo='x+y+name',
        mode='lines',
        fill='tozeroy',
        line=dict(
            width=0.5,
            color=colors['WIP']
        ),
    ))
    
    return dcc.Graph(
        id='burn-down-graph',
        figure=dict(
            data=plot_data,
            layout=dict(
                showlegend=False,
                margin=dict(
                    t=40,
                    l=40,
                    r=40,
                    b=40
                ),
                yaxis=dict(range=[0, max([data[x]for x in data.keys() if x>r.start and x<r.end])+2]),
                xaxis=dict(showgrid=False),
                height=300,
            )
        ),
        config=dict(displayModeBar=False),
    ),

@app.callback(
    dash.dependencies.Output('burn-up', 'children'),
    [Input('datastore', 'children')])
def update_burnup_graph(json_data):
    data = json.loads(json_data)
    r = Range(datetime.datetime.strptime(data["range"][0], '%Y-%m-%d %H:%M:%S'), datetime.datetime.strptime(data["range"][1], '%Y-%m-%d %H:%M:%S'))
    
    members = data["members"]
    actions = data["actions"]

    board = client.get_board(kanban_board_id)
    processor = actionprocessor.BurnUpProcessor()
    data = processor.getBurnUpData(actions, board.get_lists('open'))
    
    plot_data = []
    plot_data.append(dict(
        x=[x for x in data.keys() if x>r.start and x<r.end],
        y=[data[x]["Done"] for x in data.keys() if x>r.start and x<r.end],
        name='Done',
        hoverinfo='x+y+name',
        mode='lines',
        line=dict(
            width=0.5,
            color=colors['Done']
        ),
        stackgroup='one',
    ))
    plot_data.append(dict(
        x=[x for x in data.keys() if x>r.start and x<r.end],
        y=[data[x]["Work in progress"] for x in data.keys() if x>r.start and x<r.end],
        name='Work in progress',
        hoverinfo='x+y+name',
        mode='lines',
        line=dict(
            width=0.5,
            color=colors['WIP']
        ),
        stackgroup='one',
    ))

    y_max = max([data[x]["Done"] for x in data.keys() if x>r.start and x<r.end])+max([data[x]["Work in progress"] for x in data.keys() if x>r.start and x<r.end])+2
    return dcc.Graph(
        id='burn-up-graph',
        figure= dict(
            data=plot_data,
            layout=dict(
                showlegend=False,
                margin=dict(
                    t=40,
                    l=40,
                    r=40,
                    b=40
                ),
                yaxis=dict(range=[0, y_max]),
                xaxis=dict(showgrid=False),
                height=300,
            )
        ),
        config=dict(displayModeBar=False),
    ),

@app.callback(
    dash.dependencies.Output('cards-per-list', 'children'),
    [dash.dependencies.Input('date-range', 'start_date'),
     dash.dependencies.Input('date-range', 'end_date')])
def update_cardsperlist_grap(start_data, end_date):
    processor = boardfetcher.BoardListProcessor(client)
    data = processor.getCardsPerListData(kanban_board_id)

    plot_data = []
    plot_data.append(dict(
        type='bar',
        orientation='h',
        y=[x for x in data.keys() if x != 'Done'],
        x=[data[x] for x in data.keys() if x != 'Done'],
        marker=dict(
            color=colors['WIP-light']
        )
    ))

    return dcc.Graph(
        id='cards-per-list-graph',
        figure=dict(
            data=plot_data,
            layout=dict(
                showlegend=False,
                margin=dict(
                    t=40,
                    l=80,
                    r=40,
                    b=40
                ),
                height=300,
            )
        ),
        config=dict(displayModeBar=False),
    ),

@app.callback(
    dash.dependencies.Output('cards-per-member', 'children'),
    [dash.dependencies.Input('date-range', 'start_date'),
     dash.dependencies.Input('date-range', 'end_date')])
def update_cardspermember_grap(start_data, end_date):
    processor = boardfetcher.BoardListProcessor(client)
    data = processor.getCardsPerMemberData(kanban_board_id)
    
    plot_data = []
    for series in data:
        plot_data.append(dict(
            type='bar',
            orientation='h',
            y=[member for member in data[series].keys() if len(data[series][member])>0],
            x=[len(data[series][member]) for member in data[series].keys() if len(data[series][member])>0],
            marker=dict(
                color=colors['{}-light'.format(series)]
            ),
            name=series
        ))
    return dcc.Graph(
        id='cards-per-member-graph',
        figure=dict(
            data=plot_data,
            layout=dict(
                showlegend=False,
                margin=dict(
                    t=40,
                    l=130,
                    r=40,
                    b=40
                ),
                height=300,
                barmode='stack'
            )
        ),
        config=dict(displayModeBar=False),
    ),

@app.callback(
    dash.dependencies.Output('cta', 'children'),
    [Input('datastore', 'children')])
def update_cta_graph(json_data):
    data = json.loads(json_data)
    r = Range(datetime.datetime.strptime(data["range"][0], '%Y-%m-%d %H:%M:%S'), datetime.datetime.strptime(data["range"][1], '%Y-%m-%d %H:%M:%S'))
    
    members = data["members"]
    actions = data["actions"]

    board = client.get_board(kanban_board_id)
    processor = actionprocessor.CtaProcessor()
    data = processor.getCtaData(actions, board.get_lists('open'))
    cma = processor.getCmaData(data)
    percentiles = processor.getPercentiles(data, [85, 95])

    plot_data = []
    plot_data.append(dict(
        x=[x for x in cma.keys() if x>r.start and x<r.end],
        y=[cma[x] for x in cma.keys() if x>r.start and x<r.end],
        hoverinfo='x+y',
        name='Average cycle time',
        hoveron='points',
        mode='lines',
        line=dict(
            shape='spline',
            width=2,
            color=colors['For review'],
        ),
    ))
    plot_data.append(dict(
        x=[x for x in percentiles.keys() if x>r.start and x<r.end],
        y=[percentiles[x][85] for x in percentiles.keys() if x>r.start and x<r.end],
        hoverinfo='x+y',
        name='85 percentile',
        hoveron='points',
        mode='lines',
        line=dict(
            shape='spline',
            width=2,
            color=colors['Doing'],
        ),
    ))
    plot_data.append(dict(
        x=[x for x in percentiles.keys() if x>r.start and x<r.end],
        y=[percentiles[x][95] for x in percentiles.keys() if x>r.start and x<r.end],
        hoverinfo='x+y',
        name='95 percentile',
        hoveron='points',
        mode='lines',
        line=dict(
            shape='spline',
            width=2,
            color=colors['To do'],
        ),
    ))
    plot_data.append(dict(
        mode='markers',
        x=[x for x in data.keys() if x>r.start and x<r.end],
        y=[data[x]["Lead"] for x in data.keys() if x>r.start and x<r.end],
        text=[data[x]["Details"] for x in data.keys() if x>r.start and x<r.end],
        name='Lead time',
        hoveron='points',
        hoverinfo='text+name',
        marker=dict(
            symbol='diamond',
            size=12,
            color=colors['Done'],
        ),
    ))
    plot_data.append(dict(
        mode='markers',
        x=[x for x in data.keys() if x>r.start and x<r.end],
        y=[data[x]["Cycle"] for x in data.keys() if x>r.start and x<r.end],
        text=[data[x]["Details"] for x in data.keys() if x>r.start and x<r.end],
        name='Cycle time',
        hoveron='points',
        hoverinfo='text+name',
        marker=dict(
            symbol='diamond',
            size=12,
            color=colors['Doing'],
        ),
    ))

    return dcc.Graph(
        id='cta-graph',
        figure=dict(
            data=plot_data,
            layout=dict(
                margin=dict(
                    t=40,
                    l=40,
                    r=40,
                    b=140
                ),
                height=500,
                hovermode='closest',
                xaxis=dict(showgrid=False),
                legend=dict(
                    orientation='h',
                    x=0.5,
                    xanchor='center',
                    y=-0.2,
                    yanchor='bottom',
                    valign='middle',
                ),
            )
        ),
        config=dict(displayModeBar=False),
    ),

    
    
    



if __name__ == '__main__':
    print('Starting app...')

    app.run_server(debug=True, port=8055, host='0.0.0.0')
