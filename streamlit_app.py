# LWA POC 4 2025-08-11
# Pursues code changes to connect streamlit LWA POC app to Palo Alto CA planning commission data.

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
# add audio stream support
import io
# add video stream support
from streamlit_player import st_player
# add altair charting
import altair as alt

# DEPRECATE for this test
# # Bypass streamlit_folium component, which has bug that causes empty space at bottom of map
# import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.logo("LWA-v2-square.png", size="large")    
st.image("LWA-demo-lab-bar.png", use_container_width=True )
st.title("Look Now: The Palo Alto Planning Commission")

# decorative image of the town
st.image("https://canopy.org/wp-content/uploads/Arial-View-of-Palo-Alto_header-image-.jpg", use_container_width=True)

# Short overview
# [2025-08-25] TO DO: should modify to scan external .md file for this content, instead of hardcoding
st.markdown('''
            ##### Overview of Commission meetings 1H 2025: 
Palo Alto's Planning & Transportation Commission (PTC) focused in 1H 2025 on a range of urban planning and infrastructure topics, including:

+ the redevelopment of opportunity sites for housing and retail
+ addressing parking concerns with new systems and policies
+ updating the bicycle and pedestrian transportation plan
+ and reviewing conditional use permits for specific projects. 

The meetings highlight the PTC's role in making recommendations to the City Council on issues such as affordable housing requirements, traffic safety initiatives, and the future development of key areas like Cubberly and El Camino Real, often involving extensive public and staff input and complex legal and policy considerations.
            ''')

# SUMMARY VISUALIZATIONS ON TOPICS, PROJECTS, COMMISSIONERS

# BAR CHART WITH Meeting Highlights for 1H 2025
st.subheader("Meeting Highlights", anchor="meeting-highlights")

chart_df = pd.read_csv('PAPTC-meeting-metrics_1H2025.csv')
chart_df["Date"] = pd.to_datetime(chart_df["date"])
chart_df["Duration"] = pd.to_numeric(chart_df["duration"], errors='coerce')
chart_df["Topic Count"] = chart_df["topics-discussed"]
chart_df["Topic List"] = chart_df["topics-list"]
chart_df["Youtube link"] = chart_df["youtube-link"]

# DEPRECATED simple streamlit bar chart since this does not support clickable link
# # basic streamlit bar_chart
# st.bar_chart(chart_df, x="date", y="duration", use_container_width=True) 

# ADDED enhanced altair interactive chart
mtg_chart = alt.Chart(chart_df).mark_bar().encode(
    x='date',
    y= 'duration',
    color=alt.value('#A9CCE3'),
    # href='youtube-link',  DEPRECATED for ux reasons
    tooltip=['Date', 'Duration', 'Topic Count', 'Topic List'] # removed "'Youtube link' from list"
).properties(title="Rollover any bar for meeting highlights by date")

st.altair_chart(mtg_chart, use_container_width=True)

st.markdown("[CLICK HERE for Meeting Details](#meeting-details)")

# INTERACTIVE MAP of projects presented to the Planning Commmission
st.subheader("Project Map", anchor="project-map")
st.write("Hover over the pins to see detailed project information. Click on a pin for a popup and to see the project name below.")
st.markdown("[CLICK HERE FOR DETAILS on each project](#project-details)")

# Load the data from the uploaded CSV file
# Ensure the CSV file 'MPPC_projects_1H2025_2025-08-06_map_source.csv' is available in the environment.
try:
    # Using the exact filename provided by the user
    df = pd.read_csv("PAPTC_projects_1H2025_map_table_v2.csv")
except FileNotFoundError:
    st.error("Error: The CSV file 'PAPTC_projects_1H2025_map_table_v2.csv' was not found.")
    st.stop()

# --- Data Preprocessing and Handling Missing Values ---

# Rename columns for easier access (optional, but good practice)
df.rename(columns={
    'Project': 'name',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Address': 'address',
    'City': 'city',
    'Description': 'description',
    'URL': 'url', # 2025-08-06 DEPRECATE until CSV appended
    'First Mention': 'earliest_mention_date', # Renamed
    'Last Mention': 'latest_mention_date'    # Renamed
}, inplace=True)

