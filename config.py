## CONFIG FILE

"""
title of your app
"""
app_title = "" # string

"""
password protected - if set to True, a login form will
appear when the app is loaded
Passwords and usernames can be specified in the pwd.txt file
"""

use_pwd = False # boolean

"""
Markup styled string with information displayed at the start up of the application
"""
synopsis_text = """
This web-based application enables interactive visualization and analysis of SARS-CoV-2 sequencing data from wastewater treatment plants.
The application can be easily customized through the configuration file. For customization of the configuration file you will need a geojson file containing shape of your
catchment areas, a csv file containing basic information about catchment areas and sequencing data in the csv table.
The software is written in python 3.8 and the web server runs on Plotly Dash.

""" # string

synopsis_header = "Synopsis" # string



"""
set port on which the application will be deployed
"""
port = 8050 # integer

"""
set to True if you want to perform debugging. Do not use in production.
"""
debug = True # boolean

"""
geo json file with sampling areas
"""
geojson = "geo_data/plants_simplified_5.geojson" # path to geojson

"""
simplified geo json file with sampling areas
"""
geojson_simplified = "geo_data/supersimple.geojson" # path to geojson

"""
id key in geojson. Must match id key in data files.
"""
feature_id_key = "properties.uwwcode" # string

"""
set geo coordinates of the center point on a map
The default values are set to Austria
"""
lat = 48 # float
lon = 13.1 # float
zoom = 6 # integer

"""
file with information about the sampling areas

"""
sampling_areas = "sewage_plants.tsv"

logo = "assets/cemm_banner.png" # path to img
logo_link = "https://cemm.at" # link

"""
title on the navbar
"""
title = "SARS-CoV-2 monitoring in wastewater in Austria" # string

"""
font for navbar title 
"""
title_font = 'Franklin Gothic' # string


