# WAVWES (Web-based tool for Analysis and Visualization of Environmental Samples)
## A web application for visualization of wastewater pathogen sequencing results

This web-based application enables interactive visualization and analysis of SARS-CoV-2 sequencing data from wastewater treatment plants.
The application can be easily customized through the configuration file. For customization of the configuration file you will need a geojson file containing shape of your
catchment areas, a csv file containing basic information about catchment areas and sequencing data in the csv table.
The software is written in python 3.8 and the web server runs on Plotly Dash.

## Quickstart
+ git clone https://github.com/ptriska/WavesDash
+ cd WavesDash
+ pip install -r requirements
+ python app.py
+ open browser at localhost:8050

## Customization of the app
+ customize the config.py
+ supply own data files (example data files are in data/)
+ input data file format is described in file_format.txt
+ supply own geojson file with sampling areas
+ supply own description of sampling locations (sampling_locations.tsv)
