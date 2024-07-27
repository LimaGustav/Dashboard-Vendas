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
df = df[df['Mes'].notna()]
df = df[df['Mes'] != '']

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
    if mes_selecionado is None or mes_selecionado=='ano':
        return pd.Series(True,index=df.index)

    else:
        # Retorna os indices
        return df['Mes'] == mes_selecionado 
    

def filter_categoria(categoria_selecionada):
    if categoria_selecionada is None or categoria_selecionada == 'todos':
        return pd.Series(True,index=df.index)
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
            'width':'40%'
            }
        ),

        html.Legend(
            "Dashboard",
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
        style={'width':'33%','text-align':'end'}
    )
],
style={'display':"flex",'align-items':'center','justify-content':'space-between','margin':"30px"})

linha1 = html.Div([
        html.Div([
            html.H4(id='output_cliente'),
            dcc.Graph(id='visual01')
        ],style={'width':'65%'}),
            
      html.Div([
          dcc.Dropdown(
        options=lista_categorias,
        id='dropdown_categoria',
        placeholder="Categoria",
        style={
            'font-family' : 'Fira Code',
            'color':'black',
            'width': '80%',
            'margin-bottom':'20px'
        }

        ),
          
        dbc.RadioItems(
            id='radio_meses',
            options=lista_meses,
            inline=True,
            style={'text-align':'justify'}
        )
      ], style={'width':'30%','margin-top':'40px'})
   
   
],style={'margin':'0 auto', 'text-align':'center','display':"flex"})

linha2 = html.Div([
    dcc.Graph(
        style={'width':'65%'},
        id='visual02'
    ),
    dcc.Graph(
        style={'width':'35%'},
        id='visual03'
    )
],style={'display': 'flex', 'justify-content':'space-between','width':'100%','margin-top':'50px'})
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
    [
        
    Output('visual02','figure'),
    Output('visual03','figure'),
    ],
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
    filtro_categoria = nome_categoria
    
    df2 = df.loc[filtro_categoria]
    df3 = df.loc[filtro]
    
    df_grupo2 = df2.groupby(by='Loja')['Total'].sum().reset_index()
    df_grupo2 = df_grupo2.sort_values(by='Total',ascending=False).head()
    
    df_grupo3 = df3.groupby(by=['Mes','Loja'])['Total'].sum().reset_index()

    fig2 = px.bar(df_grupo2,
                  x='Loja',
                  y='Total',
                  title='Teste',
                  text='Total',
                  height=280,
                  template=template
                  )
    
    fig2.update_layout(
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
    
    
    #Visual 3 ________________________________________________________________
    fig3 = go.Figure(data=go.Scatterpolar(
        r = df_grupo3["Total"],
        fill='toself',
        theta=df_grupo3['Loja'],
        line=dict(color='rgba(31,119,180)'),
        marker=dict(color='rgb(31,119,180)',size=8),
        opacity=0.8
    ))
    
    fig3.update_layout(
        template=template,

        polar=dict(
            radialaxis=dict(
                visible=True,
                tickfont=dict(size=10),
                tickangle=0,
                tickcolor='rgba(68,68,68)',
                ticklen=5,
                tickwidth=1,
                tickprefix='',
                ticksuffix='',
                range=[
                    0,max(df_grupo3['Total']+1000)
                ]
            )
        ),
        font=dict(
            family='Fira Code',
            size=12
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40,r=40,t=80,b=40)
    )
    return fig2,fig3
# Subindo servidor
if __name__ == '__main__' : app.run_server(debug=True)