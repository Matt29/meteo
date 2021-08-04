import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as fac
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
#import pandas_datareader.data as web
import datetime
from rosely import WindRose
import numpy as N

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.CERULEAN],
    meta_tags=[{'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0'}]
)
server = app.server

#set positions to plot
list_pos=[]
list_pos.append(dict(name="conquet",lon=-4.87,lat=48.33))
list_pos.append(dict(name="groix",lon=-3.4903,lat=47.59))
list_pos.append(dict(name="large",lon=-3.9819,lat=47.60))
name_list=[x["name"] for x in list_pos]
lon_list=[x["lon"] for x in list_pos]
lat_list=[x["lat"] for x in list_pos]

stat="conquet"

##########
#wind plot
##########
spd = pd.read_pickle('wind_spd.pkl')
direction=pd.read_pickle('wind_dir.pkl')
fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(go.Scatter(x=spd.index,y=spd[stat],name="speed"))
fig1.add_trace(go.Scatter(x=direction.index,y=direction[stat],name="dir"),secondary_y=True)
fig1.update_layout(title=dict(text='Wind from Arome Model - %s'%(stat),x=0.5),
                   xaxis_title='',
                   yaxis_title='speed(m/s)')
test_rose=pd.DataFrame(data=dict(date=spd.index,ws=spd[stat],wd=direction[stat]))
wind=WindRose(test_rose)
wind.calc_stats(normed=True,bins=8)
fig4 = px.bar_polar(wind.wind_df, r="frequency", theta="direction",
                   color="speed", template="plotly_white",
                   color_discrete_sequence= px.colors.sequential.Plasma_r)
fig4.update_layout(title=dict(text='Wind Rose - %s'%(stat),x=0.5))

##########
#WAVE plot
##########
wave_hs = pd.read_pickle('wave_hs.pkl')
wave_dir = pd.read_pickle('wave_dir.pkl')
wave_data=pd.DataFrame(data=dict(date=wave_hs.index,ws=wave_hs[stat],wd=wave_dir[stat]))
wave_rose=WindRose(wave_data)
#fig3=px.line(wave,x=wave.index,y='hs')
fig3=go.Figure()
fig3.add_trace(go.Scatter(x=wave_hs.index,y=wave_hs['groix']))
fig3.update_layout(title=dict(text='Hs from WAM Model - %s'%(stat),x=0.5),
                   xaxis_title='',
                   yaxis_title='Hs(m)')
#rose
wave_rose.calc_stats(normed=True,bins=8)
wave_rose.wind_df=wave_rose.wind_df.rename(columns={"speed":'Hs'})

fig5 = px.bar_polar(wave_rose.wind_df, r="frequency", theta="direction",
                   color="Hs", template="plotly_white",
                   color_discrete_sequence= px.colors.sequential.Plasma_r)
fig5.update_layout(title=dict(text='Wave Rose - %s'%(stat),x=0.5))

##########
#HYDRO plot
##########
hydro=pd.read_pickle('hydro.pkl')
hydro_fig = make_subplots(specs=[[{"secondary_y": True}]])
#fig.add_trace(go.Scatter(x=data.index,y=data.xe,name="level"))
hydro_fig.add_trace(go.Scatter(x=hydro.index,y=hydro.xe,name="level",fill=None))
hydro_fig.add_trace(go.Scatter(x=hydro.index,y=hydro.xe+hydro.delta_xe,line_width=0.4,name="surcote",fill="tonexty"))#,secondary_y=True)
hydro_fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.9))

hydro_fig2 = make_subplots(specs=[[{"secondary_y": True}]])
u=hydro.u.values
v=hydro.v.values
x=N.linspace(0,1,len(hydro))
y=N.zeros(len(x))
npt=4
spd=N.sqrt(u**2+v**2)
u1 = N.ma.where(spd!=0., u/spd, u)
v1 = N.ma.where(spd!=0., v/spd, v)

