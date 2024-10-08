import pandas as pd
import requests
from datetime import datetime

def get_year(date_str):
    """
    Extracts the year from a date string.

    Parameters:
    date_str (str): A date string in the format "YYYY-MM-DDTHH:MM:SS".

    Returns:
    int: The year extracted from the date string.
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    return date_obj.year

# Define the URL
url = "https://api.economicdata.alberta.ca/api/data?code=ac7407a9-f03b-4132-8024-977480a5ec6e"

# Send a request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON data
    data = response.json()
    
    # Convert the JSON data to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Extract the year from the "Date" column
    df["Date"] = df["Date"].apply(get_year)

    # Make a copy of the unedited DataFrame
    df_unedited = df.copy()
    
    # Save the unedited DataFrame to a CSV file
    df_unedited.to_csv("GDP.csv", index=False)
    
    # Industry mapping
    industry_mapping = {
        'Management of companies and enterprises': 'Business & professional services',
        'Professional, scientific and technical services': 'Business & professional services',
        'Real estate and rental and leasing': 'Construction & construction trades',
        'Finance and insurance': 'Business & professional services',
        'Information and cultural industries': 'Business & professional services',
        'Transportation and warehousing': 'Transportation, communication & utilities',
        'Retail trade': 'Wholesale and retail',
        'Wholesale trade': 'Wholesale and retail',
        'Manufacturing': 'Manufacturing, packaging & processing',
        'Construction': 'Construction & construction trades',
        'Utilities': 'Transportation, communication & utilities',
        'Mining, quarrying, and oil and gas extraction': 'Mining & petroleum development',
        'Agriculture, forestry, fishing and hunting': 'Agriculture & forestry',
        'Administrative and support, waste management and remediation services': 'Business & professional services' ,
        'Educational services': 'Provincial & municipal government, education & health',
        'Health care and social assistance': 'Provincial & municipal government, education & health',
        'Arts, entertainment and recreation': 'Business & professional services',
        'Accommodation and food services': 'Business & professional services',
        'Other services (except public administration)': 'Business & professional services',
        'Public administration': 'Provincial & municipal government, education & health'
    }

    # Apply industry mapping
    df["NAICS Description"] = df["NAICS Description"].replace(industry_mapping)
    
    # Consolidate data
    consolidated_data = df.groupby(['Date', 'NAICS Description'], as_index=False)['Value'].sum()
    
    # Add a LastUpdated column with the current timestamp
    consolidated_data['LastUpdated'] = datetime.now().isoformat()
    
    # Save the consolidated DataFrame to a CSV file
    consolidated_data.to_csv("GDP2.csv", index=False)
    print("Data saved to GDP2.csv successfully.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
