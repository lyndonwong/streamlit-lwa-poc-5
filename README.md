# Look Now: The Menlo Park Planning Commission

![Menlo Park Cityscape](images/Menlo_Park_960px.jpg)

## Overview

This is a simple, interactive web application built with [Streamlit](https://streamlit.io/) that provides insights into the activities of the Menlo Park Planning Commission. It's designed as a learning tool for those new to Python, data visualization, and Streamlit.

The application visualizes data from the first half of 2025, offering a glimpse into development projects, meeting topics, and commissioner stances in Menlo Park, California.

## Features

*   **Interactive Project Map:** An interactive map (`folium`) showing the locations of development projects. Hover over pins for quick details and click for more information.
*   **Meeting Summaries:** An interactive bar chart (`altair`) summarizing Planning Commission meetings, including duration and topics discussed.
*   **Commissioner Stances:** A color-coded table that provides a "heat map" of each Planning Commissioner's stance on various key issues.
*   **Video Explainers:** Embedded videos offering analysis of the commission's activities for different audiences, including homeowners, renters, and investors.
*   **Detailed Data Tables:** Sortable tables with more in-depth information about meetings, projects, and commissioner positions.
*   **Responsive Design:** The app is designed to work on different screen sizes.

## How to Run the App Locally

To run this application on your local machine, please follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Install the dependencies:**
    Make sure you have Python installed. Then, install the required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    In your terminal, run the following command:
    ```bash
    streamlit run streamlit_app.py
    ```

    The application should now be open in your web browser.

## Data Sources

The data used in this application is contained in the following CSV files:

*   `mppc_highlights_2025-08-28_v4_fix-bullets.csv`: Contains data about the Planning Commission meetings.
*   `mppc_projects_2025-08-28_v2_geocodio_20250901v2_fixes.csv`: Contains information about the development projects, including geocoded locations.
*   `mppc_stances_2025-09-04_v2.csv`: Contains data on the stances and positions of the Planning Commissioners.

This data was collected and processed to be suitable for this demonstration application.

## Screenshots

*(Here you would add screenshots of the application to showcase its features. For example, a screenshot of the interactive map, the charts, and the tables.)*

**Project Map Screenshot:**
`![Project Map](link-to-your-screenshot.png)`

**Meeting Highlights Chart Screenshot:**
`![Meeting Highlights Chart](link-to-your-screenshot.png)`

## Dependencies

This project is built with Python and relies on the following main libraries:

*   [Streamlit](https://streamlit.io/): The core framework for building the web app.
*   [Pandas](https://pandas.pydata.org/): For data manipulation and analysis.
*   [Folium](https://python-visualization.github.io/folium/): For creating the interactive map.
*   [Streamlit-Folium](https://github.com/randyzwitch/streamlit-folium): To integrate Folium maps with Streamlit.
*   [Altair](https://altair-viz.github.io/): For creating declarative statistical visualizations.
*   [Streamlit-Player](https://github.com/tedchou12/streamlit-player): To embed videos in the app.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
