import pandas as pd
import ast

# change df path according to that of df saved after running niche_crawler script
df = pd.read_csv('../../Downloads/colleges_df - colleges_df.csv')

## Preprocessing
# define a function to convert stringified dictionaries into actual dictionaries
def string_to_dict(dict_string):
    # convert to proper dictionary if it's a string representation of a dictionary
    try:
        return ast.literal_eval(dict_string)
    except ValueError:
        return {}

# apply the function to the relevant columns
df['niche_report_card'] = df['niche_report_card'].apply(string_to_dict)
df['after_college'] = df['after_college'].apply(string_to_dict)

# normalize the nested dictionaries into separate columns
df_niche_report_card = df['niche_report_card'].apply(pd.Series)
df_after_college = df['after_college'].apply(pd.Series)

# join the new columns with the main dataframe
df_preprocessed = df.join([df_niche_report_card, df_after_college]).drop(columns=['niche_report_card', 'after_college'])

# ensure that numeric data is actually numeric
df_preprocessed['median_earning_6_years'] = df_preprocessed['median_earning_6_years'].replace('[\$,]', '', regex=True).astype(float)
df_preprocessed['graduation_rate'] = df_preprocessed['graduation_rate'].str.rstrip('%').astype(float) / 100.0
df_preprocessed['employment_rate'] = df_preprocessed['employment_rate'].str.rstrip('%').astype(float) / 100.0
df_preprocessed['confidence_level_percent'] = df_preprocessed['confidence_level_percent'].str.rstrip('%').astype(float) / 100.0

## Analytics: report+plots
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

def plot_to_uri(plt):
    """Converts a matplotlib plot to a URI that can be displayed in HTML."""
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    uri = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return f"data:image/png;base64,{uri}"


# top 5 w highest median earnings
top_median_earnings = df_preprocessed.sort_values(by='median_earning_6_years', ascending=False).head(5)

# top 5 w highest employment rate
top_employment_rate = df_preprocessed.sort_values(by='employment_rate', ascending=False).head(5)

# top 5 w highest graduation rate
top_graduation_rate = df_preprocessed.sort_values(by='graduation_rate', ascending=False).head(5)

# top 5 w highest confidence levels
df_preprocessed['confidence_level_responses'] = df_preprocessed['confidence_level_responses'].astype(int)
top_confidence_level = df_preprocessed[df_preprocessed['confidence_level_responses'] >= 15].sort_values(by='confidence_level_percent', ascending=False).head(5)

# colleges w lower grades for 'Value'
non_A_plus_value = df_preprocessed[(df_preprocessed['Value'] != 'A+') & (df_preprocessed['Value'] != 'A')]


# 1. Bar Plot: Median Earnings after 6 years for each college
def generate_median_earnings_plot(df_preprocessed):
    plt.figure(figsize=(8, 10))
    sns.barplot(x='median_earning_6_years', y='College name', data=df_preprocessed)
    plt.title('Median Earnings After 6 Years by College')
    plt.xlabel('Median Earnings ($)')
    plt.ylabel('College')
    # convert plot to URI and return
    return plot_to_uri(plt)

# 2. Scatter plot: Median Earnings vs graduation rate
def generate_median_earnings_trend(df_preprocessed):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(x='graduation_rate', y='median_earning_6_years', data=df_preprocessed, marker='o')
    sns.regplot(x='graduation_rate', y='median_earning_6_years', data=df_preprocessed, scatter=False, color='red', lowess=True, line_kws={'label': 'LOWESS Curve'})
    plt.title('Median Earnings vs Graduation Rates')
    plt.xlabel('Graduation Rate')
    plt.xticks(rotation=45, ha='right')
    plt.xlim(0.75, 1)
    plt.ylabel('Median Earnings')
    plt.ylim(40000, 120000)
    return plot_to_uri(plt)

# 3. Pie Chart: Distribution of 'Value' ratings among the colleges
def generate_niche_value_ratings(df_preprocessed):
    academics_counts = df_preprocessed['Value'].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(academics_counts, labels=academics_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Value Ratings Among Colleges')
    return plot_to_uri(plt)

# 4. Histogram: Distribution of 'confidence_level_percent'
def generate_confidence_level_distribution(df_preprocessed):
    plt.figure(figsize=(10, 6))
    sns.histplot(df_preprocessed['confidence_level_percent'], bins=10, kde=True)
    plt.title('Distribution of Confidence Level Percent')
    plt.xlabel('Confidence Level Percent')
    plt.ylabel('Frequency')
    return plot_to_uri(plt)

# 5. Line Plot: Employment Rate Trends across the Colleges
def generate_employment_rate_boxplot(df_preprocessed):
    plt.figure(figsize=(8, 6))
    sns.boxplot(y=df_preprocessed['employment_rate'])
    plt.title('Overall Employment Rate Distribution Across Colleges')
    plt.ylabel('Employment Rate')
    plt.ylim(0.8, 1)
    return plot_to_uri(plt)

# combine the college names from all lists into one Series
all_colleges = pd.concat([
    top_median_earnings['College name'],
    top_employment_rate['College name'],
    top_graduation_rate['College name'],
    top_confidence_level['College name']
])

# count the frequency of each college name
college_counts = all_colleges.value_counts()

# get the top 3 most frequent college names
top_3_colleges = college_counts.head(3)

# function to group all results and plots
def analyze_colleges():
    # generate plots and convert to URIs
    med_earnings_uri = generate_median_earnings_plot(top_median_earnings)
    med_earnings_gr_uri = generate_median_earnings_trend(df_preprocessed)
    value_dist_uri = generate_niche_value_ratings(df_preprocessed)
    confidence_hist_uri = generate_confidence_level_distribution(df_preprocessed)
    box_plot_uri = generate_employment_rate_boxplot(df_preprocessed)

    # incorporate the plots into the analysis_results dictionary with other analyses
    analysis_results = {
        "top_median_earnings": top_median_earnings[["College name", "median_earning_6_years"]].to_html(escape=False),
        "top_employment_rate": top_employment_rate[["College name", "employment_rate"]].to_html(escape=False),
        "top_graduation_rate": top_graduation_rate[["College name", "graduation_rate"]].to_html(escape=False),
        "top_confidence_level": top_confidence_level[["College name", "confidence_level_percent"]].to_html(escape=False),
        "non_A_plus_value": non_A_plus_value[["College name", "Value"]].to_html(escape=False),
        "median_earnings_bar_plot": f'<img src="{med_earnings_uri}" alt="Median Earnings Bar Plot">',
        "median_earnings_trend_plot": f'<img src="{med_earnings_gr_uri}" alt="Median Earnings vs. Graduation Rate">',
        "value_ratings_plot": f'<img src="{value_dist_uri}" alt="Value Ratings Distribution (Niche)">',
        "confidence_hist_plot": f'<img src="{confidence_hist_uri}" alt="Distribution of Confidence Level (%)">',
        "box_plot": f'<img src="{box_plot_uri}" alt="Employment Rate Trends">',
        "colleges_with_the_best_post-graduation_metrics": top_3_colleges.to_frame().to_html(header=False, escape=False)
    }
    return analysis_results
