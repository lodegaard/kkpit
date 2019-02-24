import dash
import dash_core_components as dcc
import dash_html_components as html
import flask

external_scripts = [
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js'
    },
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.4/umd/popper.min.js'
    },
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.2.1/js/bootstrap.min.js'
    },
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.7.3/js/mdb.min.js'
    }
]

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://use.fontawesome.com/releases/v5.7.0/css/all.css',
        'rel': 'stylesheet'
    },
    {
        'href': 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.2.1/css/bootstrap.min.css',
        'rel': 'stylesheet'
    },
    {
        'href': 'https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.7.2/css/mdb.min.css',
        'rel': 'stylesheet'
    },
]


server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.config.suppress_callback_exceptions = True