# Convert latitude and longitude to numeric, coercing errors to NaN
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# Filter out rows where latitude or longitude are missing, as these cannot be plotted
initial_rows = len(df)
df.dropna(subset=['latitude', 'longitude'], inplace=True)
if len(df) < initial_rows:
    st.warning(f"Removed {initial_rows - len(df)} rows due to missing Latitude or Longitude data.")

# Further filter to ensure only Palo Alto projects are shown (if 'City' column exists and is needed)
if 'city' in df.columns:
    df = df[df['city'].astype(str).str.contains('Palo Alto', case=False, na=False)]
    if df.empty:
        st.warning("No projects found for Palo Alto after filtering.")
        st.stop()
else:
    st.warning("The 'City' column was not found in the CSV. Displaying all projects with valid coordinates.")

# Center the map around Palo Alto, CA
# Using the mean of the available Palo Alto coordinates for a more accurate center
if not df.empty:
    map_center = [df['latitude'].mean(), df['longitude'].mean()]
else:
    # Fallback to a default Palo Alto center if no valid data points
    map_center = [37.440848, -122.156314] # Professorville, Palo Alto, CA

# Create a Folium map object
map_height = 800  # Set the height of the map
m = folium.Map(location=map_center, zoom_start=13, height=map_height, control_scale=True)

# Add markers for each location
for idx, row in df.iterrows():
    project_name = row.get('name', 'N/A')
    project_description = row.get('description', 'No description available.')
    street_address = row.get('address', 'N/A')
    public_url = row.get('url')
    earliest_date = row.get('earliest_mention_date', 'N/A') # Get earliest date
    latest_date = row.get('latest_mention_date', 'N/A')   # Get latest date

    # Handle missing URL gracefully
    url_link = ""
    if pd.notna(public_url) and public_url.strip() != '' and public_url.strip().lower() != 'n/a':
        # Ensure URL starts with http:// or https:// for proper linking
        if not public_url.startswith(('http://', 'https://')):
            public_url = 'https://' + public_url # Prepend https if missing
        url_link = f"<br><a href='{public_url}' target='_blank'>More Information</a>"
    else:
        url_link = "<br>No public URL available."

    # Format dates for display, handling potential NaN or 'N/A'
    formatted_earliest_date = str(earliest_date) if pd.notna(earliest_date) and str(earliest_date).strip().lower() != 'n/a' else 'N/A'
    formatted_latest_date = str(latest_date) if pd.notna(latest_date) and str(latest_date).strip().lower() != 'n/a' else 'N/A'

    # Construct the tooltip text with detailed information and the URL link
    # [DEPRECATED] <b>Description:</b> {project_description}<br>
    # [DEPRECATED] {url_link}
    tooltip_html = f"""
    <h4>{project_name}</h4>
    <b>Address:</b> {street_address}<br>
    <b>Earliest Mention:</b> {formatted_earliest_date}<br>
    <b>Latest Mention:</b> {formatted_latest_date}<br>
    <b>Coordinates:</b> ({row['latitude']:.4f}, {row['longitude']:.4f})<br>
    <p><small>Click for more info</small></p>
    """

    # Construct the popup text (appears on click)
    popup_html = f"""
    <b>{project_name}</b><br>
    {project_description}<br>
    <b>Earliest Mention:</b> {formatted_earliest_date}<br>
    <b>Latest Mention:</b> {formatted_latest_date}<br>
    {url_link.replace('<br>', '')}
    """

    # Add a marker with the tooltip and popup
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        tooltip=folium.Tooltip(tooltip_html, sticky=True, max_width=400),
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color='green', icon='info-sign') # Changed icon color and type for San Carlos projects
    ).add_to(m)

# Display the map in Streamlit
# Add st.container and key to st_folium to control rendering
# --- DEPRECATED 8/1/2025 to eliminate empty space bug ---
# --- RESTORED 8/7/2025 to see if folium v 0.25.1 fixes empty space bug
with st.container():
     st_data = st_folium(m, width=900, height=600, key="menlo_park_map")

