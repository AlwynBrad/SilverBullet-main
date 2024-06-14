import pandas as pd
import dash
from dash import Dash, dcc, html, dash_table, Input, Output, ctx, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data
df = pd.read_csv('')