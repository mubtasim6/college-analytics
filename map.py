from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
import logging
import folium

app = FastAPI()

COLLEGE_SCORECARD_BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
API_KEY = "wKw2JBP5ZfNPQUKqchv6KmFI4LgwnUAfQq2N7wfB"

def get_location(school_name: str):
    """
    Shows college locations for colleges specified by user and returns an HTML map.
    """
    params = {
        'api_key': API_KEY,
        'school.name': school_name,
        'fields': 'school.name,location.lat,location.lon',
        'per_page': 100,
    }
    try:
        response = requests.get(COLLEGE_SCORECARD_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info(f"API Response: {response.text}")

        results = data.get("results", [])

        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

        # adding markers for each college
        # how-to: https://python-visualization.github.io/folium/latest/getting_started.html
        for result in results:
            lat = result.get('location.lat')
            lon = result.get('location.lon')
            if lat and lon:
                folium.Marker(
                    [lat, lon],
                    popup=result["school.name"]
                ).add_to(m)

        # exporting to html: https://levelup.gitconnected.com/python-tutorial-on-how-to-use-folium-to-publish-an-interactive-map-31a4120b19c4
        map_html = m._repr_html_()

        return map_html

    except requests.HTTPError as http_err:
        logging.error(f"HTTP Error: {http_err}")
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