# --- DEPRECATED 8/1/2025 to simplify functionality of app ---
# st.subheader("Selected Project (on click):")
# if st_data and st_data.get("last_object_clicked_popup"):
#     # Extract the project name from the popup HTML for display
#     clicked_popup_content = st_data['last_object_clicked_popup']
#     # A simple way to get the bolded project name from the popup HTML
#     import re
#     match = re.search(r'<b>(.*?)</b>', clicked_popup_content)
#     if match:
#         st.info(f"You clicked on: {match.group(1)}")
#     else:
#         st.info(f"You clicked on: {clicked_popup_content.split('<br>')[0]}")
# else:
#     st.write("Click on a marker to see its project name here.")

# DEPRECATED 8/7/2025 to try streamlit_folium v. 0.25.1
# # --- RENDER MAP USING st.components.v1.html ---
# # This is a workaround to avoid the empty space issue at the bottom of the map
# # Get raw HTML from the Folium map
# map_html = m._repr_html_()
# # Render the map HTML with st.components.v1.html
# components.html(map_html, height=map_height + 2)

# Instructions to use interactive map
if st.checkbox("Show instructions for interactive map"):
    st.markdown("""
    #### Map Usage Note: 
    - **Hover** over a pin to see its `tooltip` information.
    - **Click** on a pin to see `popup` with more details, including a public URL link when available.
    - Rows with missing Latitude or Longitude values are automatically excluded from the map.
    - If a Public URL or Date information is missing or 'N/A', the relevant field will indicate that.
    - [CLICK HERE FOR DETAILS on each project](#project-details)        
    """)

# COMMISSIONER STANCES AND POSITIONS
# Commissioners policy stances data frame
stances_df = pd.read_csv('PAPTC-commissioner-stances_2025-08-19_v3.csv')

# --- Add this CSS style block to force text color to black ---
st.markdown("""
<style>
    .stDataFrame .css-1qf2o1z p {
        color: #333333 !important; /* A dark gray is often easier on the eyes than pure black */
    }
</style>
""", unsafe_allow_html=True)
# --- End of CSS block ---

# Commissioner Stances heatgrid
st.subheader("Commissioner Stances", anchor="commissioner-stances-heatgrid")
st.markdown("[CLICK HERE for Commissioners' Specific Positions](#commissioner-specific-positions)")

# Detect current theme: "light" or "dark"
theme_type = st.context.theme.type

# display stances columns using st.dataframe for horizontal scrolling
stances_summary_df = stances_df.drop(columns=['Positions'])
# add color-coding on stances (pro, neutral, opposed or mixed)

# DEPRECATED v1 palette
# def highlight_stances(val):
#     color= 'white'
#     if val == 'Pro':
#         color = '#70FA97'
#     elif val == 'Mixed':
#         color = '#B1EAF0'
#     elif val == 'Neutral':
#         color = '#E5FAA0'
#     elif val == 'Opposed':
#         color = '#FFDC78'
#     return f'background-color: {color}'

# v2 palette per ChatGPT suggestions 2025-08-20

# def highlight_stances(val):
#     color= 'white'
#     if val == 'Pro':
#         color = '#D5F5E3'
#     elif val == 'Mixed':
#         color = '#F9E79F'
#     elif val == 'Neutral':
#         color = '#D6EAF8'
#     elif val == 'Opposed':
#         color = '#FAD7A0'
#     return f'background-color: {color}'

# Enable responsive highlight colors for light or dark screen mode.

def highlight_stances(val):
    if theme_type == "dark":
        if val == 'Pro':
            return 'background-color: #27AE60; color: white;'   # darker green
        elif val == 'Mixed':
            return 'background-color: #B7950B; color: white;'   # olive
        elif val == 'Neutral':
            return 'background-color: #2874A6; color: white;'   # medium blue
        elif val == 'Opposed':
            return 'background-color: #CA6F1E; color: white;'   # dark orange
    else:  # light mode
        if val == 'Pro':
            return 'background-color: #D5F5E3; color: black;'   # pastel green
        elif val == 'Mixed':
            return 'background-color: #F9E79F; color: black;'   # pastel yellow
        elif val == 'Neutral':
            return 'background-color: #D6EAF8; color: black;'   # pastel blue
        elif val == 'Opposed':
            return 'background-color: #FAD7A0; color: black;'   # pastel orange
    return ''

styled_stances_df = stances_summary_df.style.applymap(highlight_stances)
st.dataframe(styled_stances_df)

