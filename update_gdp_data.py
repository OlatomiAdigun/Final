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
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    
    # Extract the year from the datetime object
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
    
    # Save the DataFrame to a CSV file
    df.to_csv("GDP.csv", index=False)
    print("Data saved to GDP.csv successfully.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
