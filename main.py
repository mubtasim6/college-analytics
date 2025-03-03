from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from map import get_location
from api import get_postgrad_stats, read_item
from niche_anlt import analyze_colleges
# from niche_crawler import ...

app = FastAPI()
#router = APIRouter()
app.mount("/static", StaticFiles(directory="/Users/mubi/code/dataWrangling"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    # This function serves the homepage
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>College Information Platform</title>
        <script>
            function redirectToMap() {
                const schoolNameMap = document.getElementById("school_name_map").value;
                window.location.href = `/postgrad-stats/map/?school_name=${encodeURIComponent(schoolNameMap)}`;
                return false; // Prevent form from submitting conventionally
            }
        </script>
        <style>
            .image-caption {
                font-size: small; 
            }
        </style>
    </head>
    <body>
        <h1>Learn more to earn more!</h1>
        <figure>
            <img src="/static/college_earner.jpeg" alt="Graduation Cap on Coins" style="width:100%;max-width:600px;height:auto;">
            <figcaption class="image-caption">Image source: <a href="https://bachelors-completion.northeastern.edu/news/average-salary-by-education-level/">Northeastern University</a></figcaption>
        </figure>
        <p>Explore our features:</p>
        <ul>
            <li><h2><a href="/postgrad-stats/">View Post-graduation Statistics</a></h2></li>
            <li>
                <h3>View College Locations</h3>
                <form onsubmit="return redirectToMap()">
                    <label for="school_name_map">Enter University Name:</label>
                    <input type="text" id="school_name_map" name="school_name_map">
                    <button type="submit">View Map</button>
                </form>
            </li>
            <li><h4><a href="/college-analytics/">View Niche's Top 50 Colleges Ranked By Post-graduation Statistics</a></h4></li>
            <li><h5><a href="/code-snippet/">View Code Snippets</a></h5></li>
        </ul>
    </body>
    </html>
    """

@app.get("/postgrad-stats/", response_class=HTMLResponse)
async def input_school():
    return read_item()

@app.get("/postgrad-stats/results/")
async def display_postgrad_stats(school_name: str):
    stats_html = get_postgrad_stats(school_name)
    return stats_html

@app.get("/postgrad-stats/map/", response_class=HTMLResponse)
async def display_map(school_name: str):
    return get_location(school_name)

@app.get("/college-analytics/", response_class=HTMLResponse)
async def college_analytics():
    #df_preprocessed, top_median_earnings, top_employment_rate, top_graduation_rate, top_confidence_level, non_A_plus_value, top_5_colleges = prepare_data()

    analysis_results = analyze_colleges()#df_preprocessed, top_median_earnings, top_employment_rate, top_graduation_rate,
                                        #top_confidence_level, non_A_plus_value, top_5_colleges)

    # Build HTML content from analysis_results
    content = "<h1>Analytics of Top 50 Colleges</h1>"
    content += "Info gathered from: Niche.com<br><br>Niche.com provides a platform that helps users analyze ratings and reviews of schools, colleges, and neighborhoods by producing rankings, report cards, and profiles"
    content += "<br><br>Niche's homepage: https://www.niche.com/"
    for key, value in analysis_results.items():
        content += f"<div><h2>{key.replace('_', ' ').title()}</h2>{value}</div>"
    return content


@app.get("/code-snippet/", response_class=HTMLResponse)
async def show_code_snippet():
    # Assuming 'niche_crawler.py' is in the current directory
    file_path = os.path.join(os.getcwd(), 'niche_crawler.py')
    with open(file_path, 'r') as file:
        code_content = file.read()

    # Convert the code content to HTML safe content
    code_html = f"<pre><code>{code_content}</code></pre>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Snippet</title>
        <style>
            pre {{
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                overflow: auto;
                width: auto;
                line-height: 1.5;
            }}
            code {{
                font-family: 'Courier New', Courier, monospace;
            }}
        </style>
    </head>
    <body>
        <h1>niche_crawler.py Code Snippet</h1>
        {code_html}
        <a href="/">Back to Home</a>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
