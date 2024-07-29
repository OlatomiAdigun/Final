import pandas as pd
from stats_can import StatsCan

# Initialize StatsCan and retrieve data
sc = StatsCan()
df = sc.table_to_df("14-10-0023-01")

# Select relevant columns
df = df[[
    "REF_DATE", 
    "Labour force characteristics", 
    "North American Industry Classification System (NAICS)", 
    "Sex", 
    "Age group", 
    "UOM",
    "SCALAR_FACTOR", 
    "VALUE", 
    "GEO"
]]

# Filter data for 'Labour force' characteristics and Alberta
df = df[df["Labour force characteristics"] == "Labour force"]
df = df[df["GEO"] == 'Alberta']

# Dictionary to rename columns
column_rename_dict = {
    'REF_DATE': 'Year',
    'North American Industry Classification System (NAICS)': 'Industry',
    'VALUE': 'Labour force value'
}

# Rename columns according to the dictionary
df.rename(columns=column_rename_dict, inplace=True)

# Ensure 'UOM' and 'SCALAR_FACTOR' are treated as strings
df['UOM'] = df['UOM'].astype(str)
df['SCALAR_FACTOR'] = df['SCALAR_FACTOR'].astype(str)

# Combine 'SCALAR_FACTOR' and 'UOM' into a new column 'Units'
df['Units'] = df['SCALAR_FACTOR'] + ' ' + df['UOM']

# Drop columns that are no longer needed
df.drop(columns=['Labour force characteristics', 'UOM', 'SCALAR_FACTOR', 'GEO'], inplace=True)

# Convert 'Year' column from datetime to just the year
df['Year'] = pd.to_datetime(df['Year']).dt.year

# Remove everything within square brackets (and the brackets themselves) from 'Industry'
df['Industry'] = df['Industry'].str.replace(r'\[.*?\]', '', regex=True).str.strip()

# List of industries to keep
industries_to_keep = [
    'Agriculture',
    'Utilities',
    'Construction',
    'Manufacturing',
    'Wholesale and retail trade',
    'Transportation and warehousing',
    'Finance, insurance, real estate, rental and leasing',
    'Professional, scientific and technical services',
    'Business, building and other support services',
    'Educational services',
    'Health care and social assistance',
    'Information, culture and recreation',
    'Accommodation and food services',
    'Other services (except public administration)',
    'Public administration',
    'Forestry and logging and support activities for forestry',
    'Fishing, hunting and trapping',
    'Mining, quarrying, and oil and gas extraction'
]

# Filter the DataFrame to keep only rows where the 'Industry' column is in the list
df = df[df['Industry'].isin(industries_to_keep)]

# Define the mapping dictionary
industry_sector_mapping = {
    'Agriculture': 'Agriculture & forestry',
    'Utilities': 'Transportation, communication & utilities',
    'Construction': 'Construction & construction trades',
    'Manufacturing': 'Manufacturing, packaging & processing',
    'Wholesale and retail trade': 'Wholesale and retail',
    'Transportation and warehousing': 'Transportation, communication & utilities',
    'Finance, insurance, real estate, rental and leasing': 'Business & professional services',
    'Professional, scientific and technical services': 'Business & professional services',
    'Business, building and other support services': 'Business & professional services',
    'Educational services': 'Provincial & municipal government, education & health',
    'Health care and social assistance': 'Provincial & municipal government, education & health',
    'Information, culture and recreation': 'Business & professional services',
    'Accommodation and food services': 'Business & professional services',
    'Other services (except public administration)': 'Business & professional services',
    'Public administration': 'Provincial & municipal government, education & health',
    'Forestry and logging and support activities for forestry': 'Agriculture & forestry',
    'Mining, quarrying, and oil and gas extraction': 'Mining & petroleum development'
}

df['Sector'] = df['Industry'].map(industry_sector_mapping)

# Group by Year, Sector, Sex, Age group and sum Labour force value
grouped_df = df.groupby(['Year', 'Sector', 'Sex', 'Age group'], as_index=False)['Labour force value'].sum()

# Save the cleaned DataFrame to a CSV file
grouped_df.to_csv('labourforce.csv', index=False)
print("Data saved to labourforce.csv successfully.")