# ANALYSES FROM VARIOUS PERSPECTIVES
st.header("Interpretations")

# # Explainer video
# st.subheader("The Explainer")
# st.write("Your 7 minute video on Palo Alto's real estate investment climate in mid 2025.")
# st_player("https://player.vimeo.com/video/1109170740")

# Select explainers via tabs
tab_homeowners, tab_renters, tab_investors = st.tabs(["For Homeowners", "For Renters", "For Investors"])

with tab_homeowners:
    st.subheader("For Homeowners")
    st.write("A 7-minute video on how 1H 2025 Planning Commission activity may affect homeowners.")
    st_player("https://player.vimeo.com/video/1112595717")

with tab_renters:
    st.subheader("For Renters")
    st.write("A 7-minute video on how 1H 2025 Planning Commission activity may affect renters.")
    st_player("https://player.vimeo.com/video/1112355201")

with tab_investors:
    st.subheader("For Investors")
    st.write("A 7-minute video on how 1H 2025 Planning Commission activity may affect investors.")
    st_player("https://player.vimeo.com/video/1112375299")

# DEPRECATED 8/8/2025
# Somewhat redundant with explainer video. Also a big in the audio file prevents playback
# # Podcast player
# st.subheader("Deep Dive - July 2025 Podcast")
# st.write("Your 5 minute podcast on the big themes and impacts of Menlo Park planning commission actions in 1H 2025")
# try:
#     with open("MPPC_podcast_source.m4a", "rb") as audio_file:
#         audio_bytes = audio_file.read()
#     st.audio(audio_bytes, format="audio/m4a")
# except FileNotFoundError:
#     st.error("Error: The audio file 'MPPC_podcast_source.m4a' was not found. Please ensure the file is in the correct directory.")  

# INFORMATION TABLES WITH MORE DETAILS ON TOPICS, PROJECTS AND COMMISSIONERS

# Meeting Details table
st.subheader("Meeting Details", anchor="meeting-details")
st.markdown("[CLICK HERE for Meeting Highlights](#meeting-highlights)")

# List of columns you want to display
selected_columns = ['Date', 'Duration', 'Topic Count', 'Topic List', 'Youtube link']
# Create a new DataFrame with only the selected columns
df_to_display = chart_df[selected_columns]

# DEPRECATED 2025-08-16
# st.dataframe(df_to_display) 
# use st.table instead, to render markdown in table cells
st.table(df_to_display)

# Show table of Key Projects
st.subheader("Project Details", anchor="project-details")
st.markdown("[CLICK HERE for Project Map](#project-map)")

#columns_to_show = ['Project', 'Address', 'Description', 'First Mention', 'Last Mention']
columns_to_show = ['name', 'address', 'description', 'earliest_mention_date', 'latest_mention_date', 'url']

# st.dataframe(df) # DEPRECATED 2025-08-16
# use st.table instead, to show multi-row description field
st.table(df[columns_to_show])

# COMMISSIONER SPECIFIC POSITIONS
# display subset of columns using st.table for bulleted list in cells
st.subheader("Commissioner Specific Positions", anchor="commissioner-specific-positions")
st.markdown("[CLICK HERE for Commissioner Stances at a glance](#commissioner-stances-heatgrid)")
positions_view = ['Commissioner name', 'Positions']
positions_list_df = stances_df[positions_view]
st.table(positions_list_df)

# DEPRECATED - replaced by above 2 separate tables
# display all columns using st.dataframe for horizontal scrolling
# st.dataframe(stances_df)


# # Planning Commission detailed activity highlights
# DEPRECATED tbd if useful to retain a long-form bullet point narrative summary
# st.subheader("Fine Print")
# st.write("Click the checkbox to dig deeper.")       
# # Get markdown content for the Planning Commission highlights
# def read_markdown_file(file_path):
#     """Reads the content of a markdown file."""
#     with open(file_path, "r", encoding="utf-8") as file:
#         return file.read()

# markdown_content = read_markdown_file("SCPT_1H2025_Milestones.md")

# # Display the markdown content in Streamlit, with user control to show/hide
# if st.checkbox("See Planning Commission 1H 2025 Activity Details"):
#     st.markdown(markdown_content)
