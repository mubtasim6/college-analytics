from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
import logging

# Html code generated with help of ChatGPT
def read_item():
    """
    Serve the HTML page.
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Postgraduate Statistics</title>
</head>
<body>
    <h1>Post-graduation Statistics</h1>
    <form id="postgrad-form">
        <label for="school_name">Enter University Name:</label>
        <input type="text" id="school_name" name="school_name">
        <button type="submit">Get Statistics</button>
    </form>
    <div id="result"></div>

    <script>
        document.getElementById("postgrad-form").addEventListener("submit", function(event) {
            event.preventDefault();
            const schoolName = document.getElementById("school_name").value;
            fetch(`/postgrad-stats/results/?school_name=${encodeURIComponent(schoolName)}`)
                .then(response => response.json())
                .then(data => {
                    let resultHTML = "";
                    if (data.college && data.college.length > 0) {
                        data.college.forEach((college) => {
                            resultHTML += `<p>School Name: ${college.school_name}</p>`;
                            resultHTML += `<p>State: ${college.state}</p>`;
                            resultHTML += `<p>Median Earnings 10 Years After Entry: ${college.median_earnings_10_years || 'Data not available'}</p>`;
                            // Use inline CSS for color coding based on earnings recommendation
                            const color = college.earnings_recommendation === "High" ? "green" : 
                                      college.earnings_recommendation === "Medium" ? "yellow" : 
                                      "red";
                            resultHTML += `<p>Earnings Recommendation: <span style="color: ${color};">${college.earnings_recommendation}</span></p>`;
                            resultHTML += `<p>% of Students Repaying Loans 3 Years After Entry: ${college.loan_repayment_rate}</p>`;
                            resultHTML += "<hr>"; // Add a horizontal line between colleges
                        });
                        // Add a button for viewing the map
                        resultHTML += `<button onclick="location.href='/postgrad-stats/map/?school_name=${encodeURIComponent(schoolName)}'">View Map</button>`;
                    } else {
                        resultHTML = "<p>No results found for the given university name.</p>";
                    }
                    document.getElementById("result").innerHTML = resultHTML;
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById("result").innerHTML = `<p>Error fetching data: ${error}</p>`;
                });
        });
    </script>


</body>
</html>
"""

COLLEGE_SCORECARD_BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
API_KEY = "wKw2JBP5ZfNPQUKqchv6KmFI4LgwnUAfQq2N7wfB"

def determine_earnings_recommendation(median_earnings):
    if median_earnings is None:
        return "Data not available"
    elif median_earnings > 75000:
        return "High"
    elif 30000 < median_earnings <= 75000:
        return "Medium"
    else:
        return "Low"

def get_postgrad_stats(school_name: str):
    """
    Fetches post-graduation statistics for colleges specified by user.
    """
    params = {
        'api_key': API_KEY,
        'school.name': school_name,  # Use the original case for better matching
        'fields': 'id,school.name,school.state,latest.earnings.10_yrs_after_entry.median,'
                  'latest.repayment.3_yr_repayment_suppressed.overall,'
                  'latest.completion.rate_suppressed.four_year_150nt',
        'per_page': 100,  # Adjust based on how many results you want per page
    }
    try:
        response = requests.get(COLLEGE_SCORECARD_BASE_URL, params=params)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx errors
        data = response.json()
        logging.info(f"API Response: {response.text}")

        # Process and return the results
        colleges = []
        for result in data.get("results", []):
            loan_repayment = result.get("latest.repayment.3_yr_repayment_suppressed.overall")
            loan_repayment_rate = "Data not available"  # Default text if data is not available
            if loan_repayment is not None:
                loan_repayment = float(loan_repayment)*100 # x100 to convert value into %
                # Format the loan repayment rate to 3 significant figures with a percentage sign
                loan_repayment_rate = f"{loan_repayment:.3g}%"

            colleges.append({
                "school_name": result["school.name"],
                "state": result["school.state"],
                "median_earnings_10_years": result.get("latest.earnings.10_yrs_after_entry.median"),
                "earnings_recommendation": determine_earnings_recommendation(
                    result.get("latest.earnings.10_yrs_after_entry.median")
                ),
                "loan_repayment_rate": loan_repayment_rate,
            })

        return {"college": colleges}

    except requests.HTTPError as http_err:
        logging.error(f"HTTP Error: {http_err}")
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
