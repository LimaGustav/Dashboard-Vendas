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
df['dt_Venda'] = df['dt_Venda'].astype('datetime64[us]')
df['Mes'] = df['dt_Venda'].dt.strftime('%b').str.upper()




#Variaveis de apoio

url_dark = dbc.themes.DARKLY
url_vapor = dbc.themes.VAPOR


# Funções de apoio
def filtro_cliente(cliente_selecionado):
    if cliente_selecionado is None:
        return pd.Series(True,index=df.index)
    else:
        # Retorna os indices
        return df['Cliente'] == cliente_selecionado
    
def filtro_mes(mes_selecionado):
    if mes_selecionado is None:
        return pd.Series(True,index=df.index)
    else:
        # Retorna os indices
        return df['Mes'] == mes_selecionado
    

def filter_categoria(categoria_selecionada):
    if categoria_selecionada is None:
        return pd.Series(True,index=df.index)
    else:
        # Retorna os indices
        return df['Categorias'] == categoria_selecionada




# Criando App
app = dash.Dash(__name__)



# Montando Layout


linha_cabecalho = html.Div([
    html.Div([
        dcc.Dropdown(
            options=df['Cliente'].sort_values(ascending=True).unique(),id='dropdown_cliente',
            placeholder="Clientes",
            style={
                'font-family' : 'Fira Code',
                'color':'black'
            }
            )
    ],
    style={'width':'250px'}),

    html.Div([
        html.Legend(
            "Gustavo Lima",
            style={'font-size': '150%', 'text-align':'center'}
            )
    ],style={}),

    html.Div(
        ThemeSwitchAIO(
            aio_id='theme',
            themes=[
                url_dark,
                url_vapor
            ]
        ),
        style={}
    )
],
style={'display':"flex",'align-items':'center','justify-content':'space-between','margin':"30px"})

linha1 = html.Div([
    html.Div([
        html.Div([
            html.H4(id='output_cliente'),
            dcc.Graph(id='visual01')
        ]),
            
      
        dcc.Dropdown(
            options=df['Categorias'].sort_values().unique(),
            id='dropdown_categoria',
            placeholder="Categoria",
            style={
                'font-family' : 'Fira Code',
                'color':'black',
                'width': '50%',
                'margin-top':'20px'
            }

        )
        
    ],style={'display':'flex'}),
    
    html.Div(
        dbc.RadioItems(
            id='radio_meses',
            options=df['Mes'].unique(),
            inline=True
        )
    )
],style={'width':'90%','margin':'0 auto', 'text-align':'center'})

app.layout = html.Div([
    linha_cabecalho,
    linha1  
])



#Callbacks
@app.callback(
    Output("output_cliente",'children'),
    Input('dropdown_cliente','value')
)
def atualizar_texto(cliente_selecionado):
    if cliente_selecionado:
        return f"Top 5 Produtos comprados por {cliente_selecionado}"
    return 'Top 5 Produtos Vendidos'

@app.callback(
    Output('visual01','figure'),
    [
        Input('dropdown_cliente','value'),
        Input(ThemeSwitchAIO.ids.switch('theme'),'value'),
        Input('radio_meses','value'),
        Input('dropdown_categoria','value')
    ]
)
def visual01(cliente,toggle,mes,categoria):
    template = 'darkly' if toggle else 'vapor'

    nome_cliente = filtro_cliente(cliente)
    nome_mes = filtro_mes(mes)
    nome_categoria = filter_categoria(categoria)
    filtro = nome_cliente & nome_mes & nome_categoria
    df1 = df.loc[filtro]

    print(df1.dtypes)
    df_grupo = df1.groupby(['Produto','Categorias'])['Total'].sum().reset_index()
    df_grupo = df_grupo.sort_values(by='Total',ascending=False).head()

    fig1 = px.bar(df_grupo,
                  x='Produto',
                  y='Total',
                  title='Teste',
                  text='Total',
                  height=280,
                  template=template
                  )
    
    fig1.update_layout(
        margin={'t':0},
        xaxis={'showgrid':False},
        yaxis={
            'showgrid':False,
            'range' : [
                df_grupo['Total'].min(),
                df_grupo['Total'].max()
            ],
        },
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickangle = -15,
        font={'size':13},
        plot_bgcolor='#101010',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # fig1.update_traces(texttemplate='%{text::.2s}',textposition='outside')
    return fig1


# Subindo servidor
if __name__ == '__main__' : app.run_server(debug=True)