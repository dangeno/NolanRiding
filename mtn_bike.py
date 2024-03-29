'''

Nolan Riding Biomech Assessment 

- Trail 1

'''

import os
import fnmatch
import platform
import streamlit as st
import numpy as np 
import pandas as pd
import scipy as sp
import glob
import plotly.graph_objects as go
from datetime import datetime
import timedelta
from plotly.subplots import make_subplots
from scipy.signal import find_peaks
from scipy.signal import savgol_filter
import matplotlib.cm as cm
import scipy.integrate as integrate
import gpxpy
from datetime import datetime
from xml.etree import ElementTree as ET
from fitparse import FitFile


st.image('NR.png', width = 150)
st.title("Nolan Riding GPS Analysis")

def calculate_hrv_from_hr(heart_rates):
    # Convert HR to approximate IBIs
    ibis = [60000 / hr for hr in heart_rates]
    
    # Calculate successive differences between IBIs
    differences = np.diff(ibis)
    
    # Square the differences
    squared_differences = differences ** 2
    
    # Calculate the mean of the squared differences
    mean_squared_differences = np.mean(squared_differences)
    
    # Take the square root of the mean
    rmssd = np.sqrt(mean_squared_differences)
    
    return rmssd

def read_fit_file_into_dataframe(fit_file_path):
    # Load the FIT file
    fitfile = FitFile(fit_file_path)

    # Prepare a list to hold our data rows
    data_rows = []

    # Iterate over all messages of type "record"
    # (other types include "device_info", "activity", etc.)
    for record in fitfile.get_messages('record'):
        # Convert the record into a dictionary with native values
        data_row = {field.name: field.value for field in record}
        data_rows.append(data_row)

    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(data_rows)

    return df



uploaded_data = st.file_uploader('select file for analysis')

if uploaded_data is not None: 
	datapath = uploaded_data

	path = '/Users/danielgeneau/Documents/Projects/Moutnain Bike GPS/Dan Geneau/11903516635_ACTIVITY.fit'
	df = read_fit_file_into_dataframe(datapath)

	start_time = st.number_input('Segment Start', value = 0)
	end_time = st.number_input('Segment End', value = len(df['timestamp'])-1)


	fig1 = go.Figure()

	fig1.add_trace(go.Scatter(
	    x=df['timestamp'],
	    y=df['enhanced_altitude'],
	    mode='markers',
	    marker=dict(
	        size=3,
	        color=df['enhanced_speed'],  # Set color to velocity
	        colorscale='Jet',  # Choose a color scale
	        #colorbar=dict(title='Velocity (m/s)'),
	        opacity=0.8),
	    name='Altitude'
	))

	# Add the second trace for heart rate data on a separate y-axis
	fig1.add_trace(go.Scatter(
	    x=df['timestamp'],
	    y=df['heart_rate'],
	    mode='lines+markers',  # Use both lines and markers
	    name='Heart Rate',
	    yaxis='y2',  # This specifies that this trace should use the second y-axis
	    fill='tozeroy',  # This will shade the area below the HR line
	    fillcolor='rgba(255, 0, 0, 0.2)',
	    opacity=0.1,  # Adjust the opacity of the HR data
	    marker=dict(
	        size=1,  # Set marker size to 1 for the HR data
	        color='red',  # Set marker color to red
	    ),
	    line=dict(
	        color='red',  # Set line color to red
	    )
	))

	# Update the layout to include a second y-axis on the right side
	fig1.update_layout(
	    yaxis=dict(
	        title='Altitude',
	    ),
	    yaxis2=dict(
	        title='Heart Rate',
	        overlaying='y',  # This places the second y-axis on top of the first one
	        side='right'  # This positions the second y-axis on the right
	    ),
	)

	# Add vertical dotted line for 'start'
	fig1.add_shape(type="line",
	               x0=df['timestamp'][start_time], y0=0, x1=df['timestamp'][start_time], y1=1,
	               line=dict(color="RoyalBlue", width=2, dash="dot"),
	               xref="x", yref="paper")

	# Add vertical dotted line for 'end'
	fig1.add_shape(type="line",
	               x0=df['timestamp'][end_time], y0=0, x1=df['timestamp'][end_time], y1=1,
	               line=dict(color="RoyalBlue", width=2, dash="dot"),
	               xref="x", yref="paper")

	# Add annotation for 'start'
	fig1.add_annotation(x=df['timestamp'][start_time], y=0.05, xref="x", yref="paper",
	                    text="Start", showarrow=False, font=dict(color="RoyalBlue"))

	# Add annotation for 'end'
	fig1.add_annotation(x=df['timestamp'][end_time], y=0.05, xref="x", yref="paper",
	                    text="End", showarrow=False, font=dict(color="RoyalBlue"))

	# Display the plot in Streamlit
	st.plotly_chart(fig1)

	df = df[start_time:end_time].reset_index(drop=True)	
	#display calculations
	HRV = calculate_hrv_from_hr(df['heart_rate'])

	col1, col2, col3, col4 = st.columns(4)
	with col1: 
		st.metric('Total Distance (Km)', round(df['distance'].max()/1000),2)
		st.metric('Average Heart Rate (BPM)', round(df['heart_rate'].mean(),2))
	with col2: 
		st.metric('Top Speed (m/s)', df['enhanced_speed'].max())
		st.metric('Heart Rate Variability', round(HRV, 2))
	with col3: 
		st.metric('Average Speed (m/s)', round(df['enhanced_speed'].mean(),2))
	with col4: 
		st.metric('Minimum Speed (m/s)', round(df['enhanced_speed'].min(),2))




	fig = go.Figure(data=[go.Scatter3d(
		    x=df['position_long'],
		    y=df['position_lat'],
		    z=df['enhanced_altitude'],
		    mode='markers',
		    marker=dict(
		        size=3,
		        color=df ['enhanced_speed'],  # Set color to velocity
		        colorscale='Jet',  # Choose a color scale
		        colorbar=dict(title='Velocity (m/s)'),
		        opacity=0.8
		        ))])
	st.plotly_chart(fig)

else: 
	st.header('Upload FIT File')





