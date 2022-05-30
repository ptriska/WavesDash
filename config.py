
"""
title of your app
"""
app_title = "" # string



"""
Markup styled string with information displayed at the start up of the application
"""
synopsis_text = "" # string

synopsis_header = "Synopsis" # string



"""
set port on which the application will be deployed
"""
port = 81 # integer

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


