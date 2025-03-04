from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from map import get_location
from api import get_postgrad_stats, read_item
from niche_anlt import analyze_colleges

app = FastAPI()
app.mount("/static", StaticFiles(directory="/Users/mubi/code/dataWrangling"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    # this function serves the homepage
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
                font-size: medium; 
            }
            .explore-heading {
                font-size: 1.2em; /* Slightly larger */
            }
            .author {
                font-style: italic;
                font-size: 0.9em;
                color: #555;
            }
            .footer {
                font-size: 0.9em;
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                color: #666;
                border-top: 1px solid #ddd;
            }
        </style>
    </head>
    <body>
        <h1>College Information Platform</h1>
        <p class="author">Mubtasim H Talha</p>

        <figure>
            <img src="/static/college_earner.jpeg" alt="Graduation Cap on Coins" style="width:100%;max-width:600px;height:auto;">
            <figcaption class="image-caption">Image source: <a href="https://bachelors-completion.northeastern.edu/news/average-salary-by-education-level/">Northeastern University</a></figcaption>
        </figure>

        <h2>Lesson from analytics: Learn more to earn more!</h2>
        <p class="explore-heading">Explore the following features for elaboration:</p>
        <ul>
            <li><h3><a href="/postgrad-stats/">View Post-graduation Statistics</a></h3></li>
            <li>
                <h3>View College Locations</h3>
                <form onsubmit="return redirectToMap()">
                    <label for="school_name_map">Enter University Name:</label>
                    <input type="text" id="school_name_map" name="school_name_map">
                    <button type="submit">View Map</button>
                </form>
            </li>
            <li><h3><a href="/college-analytics/">View Niche's Top 50 Colleges Ranked By Post-graduation Statistics</a></h3></li>
            <li><h3><a href="/code-snippet/">View Code Snippets</a></h3></li>
        </ul>

        <div class="footer">
            Developed for UOP's Data Wrangling course project
        </div>
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
    analysis_results = analyze_colleges()

    # build html content from analysis_results
    content = "<h1>Analytics of Top 50 Colleges</h1>"
    content += "Info gathered from: Niche.com<br><br>Niche.com provides a platform that helps users analyze ratings and reviews of schools, colleges, and neighborhoods by producing rankings, report cards, and profiles"
    content += "<br><br>Niche's homepage: https://www.niche.com/"
    for key, value in analysis_results.items():
        content += f"<div><h2>{key.replace('_', ' ').title()}</h2>{value}</div>"
    return content


@app.get("/code-snippet/", response_class=HTMLResponse)
async def show_code_snippet():
    # ensure 'niche_crawler.py' is in current dir
    file_path = os.path.join(os.getcwd(), 'niche_crawler.py')
    with open(file_path, 'r') as file:
        code_content = file.read()

    # convert the code content to html safe content
    code_html = f"""
    <pre><code class="language-python">{code_content}</code></pre>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Snippet</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            pre {{
                padding: 15px;
                border-radius: 5px;
                overflow: auto;
                font-size: 1.1em;
            }}
            code {{
                font-size: 1.1em;
            }}
            .hljs-comment {{
                color: #5DADE2 !important; /* light blue for comments */
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
