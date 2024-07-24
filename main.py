import dash
import dash_bootstrap_components as dbc

from dash import html, dcc, Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import calendar
import locale


# Importando dados  
df = pd.read_csv('./bases/data_consolidados.csv')





# Criando App
app = dash.Dash(__name__)



# Montando Layout


linha_cabecalho = html.Div([
    html.Div([
        dcc.Dropdown(
            options=df['Cliente'].sort_values(ascending=True).unique(),id='dropdown_cliente',
            placeholder="Clientes",
            style={
                'font-family' : 'Fira Code'
            }
            )
    ],
    style={'width':'25%'})
])


app.layout = html.Div([
    linha_cabecalho
])






# Subindo servidor
if __name__ == '__main__' : app.run_server(debug=True)