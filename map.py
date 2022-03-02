import pandas as pd
#import numpy as np 
import geopandas as gpd
import plotly.express as px
#import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, dash_table
# from dash.exceptions import PreventUpdate

## Reading files
dtgeo = gpd.read_file('dtgeo.geojson')
col_list_dist = list(dtgeo.columns[8:36])
acgeo2 = gpd.read_file('acgeo2.geojson')
dist = list(acgeo2['DIST_NAME'].unique()) # Pick district names from ac file
dist = sorted(dist)
dist.insert(0, "All")
gpgeo = gpd.read_file('gpgeo.geojson')
cont = pd.read_csv('contributers.csv')

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
    html.H1("Mission Antyodaya 2020",style={'text-align':'center'})],
            className='Header'),
    html.Div([
        html.Label('Select an Indicator', style={'color': '#000000', 'fontSize' : '16px'}),
        dcc.Dropdown(id="Indicator",
                 options= [{"label" : i, "value" : i} for i in col_list_dist],
                 placeholder="Select an Indicator",
                 multi=False,
                 searchable=True,
                 value="Agriculture (0-7)",
                 clearable=False,
                 style={'width' : '100%', 'verticalAlign':"middle",'color':'black'}),
        html.Br(),
        html.Label('Select a District', style={'color': '#000000', 'fontSize' : '16px'}),
        dcc.Dropdown(id="District",
                 options= [{"label" : i, "value" : i} for i in dist],
                 placeholder= "Select a District",
                 multi=False,
                 searchable=True,
                 value='All',
                 clearable=False,
                 style={'width' : '100%', 'verticalAlign':"middle",'color':'black'}
                ),
        html.Br(),
        html.Label('Select an Assembly Constituency',
                style={'color': '#000000', 'fontSize' : '16px'}),
        dcc.Dropdown(id="AC",
                 options= [],
                 placeholder= "Select an Assembly Constituency",
                 multi=False,
                 searchable=True,
                 value='None',
                 clearable=False,
                 style={'width' : '100%', 'verticalAlign':"middle",'color':'black'}
                )], className= "dropdown"),
    html.Div(id='output_container', children=[],className='output'),
    html.Div([
        html.H4('About Mission Antyodaya', style={'color': '#000000', 'fontSize' : '16px'}),
        dcc.Markdown('''
                 First started in 2017-18, Mission Antyodaya helps assess development of rural areas.
                 Annual survey in Gram Panchayats across the country is carried out and 
                 each Gram Panchayat is given a score out of 100 based on 26 Parameters. 

                 * For more information visit:
                 [Mission Antyodaya 2020](https://missionantyodaya.nic.in)
                 ''')], className='Markdown'
    ),
    html.Div([
        html.Label('Indicator Breakdown', style={'color': '#000000', 'fontSize' : '16px'}),
        html.Div(id="final_table")],className='indi_details'),
    html.Div([
        dcc.Graph(id='MAmap', figure={},
                           style={
                                  "height": "70vh",
                                  "border": "3px #5c5c5c solid",
                                 })], className='map')
],className='wrapper')

@app.callback(
    Output('AC','options'),
    Input('District','value')
)
def update_ac(District):
    df = acgeo2[acgeo2['DIST_NAME']== District]
    return [{'label' : i, 'value' : i} for i in df['AC Name']]

@app.callback(
    Output('final_table', 'children'),
    Input('Indicator', 'value')
)
def update_table(mtric_chose):
    print(mtric_chose)
    df = cont[cont["Parameters"] == mtric_chose]
    return dash_table.DataTable(data=df.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in df.columns],
                        style_cell={'text-align':'left',
                                    'height':'auto',
                                    'font-family': 'HelveticaNeue'
                                   },
                        style_header={'fontWeight':'bold'},
                        style_cell_conditional=[
                            {'if': {'column_id':'Parameters'},
                            'width' : '35vh'},
                            {'if': {'column_id':'Max Attainable Score'},
                            'width' : '20%'},
                                               ],
                        style_table={'overflowX':'auto',
                                     'minWidth': '100%'
                                    },
                        )

@app.callback(
    [Output('output_container', 'children'),
     Output('MAmap', 'figure')],
    [Input('Indicator', 'value'),
     Input('District', 'value'),
     Input('AC','value')])
def update_figure(mtric_chosen,distr,ac):
    container = "The indicator chosen by user was: {}".format(mtric_chosen)

    if distr == 'All':
        fig = px.choropleth_mapbox(
                            data_frame = dtgeo,
                            geojson = dtgeo,
                            featureidkey='properties.DIST_NAME', # from geojson
                            locations = 'DIST_NAME', # from df
                            center = {'lon': 73.8496, 'lat': 26.70},
                            mapbox_style='carto-positron',
                            color = str(mtric_chosen), # from df
                            color_continuous_scale='deep',
                            title='District-Level',
                            zoom=5.7,
                            hover_name='DIST_NAME',
                            labels={str(mtric_chosen):'Score'}
                        )
        fig.layout['coloraxis']['colorbar']['x'] = 1
        fig.update_layout(
                          margin=dict(l=15, r=15, t=50, b=15),
                          paper_bgcolor="wheat",
                          title_font_family = 'Times New Roman',
                          title_font_size = 26,
                         )
        return container, fig
    else:
        if ac == 'None':
            dist_data = acgeo2[acgeo2['DIST_NAME']==distr]
            cento = dtgeo[dtgeo['DIST_NAME']==distr]
            cen = cento.centroid
            lon = cen.apply(lambda p: p.x)
            lat = cen.apply(lambda p: p.y)
            fig = px.choropleth_mapbox(
                                data_frame = dist_data,
                                geojson = dist_data,
                                featureidkey='properties.AC Name', # from geojson
                                locations = 'AC Name', # from df
                                center = {'lon':lon.iloc[0], 'lat':lat.iloc[0]},
                                mapbox_style='carto-positron',
                                color = str(mtric_chosen), # from df
                                color_continuous_scale='deep',
                                title='Assembly-Level',
                                zoom=6,
                                hover_name='AC Name',
                                labels={str(mtric_chosen):'Score'}
                            )
            fig.update_layout(
                              margin=dict(l=15, r=15, t=50, b=15),
                              paper_bgcolor="LightSteelBlue",
                              title_font_family = 'Times New Roman',
                              title_font_size = 26)
            return container, fig
        else:
            ac_data = gpgeo[gpgeo['AC Name']== ac]
            cento = acgeo2[acgeo2['AC Name']==ac]
            cen = cento.centroid
            lon = cen.apply(lambda p: p.x)
            lat = cen.apply(lambda p: p.y)
            fig = px.choropleth_mapbox(
                                data_frame = ac_data,
                                geojson = ac_data,
                                featureidkey='properties.Gram Panchayat', # from geojson
                                locations = 'Gram Panchayat', # from df
                                center = {'lon':lon.iloc[0], 'lat':lat.iloc[0]},
                                mapbox_style='carto-positron',
                                color = str(mtric_chosen), # from df
                                color_continuous_scale='deep',
                                title='Panchayat-Level',
                                zoom=6,
                                hover_name='Gram Panchayat',
                                labels={str(mtric_chosen):'Score'})
            fig.update_layout(
                              margin=dict(l=15, r=15, t=50, b=15),
                              paper_bgcolor="LightSteelBlue",
                              title_font_family = 'Times New Roman',
                              title_font_size = 26,
                             )
            return container, fig

if __name__ == '__main__':
    app.run_server(debug=True)# use_reloader=False")
