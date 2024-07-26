import dash
import dash_bootstrap_components as dbc

from dash import html, dcc, Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd



# Importando dados  
df = pd.read_csv('./bases/data_consolidados.csv')
df['dt_Venda'] = df['dt_Venda'].astype('datetime64[us]')
df['Mes'] = df['dt_Venda'].dt.strftime('%b').str.upper()


#Listas de apoio
lista_meses = []
lista_categorias = []
for mes in df['Mes'].unique():
    if mes is None:
        continue
    
    lista_meses.append({
        'label': mes,
        'value': mes
    })

lista_meses.append({'label':'Todos','value':'ano'})

for cat in df['Categorias'].unique():
     lista_categorias.append({
        'label': cat,
        'value': cat
    })

lista_categorias.append({'label':'Todos','value':'todos'})
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
    elif mes_selecionado == 'ano':
        return df['Mes']
    else:
        # Retorna os indices
        return df['Mes'] == mes_selecionado 
    

def filter_categoria(categoria_selecionada):
    if categoria_selecionada is None:
        return pd.Series(True,index=df.index)
    elif categoria_selecionada == 'todos':
        return df['Categorias']
    else:
        # Retorna os indices
        return df['Categorias'] == categoria_selecionada




# Criando App
app = dash.Dash(__name__)
server = app.server



# Montando Layout


linha_cabecalho = html.Div([
   
    dcc.Dropdown(
        options=df['Cliente'].sort_values(ascending=True).unique(),id='dropdown_cliente',
        placeholder="Clientes",
        style={
            'font-family' : 'Fira Code',
            'color':'black',
            'width':'33%'
            }
        ),

        html.Legend(
            "Gustavo Lima",
            style={'font-size': '150%', 'text-align':'center','width':'33%'}
            ),


    html.Div(
        ThemeSwitchAIO(
            aio_id='theme',
            themes=[
                url_dark,
                url_vapor
            ]
        ),
        style={'width':'33%'}
    )
],
style={'display':"flex",'align-items':'center','justify-content':'space-between','margin':"30px"})

linha1 = html.Div([
    html.Div([
        html.Div([
            html.H4(id='output_cliente'),
            dcc.Graph(id='visual01')
        ]),
            
      html.Div([
          dcc.Dropdown(
        options=lista_categorias,
        id='dropdown_categoria',
        placeholder="Categoria",
        style={
            'font-family' : 'Fira Code',
            'color':'black',
            'width': '50%',
            'margin-top':'20px'
        }

        ),
          
        dbc.RadioItems(
            id='radio_meses',
            options=lista_meses,
            inline=True
        )
      ])
    
        
    ],style={'display':'flex'}),
    
   
   
],style={'width':'90%','margin':'0 auto', 'text-align':'center'})

linha2 = html.Div([
    dcc.Graph(
        style={'width':'70%'},
        id='visual02'
    ),
    dcc.Graph(
        style={'width':'30%'},
        id='visual03'
    )
],style={'display': 'flex', 'justify-content':'space-between','width':'90%'})
# App Layout----------------------------------------------------------------------------------
app.layout = html.Div([
    linha_cabecalho,
    linha1,
    linha2
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
            # 'range' : [
            #     df_grupo['Total'].min(),
            #     df_grupo['Total'].max()
            # ],
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

@app.callback(
    Output('visual02','figure'),
    [
        Input(ThemeSwitchAIO.ids.switch('theme'),'value'),
        Input('radio_meses','value'),
        Input('dropdown_categoria','value')
    ]
)
def visual02(toggle,mes,categoria):
    template = 'darkly' if toggle else 'vapor'

    nome_mes = filtro_mes(mes)
    nome_categoria = filter_categoria(categoria)
    filtro = nome_mes & nome_categoria
    df1 = df.loc[filtro]

    df_grupo = df1.groupby(by='Loja')['Total'].sum().reset_index()
    df_grupo = df_grupo.sort_values(by='Total',ascending=False).head()

    fig1 = px.bar(df_grupo,
                  x='Loja',
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
            # 'range' : [
            #     df_grupo['Total'].min(),
            #     df_grupo['Total'].max()
            # ],
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