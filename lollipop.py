import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

"""
generates lollipop-style genome map plot
"""
def get_lollipop(df):
	fig1 = make_subplots(specs=[[{"secondary_y": True}]])
	
	gen = pd.read_csv("genome_structure.csv", sep = "\t")
	for i in range(0, len(gen)):
				fig1.add_shape(type="rect",
								y0 = 0, x0 = gen["start"][i],
								x1 = gen["end"][i],
								y1 = -0.05,
								fillcolor = gen["color"][i],
								line=dict(color = gen["color"][i], width = 1))

	df = df.sort_values(by=["position"])
	for index, row in df.iterrows():
				 fig1.add_shape(type='line',
								y0 = 0, x0 = row["position"],
								x1 = row["position"],
								y1 = row["allele_freq"],
								line=dict(color='darkblue', width = 0.1))
	
	fig1.add_trace(go.Scatter(x = df[df["ann_effect"]=="missense_variant"]["position"], 
							y = df[df["ann_effect"]=="missense_variant"]["allele_freq"],
							mode = 'markers',
							hoverinfo = "text",
							hovertext = df[df["ann_effect"]=="missense_variant"]["ann_aa"],
							marker_color ='crimson',
							name= "missense",
							marker_size= 5),secondary_y=False)# Draw lines
							
	fig1.add_trace(go.Scatter(x = df[df["ann_effect"]=="synonymous_variant"]["position"], 
							y = df[df["ann_effect"]=="synonymous_variant"]["allele_freq"],
							mode = 'markers',
							hoverinfo = "text",
							hovertext = df[df["ann_effect"]=="synonymous_variant"]["ann_aa"],
							marker_color ='blue',
							name= "synonymous",
							marker_size= 5),secondary_y=False)# Draw lines
	
	fig1.add_trace(go.Scatter(x = df[~df["ann_effect"].isin(["synonymous_variant", "missense_variant"])]["position"], 
							y = df[~df["ann_effect"].isin(["synonymous_variant", "missense_variant"])]["allele_freq"],
							mode = 'markers',
							hoverinfo = "text",
							hovertext = df[~df["ann_effect"].isin(["synonymous_variant", "missense_variant"])]["ann_aa"],
							marker_color ='green',
							name= "other",
							marker_size= 5),secondary_y=False)# Draw lines
	try:
		fig1.add_trace(go.Scatter(x = df["position"], 
								y = df["depth"],
								mode = 'lines',
								name= "depth of coverage",
								line=dict(color='darkblue', width = 0.5)),
								secondary_y=True)
	except:
		pass

	
	# Set y-axes titles
	fig1.update_yaxes(title_text="Frequency", secondary_y=False)
	fig1.update_yaxes(title_text="Coverage", secondary_y=True, type="log")
	fig1.update_layout(template="plotly_white", xaxis = dict(
															tickmode = 'array',
															tickvals = list(gen["start"]),
															ticktext = list(gen["feature"])
															),
						#title = "Mutations",
						yaxis_title = "frequency",
						xaxis_title = "genomic position",
						legend=dict(yanchor="top",y=1.1, xanchor="right"),
						margin = dict(l=10, r=10, b=10, t=50)
						)
	
	return fig1

