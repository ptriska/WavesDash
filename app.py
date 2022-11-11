#!/usr/bin/env python# 
#-*- coding: utf-8 -*
import sys
import dash_auth
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate
import dash_table
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_trich_components as dtc
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import time
import datatable
import os.path
from os import path
import calendar
from lollipop import get_lollipop
import config
import flask


"""
This web-based application enables interactive visualization and analysis of SARS-CoV-2 sequencing data from wastewater treatment plants.
The application can be easily customized through the configuration file. For customization of the configuration file you will need a geojson file containing shape of your
catchment areas, a csv file containing basic information about catchment areas and sequencing data in the csv table.
The software is written in python 3.8 and the web server runs on Plotly Dash.

Please cite

"""


"""
if the password file is present and use_password is True, the authentication will be required
"""

if config.use_pwd == True:
	try:
		f = open("pwd.txt").read().splitlines()
		VALID_USERNAME_PASSWORD_PAIRS = {f[0]:f[1]}
		auth = dash_auth.BasicAuth(
			app,
			VALID_USERNAME_PASSWORD_PAIRS
		)
	except:
		pass

server = flask.Flask(__name__) # define flask app.server
dash_app = dash.Dash(__name__, server = server, suppress_callback_exceptions = True, external_stylesheets=[dbc.themes.YETI, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'])
app = dash_app.server
dash_app.title= config.app_title


"""
load geojson file containing shapes of the sampling areas
"""
with open(config.geojson) as f:
  plants = json.load(f)

"""
load simplified version of the geojson file containing shapes of the sampling areas
"""
with open(config.geojson_simplified) as f:
  plants_simple = json.load(f)

"""
load file with information about the sampling areas
"""
df_plants = pd.read_csv(config.sampling_areas, sep = "\t")

df_plants_id = df_plants.set_index("LocationID")
plants_dict = df_plants_id.to_dict("index")

df_plants_names = df_plants.set_index("LocationName")
plants_names_dict = df_plants_names.to_dict("index")

"""
Markup styled string with information displayed at the start up of the application
"""
synopsis_text = config.synopsis_text
data_source_text = config.data_sources_text
authors_text = config.authors_text


def get_week(year, calendar_week):
	monday = datetime.datetime.strptime(f'{year}-{calendar_week}-1', "%Y-%W-%w").date()
	return monday.strftime("%d-%b-%Y"), (monday + datetime.timedelta(days=6.9)).strftime("%d-%b-%Y")


"""
*** APP layout
"""
"""
layout of the intro modal window (synopsis)
"""
modal = dbc.Modal(
			  [
				dbc.ModalHeader(config.synopsis_header),
				dbc.ModalBody(dcc.Markdown(synopsis_text)),
				dbc.ModalFooter([
					html.Div("The dataset is loading, please wait 1 minute", id = "modal_loading_div"),
					dbc.Spinner(dbc.Button("Wait", id="close", n_clicks=0)),
				]),
			],
			id="modal",
			is_open=True,
			size = "xl"
		),
		

"""
layout of the intro modal window (authors)
"""
modal_authors = dbc.Modal(
			  [
				dbc.ModalHeader(config.authors_header),
				dbc.ModalBody(dcc.Markdown(config.authors_text)),
				dbc.ModalFooter([
					dbc.Spinner(dbc.Button("Close", id="close_authors", n_clicks=0)),
				]),
			],
			id="modal_authors",
			is_open=False,
			size = "xl"
		),

"""
layout of the intro modal window (data sources)
"""
modal_data_sources = dbc.Modal(
			  [
				dbc.ModalHeader(config.data_sources_header),
				dbc.ModalBody(dcc.Markdown(config.data_sources_text)),
				dbc.ModalFooter([
					dbc.Spinner(dbc.Button("Close", id="close_data_sources", n_clicks=0)),
				]),
			],
			id="modal_data_sources",
			is_open=False,
			size = "xl"
		),

"""
layout of modal window
"""
bigwin_modal = dbc.Modal(
			  [
				
				dbc.ModalBody(dbc.Row([dbc.Col(id = "bigcol2")])),
				dbc.ModalFooter([
					dbc.Button(
						"Close", id="close_bigwin", n_clicks=0
					)
				]),
			],
			id="bigwin_modal",
			is_open=False,
			size = "xl"
		),

"""
layout of the right-hand filtering panel
"""
filter_col = dbc.Col([
								html.H3("Filter"),
								html.Label("Show..."),
								dbc.InputGroup(
									[
											dcc.Dropdown(id = "show", style = {"minWidth":"100%", "marginBottom":"10px"}, multi = False, clearable = False, options = [{"label":"Most recent result","value":"all"},{"label":"Timelapse","value":"timelapse"}], value = "all") ,
										
									]
								),

								html.Label("Variant (searchable)"),
								dbc.InputGroup(
									[
										dcc.Dropdown(id = "variant", style = {"minWidth":"100%", "marginBottom":"10px"}, multi = False, clearable = False, options = [{"label":"All variants","value":"all"}], value = "all") ,
									]
								),
								html.Label("WW Plant (searchable)"),
								dbc.InputGroup(
									[
										dcc.Dropdown(id = "plants", optionHeight=60, style = {"minWidth":"100%", "marginBottom":"10px"}, multi = False, clearable = False, options = [{"label":"All WW plants", "value":"all"}], value = "all") ,
									
									]
								),
								dbc.Button("▼ Advanced options ▼", id = "collapse_btn"),
								dbc.Collapse([
									dbc.Label("Filter by...", style={"marginTop":"10px"}),
									dbc.RadioItems(
										options=[
											{"label": "Variant", "value": "variant"},
											{"label": "Mutation", "value": "mutation"},
										],
									value="variant",
									id="radioitems",
									inline=True
									),
									#html.Label("Mutation (searchable)"),
									dbc.InputGroup(
										[
											html.Label("genomic feature"),
											dcc.Dropdown(id = "features", style = {"minWidth":"100%", "marginBottom":"10px"}, multi = False, clearable = False, options = [{"label":"Loading options...","value":"choose..."}], value = "choose...") ,
											
											dbc.Spinner([
												html.Label("Mutation (searchable)"),
												dcc.Dropdown(id = "mutation", style = {"minWidth":"100%", "marginBottom":"10px"}, multi = False, clearable = False, options = [{"label":"Loading options...","value":"choose..."}], value = "choose...") ,
											]),
										]

									),
									html.Label("Date range"),
									dbc.InputGroup(
										[
											dcc.DatePickerRange(id = "date", display_format = "DD/MM/YYYY", with_portal  = True, style = {"minWidth":"100%", "marginBottom":"10px"})
										
										]
									),
									dbc.Button("Update", id = "btn", color = "success")
									
								],id="collapse", is_open=True)
							], width = 3, style={"marginRight":"10px", "background-color": "#f8f9fa", "position": "fixed","width": "16rem","height": "100%","right": 0})

"""
layout of the stacked-plot divide
"""
pie_col = dbc.Col([
					html.Div([
								dbc.Spinner([
									dbc.Card(children = [
															dcc.Markdown("""
															**🛈 Use instructions:**
															+ Click in the catchment area in the map or select wastewater treatment plant from the menu to display variant composition across all sampling time points.
															+ Click in the barplot representing the variant composition to select a sampling time point. This will display a genome map depicting detected mutations and their respective frequency in the sample.
															+ To display frequency of a mutation of interest, change the 'Filter by' menu in the right-hand panel to 'Mutation'. Then select a genome feature where is this mutation located and select the mutation from the drop-down menu.
															+ To use the timelapse feature, select the 'Timelapse' option from the drop-down menu 'Show...'.
															"""
															)														], id = "stacked_div"),
								]),
								
								dbc.Collapse([
									html.Div(id = "town"),
									html.Div(id = "state"),
									html.Div(id = "connected"),
									html.Div(id = "population"),
									
								], id="plant_info_collapse", is_open=False),
								dbc.Spinner([
									dbc.Card([
										html.Div(id="needle_div"),
									])	
								]),	
					], id = "pie_div"),
				], id = "pie_col", width = 10, style = {"transition": "width .5s"})

"""
General app layout
"""
dash_app.layout = html.Div(

	[
		# store divides keep chunks of data ready within the user's browser
		dcc.Store(id = "dummy"),
		dcc.Store(id = "nothing"),
		dcc.Store(id = "dummy2"),
		dcc.Store(id = "dataframe"),
		dcc.Store(id = "current_plant"),
		dcc.Store(id = "Fig"),
		dcc.Store(id = "parsed_data"),
		dcc.Store(id = "earliest_date"),
		dcc.Store(id = "latest_date"),
		dcc.Store(id = "freq"),
		dcc.Store(id = "plant_readable"),
		dcc.Store(id = "all_ww"),
		dcc.Location(id="url"),
		html.Div(modal),
		html.Div(modal_authors),
		html.Div(modal_data_sources),
		html.Div(bigwin_modal),
		
		# Navbar style
		dbc.NavbarSimple(
			children=[
				html.A([
					html.Img(src=config.logo,height="65px"),
					], href=config.logo_link, target="_blank"
				),
				
				dbc.DropdownMenu(
								children=[
									dbc.DropdownMenuItem(dbc.Button("Synopsis", id="open", n_clicks=0)),
									dbc.DropdownMenuItem(dbc.Button("Data sources", id="open_data_sources", n_clicks=1)),
									dbc.DropdownMenuItem(dbc.Button("Authors", id="open_authors", n_clicks=1)),
								],
								nav=True,
								in_navbar=True,
								style = {"font-size":"20px", "font-weight":"bold", "marginLeft":"25px"},
								label="Menu",
				),
			],
			brand=config.title,
			brand_style = {"font-size":"30px", "float":"left", "font":dict(family=config.title_font)},
			color="rgb(64,185,212)",
			
			dark=True,
			fluid = True,
		),
		
		dbc.Container([
				
				dbc.Row([
					dbc.Col([
								html.Div("Parsing data...", id="parsing1"),
								dbc.Spinner([html.Div("Parsing data...", id="parsing"),
								# left-hand divide containing the geo map 
								html.Div(id = "choropleth1_div")]),
								dbc.Row(justify="between",
									children = [
											dbc.Col([html.P("Click on a catchment area to show the results", style={"fontSize":"22px"}, id = "click_title")]),
											html.Div([
												dbc.RadioItems(
													options =[
																{"label":"dynamic scale","value":"dynamic"},
																{"label":"static scale","value":"static"}
													],
													inline = True,
													value = "static",
													id="static_dynamic"
												),
											], id= "radio_div", style={"display":"inline-block"}),
											dbc.Col(
												[dbc.Button("toggle", id="toggle")
												], align = "end", width = 2) 
									]
								) 
							], width = 8, id = "map_col", style = {"transition": "width .5s"}
					),
					# right hand divides
					dbc.Col([
						dbc.Row([
							# divide with the stacked plot
							pie_col,
							# divide with the filtering panel
							filter_col
							
							
						]),
					]),
				
			
			]
		),
	], fluid = True, style= {"marginTop":"30px","marginLeft":"30px"},
)
])

"""
*** End of APP layout
"""

"""
*** APP callbacks
"""

"""
callback: parse data
"""
@dash_app.callback(
Output("parsed_data","data"),
Output("date","start_date"),
Output("date","end_date"),
Output("earliest_date","data"),
Output("parsing","children"),
Output("parsing1","children"),
Output("all_ww","data"),
Input("dummy","data")
)
def parse_df(dummy):
	# attempts to find a pre-computed file.
	try:
		if not path.exists("data/allele_freq_processed.tsv"):
			raise Exception
		ww_df = datatable.fread("data/variant_freq_processed.tsv", sep="\t").to_pandas()
		ww_df.index = pd.to_datetime(ww_df['sample_date'])
		earliest_date = ww_df.index[0]
		latest_date = ww_df.index[-1]
		past_date = latest_date - relativedelta(months=1)
		
		all_ww = list(ww_df["LocationID"].unique())
		return ww_df.to_dict("records"), past_date, latest_date, earliest_date, None, None, all_ww
		
	# if no precomputed file is found, the program attempts to parse raw data and generate the pre-computed file.
	except Exception:
		ww_df = datatable.fread("data/variant_freq.tsv", sep = "\t").to_pandas()
		ww_df = ww_df[ww_df["value"]>0]
		ww_df['sample_date'] = pd.to_datetime(ww_df['sample_date'])
		ww_df.index = pd.to_datetime(ww_df['sample_date'])
		
		ww_df.sort_index(inplace = True)
		
		earliest_date = ww_df.index[0]
		latest_date = ww_df.index[-1]
		ww_df['week'] = ww_df['sample_date'].dt.isocalendar().week#[1]
		ww_df['year'] = ww_df['sample_date'].dt.isocalendar().year#[0]
		ww_df["kw"] = ww_df["week"].astype(str)+"/"+ww_df["year"].astype(str)
		ww_df.index.names = ["sampleDate"]
		
		# if a sampling location has multiple time points in one calendar week
		# more recent time points are marked as _1, _2 etc.
		master = pd.DataFrame()
		for ix, data in ww_df.groupby(by=["kw","LocationID"]):
			if len(data.sample_date.unique())>1:
				week=pd.DataFrame()
				cntr = 1
				for i, d in data.groupby(by='sampleDate'):
					d["kw"]=d["kw"]+"_"+str(cntr)
					cntr += 1
					week = pd.concat([week, d])
				master = pd.concat([master, week])
			else:
				master = pd.concat([master, data])
		master.sort_index(inplace = True)
		past_date = latest_date - relativedelta(months=1)
		master.to_csv("data/variant_freq_processed.tsv", sep="\t")
		if not path.exists("data/allele_freq_processed.tsv"):
			df_frq = datatable.fread("data/allele_freq.tsv", sep = "\t").to_pandas()
			try:
				df_frq["sample_id"] = df_frq["BSF_sample_name"]
			except:
				pass
			df_frq = df_frq[ df_frq["sample_id"].isin(list(ww_df.sample_id) ) ]
			df_frq["mut"]=df_frq["ann_gene"]+":"+df_frq["ann_aa"].replace("p.","")
			df_meta = master.drop_duplicates(subset = ['sample_id'], keep='first')
			df_frq = pd.merge(df_frq, df_meta, on = "sample_id", how = "left")
			
			def splitmut(mut):
				return mut.split(":")[0]
			df_frq["gen_feature"] = df_frq["mut"].apply(splitmut)
			
			#df_frq[["gen_feature", "aa_change"]] = df_frq["mut"].str.split(":", 1, expand=True)
			df_frq = df_frq[["sample_id","mut","kw","allele_freq","LocationID","LocationName","position","ann_effect","ann_aa", "gen_feature", "depth"]]
			df_frq.to_csv("data/allele_freq_processed.tsv", sep = "\t", index=False)
		all_ww = list(master["LocationID"].unique())
		return master.to_dict("records"), past_date, latest_date, earliest_date, None, None, all_ww

"""
callback: creates a subset of data based on selected dates
"""
@dash_app.callback(
Output("dataframe","data"),
Input("parsed_data","data"),
Input("btn","n_clicks"),
State("date","start_date"),
State("date","end_date")
)
def process_df(data, btn, start, end):
	print("subset process data")
	ww_df = pd.DataFrame.from_dict(data)
	ww_df = ww_df[ (ww_df["sampleDate"]>= start) & (ww_df["sampleDate"]<=end) ]
	print("returning")
	return ww_df.to_dict("records")

"""
callback: fill the forms in the filtering divide with options based on parsed data
"""
@dash_app.callback(
Output("variant","options"),
Output("plants","options"),
#Output("mutation","options"),
Input("dataframe","data"),
)
def options(data):
	print("loading options")
	ww_df = pd.DataFrame.from_dict(data)
	#df_frq = datatable.fread("allele_freq_processed.tsv", sep = "\t").to_pandas()
	var_options = [{"label":"All variants","value":"all"}]+[{"label":x, "value":x} for x in list(ww_df.variant.unique())]
	plant_options = [{"label":"All WW plants","value":"all"}]+[{"label":x, "value":x} for x in list(ww_df.LocationName.unique())]
	#mutation_options = [{"label":"cosi", "value":"cosi"}]#[{"label":"Choose...","value":"choose..."}]+[{"label":x, "value":x} for x in list(df_frq.mut.unique())]
	print("returning options")
	return var_options, plant_options#, mutation_options


"""
callback: fill the forms in the filtering divide with options based on parsed data
"""
@dash_app.callback(
Output("features","options"),
Output("features","value"),
Input("dummy","data"),
)
def feature_options(data):
	print("loading features")
	ww_df = pd.DataFrame.from_dict(data)
	#df_frq = datatable.fread("allele_freq_processed.tsv", sep = "\t").to_pandas()
	df_frq = pd.read_csv("data/allele_freq_processed.tsv", sep = "\t")
	all_features = list(df_frq.gen_feature.unique())
	features_options = [{"label":x, "value":x} for x in all_features if isinstance(x, str)]
	print("returning features", features_options)
	return features_options, all_features[0]

"""
callback: fill the forms in the filtering divide with options based on parsed data
"""
@dash_app.callback(
Output("mutation","options"),
Output("mutation","value"),
Input("features","value"),
)
def mutation_options(feature):
	print("loading mutations")
	#df_frq = datatable.fread("allele_freq_processed.tsv", sep = "\t").to_pandas()
	df_frq = pd.read_csv("data/allele_freq_processed.tsv", sep = "\t")
	df_frq = df_frq[df_frq["gen_feature"] == feature]
	mutation_options = [{"label":"Choose...","value":"choose..."}]+[{"label":x, "value":x} for x in list(df_frq.mut.unique())]
	print("returning mutations: ",len(list(df_frq.mut.unique())))
	return mutation_options, "choose..."


"""
callback: update the map based on selected filters.
The map can provide several different views:
+ choropleth map showing frequency of variant or a mutation in a given sampling area
+ cathegorical map showing the most common variant for a given sampling area
+ timelapse map
"""
@dash_app.callback(
Output("choropleth1_div","children"),
Output("close","children"),
Output("modal_loading_div","children"),
Output("radio_div", "style"),
Output("click_title","children"),
Input("show","value"),
Input("variant","value"),
Input("plants","value"),
Input("mutation","value"),
Input("dataframe","data"),
Input("static_dynamic","value"),
Input("radioitems","value"),
State("Fig","data"),
State("date","end_date"),
State("all_ww","data"),
State("date","start_date"),
)
def update_map(show, variant, plant, mutation, data,static_dynamic, radioitems, Fig, end_date, all_ww, start_date):
	max_date_label = str(end_date).split("T")[0]
	min_date_label = str(start_date).split("T")[0]
	try:
		df_full = pd.DataFrame.from_dict(data)
		sampled_locations = list(df_full["LocationID"].unique())
		all_samples = list(df_full["sample_id"].unique())
		df = df_full
		if variant != "all":
			df = df[df["variant"]==variant]
		if plant != "all":
			df = df[df["LocationName"]==plant]
		df=df.sort_index()
	
		minor_recent = df.drop_duplicates("LocationID", keep='last')
		
		lat = config.lat
		lon = config.lon
		zoom = config.zoom
		
		
		if plant!= "all":
			lat = plants_names_dict[plant]["dcpLatitude"]
			lon = plants_names_dict[plant]["dcpLongitude"]
			zoom = 8
		
		# *** display mode: most frequent variant (static)
		if show == "all" and variant == "all" and radioitems =="variant":
	
			ww_recent_major = pd.DataFrame()
			for index, data in df.groupby(by="LocationID"):
				max_date = data.sample_date.max()
				min_date = data.sample_date.min()
				
				
				
				data = data[data["sample_date"]==max_date]
				data = data.sort_values(by="value", ascending = False)
				ww_recent_major = pd.concat([ww_recent_major, data.head(1)])
			ww_recent_major.sort_index(inplace = True)
			
			if plant == "all":
				for plant in all_ww:
					if plant not in list(ww_recent_major["LocationID"]):
						ww_recent_major = ww_recent_major.append({
							"LocationID" : plant,
							'variant' : "not sampled",
						}, ignore_index=True)
			if len(ww_recent_major)==0:
				raise Exception
			fig=px.choropleth_mapbox(ww_recent_major,
					geojson=plants,
					featureidkey='properties.uwwcode',
					locations = "LocationID",
					color_discrete_map={"not sampled":"gray"},
					color = "variant",
					mapbox_style = "carto-positron",
					hover_data = ["LocationName","kw","variant"],
					opacity = 0.5,
					center={"lat":lat, "lon": lon},
					zoom = zoom,
					height=900,
					title = "Distribution of the most frequent variant between "+min_date_label+" and "+max_date_label+"."
					)
			radio_style = {"display":"none"}
		
		# *** display mode: frequency of a mutation (static)
		if mutation != "choose..." and radioitems == "mutation" and show == "all":
			df = datatable.fread("data/allele_freq_processed.tsv", sep = "\t").to_pandas()
			
			if plant != "all":
				df = df[df["LocationName"]==plant]
			df = df[df["sample_id"].isin(all_samples)]
			df = df[df["mut"]==mutation]
			
			# keep the most recent record
			df = df.sort_values(by="kw", ascending = False)
			df = df.drop_duplicates("LocationID", keep='first')
			
			# static scale
			if static_dynamic == "static":
				step = 0.25
				range_color=[-0.25,1]
				tickvals = [-0.25,0.0,0.25,0.5,0.75,1.0]
				ticktext = ["not sampled","0.0","0.25","0.5","0.75","1.0"]
			
			# dynamic scale
			else:
				step = float(df.allele_freq.max())/4
				range_color=[-1*step,df.allele_freq.max()]
				tickvals = [-1*step, 0.0, step, 2*step, 3*step,4*step ]
				ticktext = ["not sampled", str(0.0), str(round(step, 2)), str(round(2*step, 2)), str(round(3*step, 2)), str(round(4*step, 2))]
			
			# fill not sampled and not observed
			for plant in all_ww:
				try:
					plant_name = plants_dict[plant]["LocationName"]
				except:
					plant_name = "N/A"
				# not sampled
				if plant not in sampled_locations:
					df = df.append({
						"LocationID" : plant,
						"allele_freq" : -1*step,
						"LocationName":plant_name,
						"kw":"N/A",
						"variant":variant
					}, ignore_index=True)
				# not observed
				elif plant not in list(df["LocationID"]): 
					df = df.append({
						"LocationID" : plant,
						"allele_freq" : 0.0,
						"LocationName":plant_name,
						"kw":"N/A",
						"variant":variant
					}, ignore_index=True)
			def format_val(val):
				if float(val)<0:
					return "not sampled"
				else:
					return round(float(val), 2)
			df["Allele_freq"] = df.allele_freq.apply(format_val)
			
			if len(df)==0:
				raise Exception
				
			fig=px.choropleth_mapbox(df,
					geojson=plants,
					featureidkey=config.feature_id_key,
					locations = "LocationID",
					color='allele_freq',  
					color_continuous_scale= ["darkgrey","white","#FFEFCF","orange","red","crimson","#6D010D"],#px.colors.diverging.RdGy[::-1],
					range_color = range_color,
						
					mapbox_style = "carto-positron",
					opacity = 0.5,
					hover_data = ["LocationName","kw","Allele_freq"],
					center={"lat":lat, "lon": lon},
					zoom = zoom,
					height=900,
					title = "Frequency of the mutation "+mutation+" between "+min_date_label+" and "+max_date_label+".",
					)
			fig.update_layout(coloraxis_colorbar=dict(
					title="frequency",
					tickvals = tickvals,
					tickfont = dict(size=15),
					ticktext = ticktext,
			))
		
		
			radio_style = {"display":"inline-block"}
		
		# *** display mode: frequency of a variant (static)
		if show == "all" and variant != "all" and radioitems=="variant":
			
			if plant == "all":
			
				if static_dynamic == "static":
					step = 0.25
					range_color=[-0.25,1]
					tickvals = [-0.25,0.0,0.25,0.5,0.75,1.0]
					ticktext = ["not sampled","0.0","0.25","0.5","0.75","1.0"]
				else:
					step = float(minor_recent.value.max())/4
					range_color=[-1*step,minor_recent.value.max()]
					tickvals = [-1*step, 0.0, step, 2*step, 3*step,4*step ]
					ticktext = ["not sampled", str(0.0), str(round(step, 2)), str(round(2*step, 2)), str(round(3*step, 2)), str(round(4*step, 2))]
				for plant in all_ww:
					try:
						plant_name = plants_dict[plant]["LocationName"]
					except:
						plant_name = "N/A"
					if plant not in sampled_locations:
						minor_recent = minor_recent.append({
							"LocationID" : plant,
							"value" : -1*step,
							"LocationName":plant_name,
							"kw":"N/A",
							"variant":variant
						}, ignore_index=True)
					elif plant not in list(minor_recent["LocationID"]): 
						minor_recent = minor_recent.append({
							"LocationID" : plant,
							"value" : 0.0,
							"LocationName":plant_name,
							"kw":"N/A",
							"variant":variant
						}, ignore_index=True)
			def format_val(val):
				if float(val)<0:
					return "not sampled"
				else:
					return round(float(val), 2)
			minor_recent["Value"] = minor_recent.value.apply(format_val)

			if len(minor_recent)==0:
				raise Exception
			
			fig=px.choropleth_mapbox(minor_recent,
					geojson=plants,
					featureidkey='properties.uwwcode',
					locations = "LocationID",
					color='value',  
					color_continuous_scale= ["darkgrey","white","#FFEFCF","orange","red","crimson","#6D010D"],#px.colors.diverging.RdGy[::-1],
					range_color = range_color,
					mapbox_style = "carto-positron",
					opacity = 0.5,
					hover_data = ["LocationName","kw","Value","variant"],
					center={"lat":lat, "lon": lon},
					zoom = zoom,
					height=900,
					title = "Frequency of the variant "+variant+" between "+min_date_label+" and "+max_date_label+".",
					)
			fig.update_layout(coloraxis_colorbar=dict(
					title="frequency",
					tickvals=tickvals,
					tickfont = dict(size=15),
					ticktext=ticktext,
			))
			radio_style={"display":"inline-block"}
		
		# *** display mode: most frequent variant (timelapse)
		if show == "timelapse" and variant == "all" and radioitems == "variant":
			df_temp = pd.DataFrame()
			for index, data in df.groupby(by="LocationID"):
				data = data.sort_values(by="value", ascending = False)
				
				data = data.drop_duplicates('kw', keep='first')
				df_temp = pd.concat([df_temp, data])
			df = df_temp.sort_values(by="sample_date")
			if plant == "all":
				for index, data in df.groupby(by="kw"):
					for plant in all_ww:
						if plant not in list(data["LocationID"]):
							df = df.append({
								"LocationID" : plant,
								"kw":index,
								'variant' : "not sampled",
							}, ignore_index=True)
			catg = df['variant'].unique()
			dts = df['kw'].unique()
			for tf in dts:
				for i in catg:
					df = df.append({
						'kw' : tf,
						'variant' : i,
						'cartodb_id' : '0',
					}, ignore_index=True)
			
			if len(df)==0:
				raise Exception
			fig=px.choropleth_mapbox(df,
				geojson=plants_simple,
				featureidkey='properties.uwwcode',
				locations = "LocationID",
				animation_frame='kw',
				color = "variant",
				color_discrete_map={"not sampled":"gray"},
				hover_data = ["LocationName","kw","variant"],
				mapbox_style = "carto-positron",
				opacity = 0.5,
				center={"lat":lat, "lon": lon},
				zoom = zoom,
				height=900,
				title = "Timelapse distribution of the most frequent variants between "+min_date_label+" and "+max_date_label+"."
			)
			fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
			fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 50
			radio_style = {"display":"none"}
		
		# *** display mode: variant frequency (timelapse)
		if show == "timelapse" and variant != "all" and radioitems=="variant":
			if len(df)==0:
				raise Exception
			
			for index, data in df.groupby(by="kw"):
				sampled_locations = list(df_full[df_full["kw"]==index]["LocationID"])
				for plant in all_ww:
					try:
						plant_name = plants_dict[plant]["LocationName"]
					except:
						plant_name = "N/A"
					if plant not in sampled_locations:
						print("NF: ",plant)
						print(plant in sampled_locations)
						df = df.append({
							"LocationID" : plant,
							"value" : -0.25,
							"LocationName":plant_name,
							"kw":index,
							"variant":variant
						}, ignore_index=True)
					elif plant not in list(data["LocationID"]): 
						df = df.append({
							"LocationID" : plant,
							"value" : 0.0,
							"LocationName":plant_name,
							"kw":index,
							"variant":variant
						}, ignore_index=True)
		
			fig = px.choropleth_mapbox(df,
				geojson=plants_simple,
				featureidkey='properties.uwwcode',
				locations = "LocationID",
				animation_frame='kw',
				color='value',  
				color_continuous_scale= ["darkgrey","white","#FFEFCF","orange","red","crimson","#6D010D"],#px.colors.diverging.RdGy[::-1],
				range_color=[-0.25,1],
				mapbox_style = "carto-positron",
				opacity = 0.5,
				center={"lat":lat, "lon": lon},
				zoom = zoom,
				height=900,
				title = "Timelapse frequency of the variant "+variant+" between "+min_date_label+" and "+max_date_label+"."
			)
			fig.update_layout(coloraxis_colorbar=dict(
					title="frequency",
					tickvals=[-0.25,0.0,0.25,0.5,0.75,1.0],
					tickfont = dict(size=15),
					ticktext=["not sampled","0.0","0.25","0.5","0.75","1.0"],
			))
			fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
			fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 50
			radio_style = {"display":"inline-block"}
			
		# *** display mode: mutation frequency (timelapse)
		if show == "timelapse" and mutation != "choose..." and radioitems=="mutation":
			
			df = datatable.fread("data/allele_freq_processed.tsv", sep = "\t").to_pandas()
			if plant != "all":
				df = df[df["LocationName"]==plant]
			df = df[df["sample_id"].isin(all_samples)]
			df = df[df["mut"]==mutation]
			
			for index, data in df.groupby(by="kw"):
				sampled_locations = list(df_full[df_full["kw"]==index]["LocationID"])
				for plant in all_ww:
					try:
						plant_name = plants_dict[plant]["LocationName"]
					except:
						plant_name = "N/A"
					if plant not in sampled_locations:
						df = df.append({
							"LocationID" : plant,
							"allele_freq" : -0.25,
							"LocationName":plant_name,
							"kw":index,
							"mutation":mutation
						}, ignore_index=True)
					elif plant not in list(data["LocationID"]): 
						df = df.append({
							"LocationID" : plant,
							"allele_freq" : 0.0,
							"LocationName":plant_name,
							"kw":index,
							"mutation":mutation
						}, ignore_index=True)

			if len(df)==0:
				raise Exception
			fig=px.choropleth_mapbox(df,
				geojson=plants_simple,
				featureidkey='properties.uwwcode',
				locations = "LocationID",
				animation_frame='kw',
				color='allele_freq',  
				color_continuous_scale= ["darkgrey","white","#FFEFCF","orange","red","crimson","#6D010D"],#px.colors.diverging.RdGy[::-1],
				range_color = [-0.25, 1],
				mapbox_style = "carto-positron",
				opacity = 0.5,
				center={"lat":lat, "lon": lon},
				zoom = zoom,
				height=900,
				title = "Timelapse frequency of the mutation "+mutation+" between "+min_date_label+" and "+max_date_label+"."
			)
			fig.update_layout(coloraxis_colorbar=dict(
					title="frequency",
					tickvals=[-0.25,0.0,0.25,0.5,0.75,1.0],
					tickfont = dict(size=15),
					ticktext=["not sampled","0.0","0.25","0.5","0.75","1.0"],
			))
			fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 500
			fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 50
			radio_style = {"display":"inline-block"}
				
		fig.update_layout(height=900,margin = {"l":10, "r":0, "b":5, "t":25}, legend=dict(yanchor="top", xanchor="right"))
		current = time.time()
		print("returning")
		return dcc.Graph(figure=fig, id="choropleth1"), "Close", None, radio_style, "Click on a catchment area to show the results"
	except Exception as e:
		print(e)
		if mutation == "choose..." and radioitems=="mutation":
			raise Exception
		else: 
			return "Selected filters return no results.", "Close", None, {"display":"none"}, None

"""
callback: toggle the modal window: synopsis
"""
@dash_app.callback(
	Output("modal", "is_open"),
	[Input("open", "n_clicks"), Input("close", "n_clicks")],
	[State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
	if n1 or n2:
		return not is_open
	return is_open
	
"""
callback: toggle the modal window: authors
"""
@dash_app.callback(
	Output("modal_authors", "is_open"),
	[Input("open_authors", "n_clicks"), Input("close_authors", "n_clicks")],
	[State("modal_authors", "is_open")],
)
def toggle_modal(n1, n2, is_open):
	if n1 == 1:
		return False
	if n1 or n2:
		return not is_open
	return is_open

"""
callback: toggle the modal window: data sources
"""
@dash_app.callback(
	Output("modal_data_sources", "is_open"),
	[Input("open_data_sources", "n_clicks"), Input("close_data_sources", "n_clicks")],
	[State("modal_data_sources", "is_open")],
)
def toggle_modal(n1, n2, is_open):
	if n1 == 1:
		return False
	if n1 or n2:
		return not is_open
	return is_open

"""
callback: toggle the modal window: big window
"""
@dash_app.callback(
	Output("bigwin_modal", "is_open"),
	[Input("bigwin", "n_clicks"), Input("close_bigwin", "n_clicks")],
	[State("bigwin_modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
	if n1 == 1:
		return False
	if n1 or n2:
		return not is_open
	return is_open

"""
callback: generate the stacked plot with the sampling region information
"""
@dash_app.callback(
Output("stacked_div","children"),
Output("town","children"),
Output("state","children"),
Output("connected","children"),
Output("population","children"),
Output("current_plant","data"),
Output("plant_readable","data"),
Input("choropleth1","clickData"),
Input("plants","value"),
State("parsed_data","data"),
)
def update_variant_pie(clickData,plant_name, data):
	df = pd.DataFrame.from_dict(data)
	
	ctx = dash.callback_context
	if not ctx.triggered:
		button_id = None
	else:
		button_id = ctx.triggered[0]['prop_id'].split('.')[0]
	if button_id =="choropleth1":
		if clickData is not None:
			plant = clickData["points"][0]["location"]
	elif button_id =="plants":
		plant = plants_names_dict[plant_name]["LocationID"]
	else:
		plant = None
	town = "Town: "+plants_dict[plant]["adress_town"]
	state = "State: "+plants_dict[plant]["state"]
	connected = "Connected towns: "+plants_dict[plant]["connected_towns"]
	population = "Population: "+str(int(plants_dict[plant]["total_population"]))
		
	df = df[df["LocationID"]==plant]
	all_lin = df.variant.value_counts()
	all_lin = (list(all_lin.index))
	
	figdata = []
	all_dates = list(df.kw.unique())
	for lin in all_lin:
		counts = []
		for date in all_dates:
			month_counts = float( len(df[df['kw']==date]))
			if lin != "other":
				try:
					lineage_counts = float(df[(df['variant']==lin) & (df['kw']==date)].iloc[0]["value"])
				except:
					lineage_counts = 0
			
			counts.append(lineage_counts)
		style={"width":"1500px", "height":"1000px"},
		figdata.append(go.Bar(name= lin, x=all_dates, y=counts))
	
	text = html.Label("Click on a time point to display mutation frequencies.")
	button = dbc.Button("▼ Catchment info ▼", id = "plant_btn")
	
	fig_total = go.Figure(data=figdata)
	fig_total.update_layout(yaxis_range=[0,1], barmode='stack', height=300, margin = dict(l=10, r=10, b=10, t=30),  xaxis = {"tickangle":90}, title = plants_dict[plant]["LocationName"])
	graph = dcc.Graph(figure = fig_total, id = "stackbar", config = dict({'scrollZoom': True, 'displaylogo': False}))
	return [graph,button, text], town, state, connected, population, plant, plants_dict[plant]["LocationName"]


"""
callback: toggle enable/disable filter input field
"""
@dash_app.callback(Output("variant","disabled"), Output("mutation","disabled"), Output("features","disabled"), Input("radioitems","value"))
def toggle_var_mut(value):
	if value == "mutation":
		return True, False, False
	else:
		return False, True, True


"""
callback: generates the lollipop plot with frequency of mutations
"""
@dash_app.callback(Output("needle_div","children"), Output("bigcol2","children"), Input("stackbar","clickData"), State("current_plant","data"),  State("plant_readable","data"))
def show_freq(clickdata, plant_name, plant_readable):

	df = datatable.fread("data/allele_freq_processed.tsv", sep = "\t").to_pandas()
	df = df[ (df["kw"]==clickdata["points"][0]["label"]) & (df["LocationID"]==plant_name) & (df["allele_freq"]>0.05)]
	if len(df)<1:
		return [html.Div("No data to show."), None]
	kw = clickdata["points"][0]["label"]
	title = "Mutations frequency in "+plant_readable+", week "+kw
	
	fig = get_lollipop(df)

	return [html.Label(title, style={"marginTop":"15px"}), dcc.Graph(figure= fig, config = dict({'scrollZoom': True, 'displaylogo': False})), dbc.Button("Expand 📤", id = "bigwin")], html.Div([html.Label(title, style={"marginTop":"15px"}), dcc.Graph(figure= fig, config = dict({'scrollZoom': True, 'displaylogo': False}))])


"""
callback: expand/collapse sampling region info (eg. water treatment plant catchment area)
"""
@dash_app.callback(
	Output("plant_info_collapse", "is_open"),
	Output("plant_btn", "children"),
	[Input("plant_btn", "n_clicks")],
	[State("plant_info_collapse", "is_open")],
)
def toggle_plant_collapse(n, is_open):
	if n:
		if is_open == True:
			label = "▼ Catchment info ▼"
		else:
			label = "▲ Catchment info ▲"
		return not is_open, label

	return is_open, "▼ Catchment info ▼"

"""
callback: expand/collapse advanced filter options
"""
@dash_app.callback(
	Output("collapse", "is_open"),
	Output("collapse_btn", "children"),
	[Input("collapse_btn", "n_clicks")],
	[State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
	if n:
		if is_open == True:
			label = "▼ Advanced options ▼"
		else:
			label = "▲ Advanced options ▲"
		return not is_open, label

	return is_open, "▼ Advanced options ▼"


"""
callback: expand/collapse choropleth map
"""
@dash_app.callback(Output("map_col","width"), Output("pie_col","width"),Output("pie_div","style"),Output("toggle","children"), Input("toggle","n_clicks"), State("map_col","width"))
def toggle(i, w):
	if w == 6:
		return 10,0, {"display":"none"}, "⯬  Collapse map"
	else:
		return 6,8, {"display":"block"}, "Expand map ⯮"
	
"""
*** End of APP callbacks
"""


if __name__ == "__main__":
	dash_app.run_server(debug=config.debug,dev_tools_ui=config.debug, dev_tools_props_check=config.debug)