x1=x[::npt]
y1=spd[::npt]
y1=y[::npt]
u1=u1[::npt]
v1=v1[::npt]
hydro_fig2.add_trace(go.Scatter(x=x,y=spd,mode='lines',name="current speed"))
quiv=fac.create_quiver(x1,y1,u1,v1,scale =0.1, scaleratio = 0.25,arrow_scale=0.2,name="current Direction")
hydro_fig2.add_trace(quiv.data[0])
hydro_fig2.update_layout(xaxis_tickvals =x1[::8],xaxis_ticktext=hydro.index[::npt])
hydro_fig2.add_trace(go.Scatter(x=x,y=hydro.xe.values,line_width=0.5,name="water level",fill=None),secondary_y=True)
hydro_fig2.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.9))

######
#map
######
fig2 = go.Figure(data=go.Scattermapbox(
        lon = lon_list,
        lat = lat_list,
        text = name_list,
        mode = 'markers',
        marker=go.scattermapbox.Marker(
            size=14),
        )      )
fig2.update_layout(mapbox_style="open-street-map",

                 mapbox=dict(center=go.layout.mapbox.Center(lon=-4.49,lat=48.35),
                     zoom=6)
                 )

app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("Meteo Dashboard",
                        className='text-center text-primary mb-4'),
                width=12)
    ),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='map-fig', figure=fig2)
        ], width=6),
    ], justify="center"),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='wind-fig', figure=fig1),
        ], width={'size': 6, 'offset': 0}),

        dbc.Col([
            dcc.Graph(id='wind_dir-fig', figure=fig4),
        ], width={'size': 6, 'offset': 0}),

    ], align='center', no_gutters=True, justify='start'),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='wave-fig', figure=fig3),
        ], width={'size': 6, 'offset': 0}),

        dbc.Col([
            dcc.Graph(id='wave-fig2', figure=fig5),
        ], width={'size': 6, 'offset': 0}),

    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='hydro-fig1', figure=hydro_fig),
        ], width=6),

        dbc.Col([
            dcc.Graph(id='hydro-fig22', figure=hydro_fig2),
        ], width=6),
    ], no_gutters=True)

], fluid=True)


@app.callback(output=Output('wave-fig', 'figure'),
              inputs=Input('map-fig', 'clickData'))
def _update_graph(clickData):
    print(clickData)
    # click
    stat = clickData['points'][0]['text']
    print("stat=", stat)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=wave.index, y=wave[stat]))
    fig.update_layout(title=dict(text='Hs from WAM Model - %s' % (stat), x=0.5),
                      xaxis_title='',
                      yaxis_title='Hs(m)')
    return fig


@app.callback(output=Output('wind-fig', 'figure'),
              inputs=Input('map-fig', 'clickData'))
def _update_graph(clickData):
    print(clickData)
    # click
    stat = clickData['points'][0]['text']
    print("stat=", stat)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=spd.index, y=spd[stat], name="speed"))
    fig.add_trace(go.Scatter(x=direction.index, y=direction[stat], name="dir"), secondary_y=True)
    fig.update_layout(title=dict(text='Wind from Arome Model - %s' % (stat), x=0.5),
                      xaxis_title='',
                      yaxis_title='speed(m/s)')
    return fig


@app.callback(output=Output('wind_dir-fig', 'figure'),
              inputs=Input('map-fig', 'clickData'))
def _update_graph(clickData):
    print(clickData)
    # click
    stat = clickData['points'][0]['text']
    print("stat=", stat)
    test_rose = pd.DataFrame(data=dict(date=spd.index, ws=spd[stat], wd=direction[stat]))
    wind = WindRose(test_rose)
    wind.calc_stats(normed=True, bins=8)
    fig = px.bar_polar(wind.wind_df, r="frequency", theta="direction",
                       color="speed", template="plotly_white",
                       color_discrete_sequence=px.colors.sequential.Plasma_r)
    fig.update_layout(title=dict(text='Wind Rose - %s' % (stat), x=0.5))
    return fig


#RUN SERVER
if __name__ == '__main__':
    app.run_server( port = 8090,  debug=True)
