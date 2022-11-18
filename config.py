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
Markup styled string with information displayed under Author information
"""
authors_text = """
This software was produced by Petr Triska, Fabian Amman, Lukas Endler and Andreas Bergthaler.
For questions regarding the publication, please contact Prof. Andreas Bergthaler (andreas.bergthaler{at}meduniwien.ac.at).
For questions regarding the code, please contact Petr Triska (triskapet@gmail.com).

""" # string

authors_header = "Authors & Contact" # string

"""
Markup styled string with information displayed under Data Sources
"""
data_sources_text = """
All data used in this demo version of WAVES application are a sample from the dataset published in:
Amman, F., Markt, R., Endler, L. et al. Viral variant-resolved wastewater surveillance of SARS-CoV-2 at national scale. Nat Biotechnol (2022). https://doi.org/10.1038/s41587-022-01387-y
""" # string

data_sources_header = "Data sources" # string



"""
set to True if deploying to Azure App Services.
Will ommit port and host definition.
"""
azure = False

"""
set port on which the application will be deployed
"""
port = 8050 # integer

"""
"""
host = "0.0.0.0" # string

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
sampling_areas = "sampling_locations.tsv"

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


