import re
import pandas as pd
from PyPDF2 import PdfReader
import warnings

# Suppress specific FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Your code here


# Set display options to show all columns
pd.set_option('display.max_columns', None)

sector_names=['Agriculture & forestry', 'Business & professional services', 'Construction & construction trades', 'Provincial & municipal government, education & health', 'Manufacturing, packaging & processing', 'Mining & petroleum development', 'Transportation, communication & utilities', 'Wholesale and retail']


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def sort_dict(input_dict):
    sorted_dict = {k: v for k, v in sorted(input_dict.items(), key=lambda item: item[1], reverse=True)}
    return sorted_dict

def nos_btw_21_and_32(string_list):
    result = []
    for string in string_list:
        numbers = re.findall(r'\b(?:2[1-9]|[3][0-2])\b', string)
        result.extend(map(int, numbers))
    return result

def nos_btw_21_and_31(string_list):
    result = []
    for string in string_list:
        numbers = re.findall(r'\b(?:2[1-9]|[3][0-1])\b', string)
        result.extend(map(int, numbers))
    return result

def nos_btw_23_and_29(string_list):
    result = []
    for string in string_list:
        numbers = re.findall(r'\b(?:2[3-9])\b', string)
        result.extend(map(int, numbers))
    return result

def find_age_groups(text):
    # Define the regular expression patterns for the age groups
    pattern = r'\b\d+-\d+\b|\b\d+\+\b'
    
    # Find all matches in the text
    age_groups = re.findall(pattern, text)
    
    return age_groups

def extract_age_group_percentages(text):
    age_groups = find_age_groups(text)
    age_group_percent = {}

    if len(age_groups) == 1:
        # First pattern to search for percentage
        match = re.search(r'%\n{0,1}(\d{2})%\n\d{1,2}%\n\s{1,6}male', text)
        if not match:
            # Second pattern if no value is found
            match = re.search(r'(\d{1,2})%.*?\n\d{1,2}%.*?\n{0,1}\d{2}%\n\d{1,2}%\n\s{1,6}male', text)
        if not match:
            # Third pattern if still no value is found
            match = re.search(r'(\d*)%Injuries by gender', text)

        if match:
            age_group_percent[age_groups[0]] = match.group(1)

    elif len(age_groups) == 2:
        # Pattern to search for percentages for two age groups
        match = re.search(r'\n(\d{1,2})%.*?\n\d{1,2}%.*?\n\d{1,2}%\n(\d{1,2})%\d{1,2}-\d{1,2}\nyears\n\d{1,2}All fatality', text)
        
        if match:
            age_group_percent[age_groups[0]] = match.group(1)
            age_group_percent[age_groups[1]] = match.group(2)

    return age_group_percent

def extract_age_percent_2018(file_text):
    try:
        agegroup = re.findall(r'\s?(\d+-\d+)', file_text)
        percent = re.findall(r'(\d+)%', re.findall(r'were injured\n?([\s\S]+?)All numbers', file_text)[0])
        percent=nos_btw_21_and_32(percent)
    
        result = {age: per for age, per in zip(agegroup, percent)}
    except Exception as e:
        result = None
    return result

def extract_age_percent_2019(file_text):
    try:
        agegroup = re.findall(r'\s?(\d+-\d+)', file_text)
        percent = re.findall(r'(\d+)%', re.findall(r'were injured\n?([\s\S]+?)All numbers', file_text)[0])
        percent= nos_btw_21_and_31(percent)
        
        if percent==[]:            
            percent= list(re.findall(r'All numbers are based on the year of the fatality.*?\n.*?\n.*?\n(\d+)%\n.*?\n?.*?(\d+)%', file_text)[0])   
       
            percent=nos_btw_21_and_31(percent)
            if len(percent)>1:
                percent= [max(percent)]

        if len(agegroup)==2 and len(percent)==1:
            percent=percent*2   
        result = {age: per for age, per in zip(agegroup, percent)}
    except Exception as e:
        result = None
    return result

def extract_age_percent_2020(file_text):
    try:
        agegroup = re.findall(r'\s?(\d+-\d+)', file_text)
        percent = re.findall(r'(\d+)%', re.findall(r'were injured\n?([\s\S]+?)All numbers', file_text)[0])
        percent= nos_btw_23_and_29(percent)
        
        if percent==[]:            
            percent= list(re.findall(r'All numbers are based on the year of the fatality.*?\n.*?\n.*?\n(\d+)%\n.*?\n?.*?(\d+)%', file_text)[0])   
       
            percent=nos_btw_21_and_31(percent)

        if len(agegroup)==2 and len(percent)==1:
            percent=percent*2   
        result = {age: per for age, per in zip(agegroup, percent)}
    except Exception as e:
        result = None
    return result

def get_parts(matches):
    return {
            matches[0][0].strip().replace('\n', ''): int(matches[0][1]),
            matches[0][2].strip().replace('\n', ''): int(matches[0][3]),
            matches[0][4].strip().replace('\n', ''): int(matches[0][5])
        }


def extract_common_injuries_2018(file_text,sector_abb):
    commonly_injured_parts = None

    matches = re.findall(r'were injured\n(.*?\n.*?\n.*?\n)(\d+)%\n(.*?)\n(\d+)%\n(.*?\n.*?\n)(\d+)%', file_text)
    if matches and len(matches[0]) == 6:
        commonly_injured_parts = get_parts(matches)
    else:
        matches = re.findall(r'injured\n(.*?\n?.*?)\n(\d+)%(.*?\n.*?\n?.*?)\n(\d+)%', file_text)
        matches.extend(re.findall(r'fatality.(.*?\n.*?\n.*?)\n(\d+)%', file_text))
        matches= [sum(matches,())]
        if matches and len(matches[0]) == 6 and sector_abb.lower() !='trans':
            commonly_injured_parts = get_parts(matches)
        else:
            matches = re.findall(r'were injured\n(.*?\n.*?\n.*?\n)(\d+)%\n', file_text)
            matches.extend(re.findall(r'fatality.(.*?)\n(\d+)%(.*?\n.*?\n.*?)\n(\d+)%', file_text))
            matches= [sum(matches,())]
            if matches and len(matches[0]) == 6:
                commonly_injured_parts = get_parts(matches)
            else:
                matches = re.findall(r'injured\n\d+?%(.*?\n.*?\n.*?)\n(\d+)%(.*?\n.*?)\n(\d+)%\n', file_text)
                matches.extend(re.findall(r'fatality.(.*?\n.*?\n.*?)\n(\d+)%', file_text))
                matches= [sum(matches,())]
                if matches and len(matches[0]) == 6:
                    commonly_injured_parts = get_parts(matches)
                else:
                    matches = re.findall(r'injured(.*?\n.*?)\n(\d+)%\n(.*?\n.*?\n.*?)\n(\d+)%', file_text)
                    matches.extend(re.findall(r'fatality.(.*?\n.*?\n.*?)\n(\d+)%', file_text))
                    matches= [sum(matches,())]
                    if matches and len(matches[0]) == 6:
                        commonly_injured_parts = get_parts(matches)
                    else:
                        matches = re.findall(r'were injured\n(.*?)\n(\d+)%\n', file_text)
                        matches.extend(re.findall(r'fatality.(.*?\n.*?\n.*?)\n(\d+)%(.*?\n.*?\n.*?)\n(\d+)%', file_text))
                        matches= [sum(matches,())]
                        if matches and len(matches[0]) == 6:
                            commonly_injured_parts = get_parts(matches)
                        else:
                            matches = re.findall(r'were injured\n\d+%(.*?\n.*?\n.*?)\n(\d+)%\n', file_text)
                            matches.extend(re.findall(r'fatality.(.*?\n.*?)\n(\d+)%\n(.*?\n.*?\n.*?)\n(\d+)%', file_text))
                            matches= [sum(matches,())]
                            if matches and len(matches[0]) == 6:
                                step = 7
                                matches = [sum(matches, ())]
                                commonly_injured_parts = get_parts(matches)


    return commonly_injured_parts


def extract_common_injuries_2019(file_text,sector_abb):
    commonly_injured_parts = None

    matches = re.findall(r'workers were injured\n(.*?\n.*?\n.*?)\n(\d+)%\n(.*?)\n(\d+)%(.*?\n.*?)\n(\d+)%', file_text)
    if matches and len(matches[0]) == 6:
        commonly_injured_parts = get_parts(matches)
    else:
        matches = re.findall(r'injured\n(.*?\n?.*?)\n(\d+)%(.*?\n.*?\n?.*?)\n(\d+)%', file_text)
        matches.extend(re.findall(r'fatality.(.*?\n.*?\n.*?)\n(\d+)%', file_text))
        matches= [sum(matches,())]
        if matches and len(matches[0]) == 6 and sector_abb.lower() !='trans':
            commonly_injured_parts = get_parts(matches)

        else:
            matches = re.findall(r'were injured\n(.*?)\n(\d+)%\n', file_text)
            matches.extend(re.findall(r'fatality.(.*?\n.*?\n.*?)\n(\d+)%(.*?\n.*?\n.*?)\n(\d+)%', file_text))
            matches= [sum(matches,())]
            if matches and len(matches[0]) == 6:
                commonly_injured_parts = get_parts(matches)
            else:
                matches = re.findall(r'were injured\n\d+%(.*?\n.*?\n.*?)\n(\d+)%\n', file_text)
                matches.extend(re.findall(r'fatality.(.*?\n.*?)\n(\d+)%\n(.*?\n.*?\n.*?)\n(\d+)%', file_text))
                matches= [sum(matches,())]
                if matches and len(matches[0]) == 6:
                    matches = [sum(matches, ())]
                    commonly_injured_parts = get_parts(matches)

                else:
                    matches = re.findall(r'were injured\n(.*?\n.*?\n.*?)\n(\d+)%\n(.*?)\n(\d+)%', file_text)
                    matches.extend(re.findall(r'fatality.(.*?\n.*?\n.*?)\n(\d+)%',file_text))
                    matches= [sum(matches,())]

                    if matches and len(matches[0]) == 6:
                        commonly_injured_parts = get_parts(matches)
                    else:
                        matches = re.findall(r'were injured(.*?\n.*?)\n(\d+)%', file_text)
                        matches.extend(re.findall(r'fatality.(.*?)\n(\d+)%(.*?\n.*?\n.*?)\n(\d+)%',file_text))
                        matches= [sum(matches,())]

                        if matches and len(matches[0]) == 6:
                            commonly_injured_parts = get_parts(matches)



    return commonly_injured_parts

def extract_common_injuries_2020(file_text,sector_abb):
    commonly_injured_parts = None

    matches = re.findall(r'were injured\n(.*?\n.*?\n.*?)\n(\d+)%\n(.*?)\n(\d+)%(.*?\n.*?)\n(\d+)%', file_text)
    if matches and len(matches[0]) == 6:
        commonly_injured_parts = get_parts(matches)
    else:
        matches = re.findall(r'injured\n(.*?\n?.*?\n?.*?)\n(\d+)%\n?(.*?\n?.*?\n?.*?)\n(\d+)%\n\d+-?',file_text)
        matches.extend(re.findall(r'([A-Z].*?\n.*?\n.*?)\n(\d+)%\n\d?\d?-?\d?\d?\s?\n?.*?\d?\d?%?\n?Data', file_text))
        matches= [sum(matches,())]
        if matches and len(matches[0]) == 6 and sector_abb.lower() !='trans':
            commonly_injured_parts = get_parts(matches)

        else:
            matches = re.findall(r'injured\n?\d?\d?%?(.*?)\n(\d+)%\n',file_text)
            matches.extend(re.findall(r'gender\n?([A-Z].*?\n?.*?\n?.*?)\n(\d+)%\n?([A-Z].*?\n.*?\n?.*?)\n(\d+)%', file_text))
            matches= [sum(matches,())]
            if matches and len(matches[0]) == 6:
                commonly_injured_parts = get_parts(matches)
    return commonly_injured_parts



def get_data_2017():
    # Initialize lists to store data from each file
    data = []

    # Iterate over file names
    for file in sector_names:
        # Extract text from PDF
        file_text = extract_text_from_pdf('2017/'+file[0:5] + "_2017.pdf")
        
        # Extract workers died
        match = re.search(r'Alberta\.(\d+)\nNumber of \nworkers \nwho died1', file_text)
        workers_died = int(match.group(1)) if match else None
        
        # Extract workers injured
        match = re.search(r'\n\d{1,2}Workplace incidents(\d{1,3}(?:,\d{3})?)\nInjury', file_text)
        workers_injured = int(match.group(1).replace(',', '')) if match else None
        
        # Extract injuries by gender
        match = re.search(r'(\d{1,2})%\n\s{1,6}male\s{0,1}(\d{1,3})%\n\s{1,4}female', file_text)
        if match:
            male_percentage = int(match.group(1))
            female_percentage = int(match.group(2))
            injuries_by_gender = {'male': male_percentage, 'female': female_percentage}
        else:
            injuries_by_gender = None
        
        # Extract age with highest injury claims  
        # match = re.search(r'(\d+-\d+|\d+\+)\s*year olds\n([0-9]+\.[0-9]+)\s*per 100 person-years', file_text)
        # match = re.search(r'%\n{0,1}(\d{2})%\n\d{1,2}%\n\s{1,6}male', file_text)
        # match= re.search(r'\nclaims (.*?) \nyearsWorkplace injuries', file_text)
        age_highest_injury_claims = extract_age_group_percentages(file_text) if match else None
        
        # Extract commonly injured parts
        # file_text= file_text.replace('\n','')
        pattern = r'\n100 workers were injured\n(.*?)\n(\d{1,2})%\n?\d{0,2}%?(.*?)\n(\d{1,2})%\n?(.*?)\n(\d{1,2})%'


        matches = re.findall(pattern, file_text)
        commonly_injured_parts = {
            matches[0][0].strip(): int(matches[0][1]),
            matches[0][2].strip(): int(matches[0][3]),
            matches[0][4].strip(): int(matches[0][5])
        } if matches else None
        if commonly_injured_parts:
            commonly_injured_parts= sort_dict(commonly_injured_parts)
        # Extract top three causes of injuries
        pattern = r'workers\s\n(.*?)\s{1,3}(\d+)%\n(.*?)\s(\d+)%\n(.*?)\s{1,5}(\d+)%Common'
        matches = re.findall(pattern, file_text)
        
        if matches:
            top_three_causes = {
                matches[0][0].strip(): int(matches[0][1]),
                matches[0][2].strip(): int(matches[0][3]),
                matches[0][4].strip(): int(matches[0][5])
            } if matches else None
        
        
        # Extract common types of injuries
        pattern = r'injuries\n(.*?)(\d+)%\n(.*?)(\d+)%\n(.*?)(\d+)%Commonly'

        matches = re.findall(pattern, file_text)
        common_types_of_injuries = {
            matches[0][0].strip(): int(matches[0][1]),
            matches[0][2].strip(): int(matches[0][3]),
            matches[0][4].strip(): int(matches[0][5])
        } if matches else None
        
        # Append extracted data to the list
        data.append({
            'Sector': file,
            'no_dead_workers': workers_died,
            'no_injured_workers': workers_injured,
            'injuries_by_gender': injuries_by_gender,
            'age_with_highest_injury_claims': age_highest_injury_claims,
            'commonly_injured_parts': commonly_injured_parts,
            'top_three_causes': top_three_causes,
            'common_types_of_injuries': common_types_of_injuries
        })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df.insert(0, 'year', 2017)
    return df

def get_data_2018():
    # Initialize lists to store data from each file
    data = []

    # Iterate over file names
    for file in sector_names:
        # Extract text from PDF
        file_text = extract_text_from_pdf('2018/' + file[0:5] + "_2018.pdf")
        
        # Extract workers died
        match = re.search(r'Alberta\.(\d+)\nNumber of \nworkers \nwho died1', file_text)
        workers_died = int(match.group(1)) if match else None
        
        # Extract workers injured
        match = re.search(r'\n\d{1,2}Workplace incidents(.*?)\n[Ii]njury', file_text)
        workers_injured = int(match.group(1).replace(',', '')) if match else None
        
        # Extract injuries by gender
        match = re.search(r'(\d{1,2})%\n?\s{1,6}male\s{0,1}(\d{1,3})%\n\s{1,4}female', file_text)
        if match:
            male_percentage = int(match.group(1))
            female_percentage = int(match.group(2))
            injuries_by_gender = {'male': male_percentage, 'female': female_percentage}
        else:
            injuries_by_gender = None
        
        # Extract age with highest injury claims  
        

        age_highest_injury_claims = extract_age_percent_2018(file_text) 
        
        # Extract commonly injured parts
        commonly_injured_parts=extract_common_injuries_2018(file_text, sector_abb=file[0:5])
        commonly_injured_parts= sort_dict(commonly_injured_parts)
        
        # Extract top three causes of injuries
        pattern = r'workers\s\n(.*?)\s{1,3}(\d+)%\n(.*?)\s(\d+)%\n(.*?)\s{1,5}(\d+)%Common'
        matches = re.findall(pattern, file_text)
        
        if matches:
            top_three_causes = {
                matches[0][0].strip(): int(matches[0][1]),
                matches[0][2].strip(): int(matches[0][3]),
                matches[0][4].strip(): int(matches[0][5])
            } if matches else None
        
        
        # Extract common types of injuries
        pattern = r'injuries\n(.*?\n?.*?)(\d+)%\n(.*?\n?.*?)(\d+)%\n(.*?\n?.*?)(\d+)%\s?Commonly'
        matches = re.findall(pattern, file_text)
        if matches:
            common_types_of_injuries = {
                matches[0][0].strip(): int(matches[0][1]),
                matches[0][2].strip(): int(matches[0][3]),
                matches[0][4].strip(): int(matches[0][5])
            }
        else: 
            matches = re.findall(r'(\d+)%\n(\d+)%Common types of injuries \n(.*?)\s{3}\n(.*?)  \n(.*?)\s(\d+)%Commonly', file_text)
            if matches:
                common_types_of_injuries = {
                    matches[0][2].strip(): int(matches[0][0]),
                    matches[0][3].strip(): int(matches[0][1]),  
                    matches[0][4].strip(): int(matches[0][5])
                }
            else:        
                common_types_of_injuries = None
        # Append extracted data to the list
        data.append({
            'Sector': file,
            'no_dead_workers': workers_died,
            'no_injured_workers': workers_injured,
            'injuries_by_gender': injuries_by_gender,
            'age_with_highest_injury_claims': age_highest_injury_claims,
            'commonly_injured_parts': commonly_injured_parts,
            'top_three_causes': top_three_causes,
            'common_types_of_injuries': common_types_of_injuries
        })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df.insert(0, 'year', 2018)

    return df

def get_data_2019():

    # Initialize lists to store data from each file
    data = []

    # Iterate over file names
    for file in sector_names:
        # Extract text from PDF
        file_text = extract_text_from_pdf('2019/' + file[0:5] + "_2019.pdf")
        
        # Extract workers died
        match = re.search(r'Alberta\.(\d+)\nNumber of \nworkers \nwho died1', file_text)
        workers_died = int(match.group(1)) if match else None
        
        # Extract workers injured
        match = re.search(r'\n\d{1,2}Workplace incidents(.*?)\n[Ii]njury', file_text)
        workers_injured = int(match.group(1).replace(',', '')) if match else None
        
        # Extract injuries by gender
        match = re.search(r'(\d{1,2})%\n?\s{1,6}male\s{0,1}(\d{1,3})%\n\s{1,4}female', file_text)
        if match:
            male_percentage = int(match.group(1))
            female_percentage = int(match.group(2))
            injuries_by_gender = {'male': male_percentage, 'female': female_percentage}
        else:
            injuries_by_gender = None
        
        # Extract age with highest injury claims  
        

        age_highest_injury_claims = extract_age_percent_2019(file_text) 
        
        # Extract commonly injured parts
        commonly_injured_parts=extract_common_injuries_2019(file_text, sector_abb=file[0:5])
        commonly_injured_parts= sort_dict(commonly_injured_parts)
        
        # Extract top three causes of injuries
        pattern = r'workers\s\n(.*?)\s{1,3}(\d+)%\n(.*?)\s(\d+)%\n(.*?)\s{1,5}(\d+)%Common'
        matches = re.findall(pattern, file_text)
        
        if matches:
            top_three_causes = {
                matches[0][0].strip(): int(matches[0][1]),
                matches[0][2].strip(): int(matches[0][3]),
                matches[0][4].strip(): int(matches[0][5])
            } if matches else None
        
        
        # Extract common types of injuries
        pattern = r'injuries\n(.*?\n?.*?)(\d+)%\n(.*?\n?.*?)(\d+)%\n(.*?\n?.*?)(\d+)%\s?Commonly'
        matches = re.findall(pattern, file_text)
        if matches:
            common_types_of_injuries = {
                matches[0][0].strip(): int(matches[0][1]),
                matches[0][2].strip(): int(matches[0][3]),
                matches[0][4].strip(): int(matches[0][5])
            }
        else: 
            matches = re.findall(r'(\d+)%\n(\d+)%Common types of injuries \n(.*?)\s{3}\n(.*?)  \n(.*?)\s(\d+)%Commonly', file_text)
            if matches:
                common_types_of_injuries = {
                    matches[0][2].strip(): int(matches[0][0]),
                    matches[0][3].strip(): int(matches[0][1]),  
                    matches[0][4].strip(): int(matches[0][5])
                }
            else:        
                common_types_of_injuries = None
        # Append extracted data to the list
        data.append({
            'Sector': file,
            'no_dead_workers': workers_died,
            'no_injured_workers': workers_injured,
            'injuries_by_gender': injuries_by_gender,
            'age_with_highest_injury_claims': age_highest_injury_claims,
            'commonly_injured_parts': commonly_injured_parts,
            'top_three_causes': top_three_causes,
            'common_types_of_injuries': common_types_of_injuries
        })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df.insert(0, 'year', 2019)

    return df





def get_data_2020():
    # Initialize lists to store data from each file
    data = []
    # Iterate over file names
    for file in sector_names:
        # Extract text from PDF
        file_text = extract_text_from_pdf("2020/" + file[0:5] + "_2020.pdf")
        
        # Extract workers died
        match = re.search(r'2020\s?\n(\d+)\nNumber of \nworkers', file_text)
        workers_died = int(match.group(1)) if match else None
        
        # Extract workers injured
        match = re.search(r'\n\d{1,2}Workplace incidents(.*?)\n[Ii]njury', file_text)
        workers_injured = int(match.group(1).replace(',', '')) if match else None
        
        # Extract injuries by gender
        match = re.search(r'(\d{1,2})%\n?\s{1,6}male\s{0,1}(\d{1,3})%\n\s{1,4}female', file_text)
        if match:
            male_percentage = int(match.group(1))
            female_percentage = int(match.group(2))
            injuries_by_gender = {'male': male_percentage, 'female': female_percentage}
        else:
            injuries_by_gender = None
        
        # Extract age with highest injury claims  
        

        age_highest_injury_claims = extract_age_percent_2020(file_text) 
        
        # Extract commonly injured parts
        commonly_injured_parts=extract_common_injuries_2020(file_text, sector_abb=file[0:5])
        commonly_injured_parts= sort_dict(commonly_injured_parts)
        
        # Extract top three causes of injuries
        pattern = r'workers\s\n(.*?)\s{1,3}(\d+)%\n(.*?)\s(\d+)%\n(.*?)\s{1,5}(\d+)%Common'
        matches = re.findall(pattern, file_text)
        
        if matches:
            top_three_causes = {
                matches[0][0].strip(): int(matches[0][1]),
                matches[0][2].strip(): int(matches[0][3]),
                matches[0][4].strip(): int(matches[0][5])
            } if matches else None

        pattern = r'injuries\n(.*?\n?.*?)(\d+)%\n(.*?\n?.*?)(\d+)%\n(.*?)\n?(.*?)(\d+)%\s?\n?(.*?)Commonly'
        matches = re.findall(pattern, file_text)
        if matches:
            matches= list(matches[0])
            matches[2]=matches[2]+ matches[4]
            matches[5]=matches[5]+ matches[7]
            matches.pop(4)
            matches.pop(6)
            common_types_of_injuries= {matches[0].strip().replace('\n',''):int(matches[1]), matches[2].strip().replace('\n',''):int(matches[3]),matches[4].strip().replace('\n',''):int(matches[5])}
        else:
            common_types_of_injuries=None
        # Append extracted data to the list
        data.append({
            'Sector': file,
            'no_dead_workers': workers_died,
            'no_injured_workers': workers_injured,
            'injuries_by_gender': injuries_by_gender,
            'age_with_highest_injury_claims': age_highest_injury_claims,
            'commonly_injured_parts': commonly_injured_parts,
            'top_three_causes': top_three_causes,
            'common_types_of_injuries': common_types_of_injuries
        })
    df= pd.DataFrame(data)
    df.insert(0, 'year', 2020)
    return df


def get_data_2021():

    # Initialize lists to store data from each file
    data = []

    # Iterate over file names
    for file in sector_names:
        # Extract text from PDF
        file_text = extract_text_from_pdf("2021/" + file[0:5] + "_2021.pdf")
        
        # Extract workers died
        match = re.search(r'Fatality trends 2017-2021\*(\d+)', file_text)
        workers_died = int(match.group(1)) if match else None
        
        # Extract workers injured
        match = re.search(r'sector([\d,]+)', file_text)
        workers_injured = int(match.group(1).replace(',', '')) if match else None
        
        # Extract injuries by gender
        match = re.search(r'(\d{1,2})%\nmale(\d{1,2})%\nfemale', file_text)
        if match:
            male_percentage = int(match.group(1))
            female_percentage = int(match.group(2))
            injuries_by_gender = {'male': male_percentage, 'female': female_percentage}
        else:
            injuries_by_gender = None
        
        # Extract age with highest injury claims
        match = re.search(r'(\d{2}-\d{2})\s{1,2}year olds\n([\d.]+)', file_text)
        age_highest_injury_claims = {match.group(1): float(match.group(2))} if match else None
        
        # Extract commonly injured parts
        file_text= file_text.replace('\n','')
        pattern = r'100 person-years(.*?)\s(\d+)%(.*?)\s(\d+)%(.*?)\s(\d+)%' 
        matches = re.findall(pattern, file_text)
        commonly_injured_parts = {
            matches[0][0].strip(): int(matches[0][1]),
            matches[0][2].strip(): int(matches[0][3]),
            matches[0][4].strip(): int(matches[0][5])
        } if matches else None
        
        # Extract top three causes of injuries
        pattern = r'Causes(.*?)\s(\d+)%(.*?)\s(\d+)%(.*?)\s(\d+)%' 
        matches = re.findall(pattern, file_text)
        top_three_causes = {
            matches[0][0].strip(): int(matches[0][1]),
            matches[0][2].strip(): int(matches[0][3]),
            matches[0][4].strip(): int(matches[0][5])
        } if matches else None
        
        # Extract common types of injuries
        pattern = r'Types(.*?)\s(\d+)%(.*?)\s(\d+)%(.*?)\s(\d+)%' 
        matches = re.findall(pattern, file_text)
        common_types_of_injuries = {
            matches[0][0].strip(): int(matches[0][1]),
            matches[0][2].strip(): int(matches[0][3]),
            matches[0][4].strip(): int(matches[0][5])
        } if matches else None
        
        # Append extracted data to the list
        data.append({
            'Sector': file,
            'no_dead_workers': workers_died,
            'no_injured_workers': workers_injured,
            'injuries_by_gender': injuries_by_gender,
            'age_with_highest_injury_claims': age_highest_injury_claims,
            'commonly_injured_parts': commonly_injured_parts,
            'top_three_causes': top_three_causes,
            'common_types_of_injuries': common_types_of_injuries
        })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df.insert(0, 'year', 2021)

    return df

def get_data_2022():

    # Initialize lists to store data from each file
    data = []

    # Iterate over file names
    for file in sector_names:
        # Extract text from 
        filename= "2022/" + file[0:5] + "_2022.pdf"
        file_text = extract_text_from_pdf(filename)
        
        # Extract workers died
        match = re.search(r'\*([0-9]+)\n[0-9]+\nOccupational', file_text)
        workers_died = int(match.group(1)) if match else None
        
        # Extract workers injured
        if filename != "2022/Whole_2022.pdf":
            match = re.search(r'illnesses\)\n([0-9,]+)', file_text)
            workers_injured = int(match.group(1).replace(',', '')) if match else None
        else:
            match = re.search(r'Injury claims ([0-9,]+) Common injuries', file_text)
            workers_injured = int(match.group(1).replace(',', '')) if match else None            


        
        # Extract injuries by gender
        match = re.search(r'(\d{1,2})%\nmale(\d{1,2})%\nfemale', file_text)
        if match:
            male_percentage = int(match.group(1))
            female_percentage = int(match.group(2))
            injuries_by_gender = {'male': male_percentage, 'female': female_percentage}
        else:
            injuries_by_gender = None
        
        # Extract age with highest injury claims
        match = re.search(r'(\d+-\d+|\d+\+)\s*year olds\n([0-9]+\.[0-9]+)\s*per 100 person-years', file_text)
        age_highest_injury_claims = {match.group(1): float(match.group(2))} if match else None
        
        # Extract commonly injured parts
        # file_text= file_text.replace('\n','')
        pattern = r'([A-Z][a-z\s,]*)\s+(\d{1,2})%\s*([A-Z][a-zA-Z\s,]*)\s*(\d{1,2})%\s*([A-Z][a-zA-Z\s,]*)\s*(\d{1,2})%\s*Industry with higher'


        matches = re.findall(pattern, file_text)
        commonly_injured_parts = {
            matches[0][0].strip(): int(matches[0][1]),
            matches[0][2].strip(): int(matches[0][3]),
            matches[0][4].strip(): int(matches[0][5])
        } if matches else None
        if commonly_injured_parts:
            commonly_injured_parts= sort_dict(commonly_injured_parts)
        # Extract top three causes of injuries
        pattern = r'Cause\n(.*?)\s+(\d+)%\n(.*?)\s+(\d+)%\n(.*?)\s+(\d+)%Injuries'
        matches = re.findall(pattern, file_text)
        
        if matches:
            top_three_causes = {
                matches[0][0].strip(): int(matches[0][1]),
                matches[0][2].strip(): int(matches[0][3]),
                matches[0][4].strip(): int(matches[0][5])
            }
        else:
            pattern = r'\n(\d{1,2})%\n(\d{1,2})%Cause\n(.*?)\s\n(.*?)\s+\n(.*?)\s+(\d{1,2})%Injuries'
            matches = re.findall(pattern, file_text)
            if matches:
                top_three_causes = {matches[0][2].strip(): int(matches[0][0]), matches[0][3].strip(): int(matches[0][1]), matches[0][4].strip(): int(matches[0][5])}
            else:
                top_three_causes= None
            
        
        # Extract common types of injuries
        pattern = r'\*Type\n(.*?)\s*(\d+)%\s*\n(.*?)\s*(\d+)%\s*\n(.*?)\s*(\d+)%'

        matches = re.findall(pattern, file_text)
        common_types_of_injuries = {
            matches[0][0].strip(): int(matches[0][1]),
            matches[0][2].strip(): int(matches[0][3]),
            matches[0][4].strip(): int(matches[0][5])
        } if matches else None
        
        # Append extracted data to the list
        data.append({
            'Sector': file,
            'no_dead_workers': workers_died,
            'no_injured_workers': workers_injured,
            'injuries_by_gender': injuries_by_gender,
            'age_with_highest_injury_claims': age_highest_injury_claims,
            'commonly_injured_parts': commonly_injured_parts,
            'top_three_causes': top_three_causes,
            'common_types_of_injuries': common_types_of_injuries
        })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df.insert(0, 'year', 2022)

   
    return df


def split_series_into_columns(series):
    # Ensure the input is a pandas Series
    if not isinstance(series, pd.Series):
        raise ValueError("Input must be a pandas Series")

    # Extract the keys from the first dictionary in the Series
    first_dict = series.dropna().iloc[0]
    if not isinstance(first_dict, dict):
        raise ValueError("Series must contain dictionaries")
    
    keys = first_dict.keys()

    # Create a DataFrame from the series
    df = pd.DataFrame(series)

    # Split the series into multiple columns
    for key in keys:
        df[f"{series.name}_{key}"] = series.apply(lambda x: x[key] if isinstance(x, dict) else None)
    
    # Drop the original column
    df.drop(columns=[series.name], inplace=True)
    
    return df

def split_series_to_columns_numbers(series):
    """
    Split a Pandas Series of dictionaries into separate columns.

    Args:
        series (pd.Series): The series containing dictionaries to split.

    Returns:
        pd.DataFrame: A DataFrame with the split columns.
    """
    # Initialize list to store the split columns
    split_columns = []

    # Iterate through each dictionary in the series
    for idx, item in series.items():
        # If the item is a dictionary, extract keys and values
        if isinstance(item, dict):
            keys = list(item.keys())
            values = list(item.values())
        else:
            keys = []
            values = []

        # Interleave keys with values
        interleaved = []
        for key, value in zip(keys, values):
            interleaved.append(key)
            interleaved.append(value)
        
        split_columns.append(interleaved)

    # Determine the maximum length of interleaved lists
    max_len = max(len(interleaved) for interleaved in split_columns)

    # Pad the interleaved lists with None to ensure equal length
    split_columns = [interleaved + [None] * (max_len - len(interleaved)) for interleaved in split_columns]

    # Create a DataFrame with interleaved columns
    column_names = []
    for i in range(1, max_len // 2 + 1):
        column_names.append(f"{series.name}_{i}")
        column_names.append(f"{series.name}_{i}" + "_percent")
        
    result_df = pd.DataFrame(split_columns, columns=column_names)

    return result_df

def split_series_to_unique_columns(series):
    """
    Split a Pandas Series of dictionaries into separate columns for unique keys and unique values.

    Args:
        series (pd.Series): The series containing dictionaries to split.

    Returns:
        pd.DataFrame: A DataFrame with the split columns.
    """
    # Initialize lists to store the unique keys and values
    unique_keys = []
    unique_values = []

    # Iterate through each dictionary in the series
    for idx, item in series.items():
        # If the item is a dictionary, extract keys and values
        if isinstance(item, dict):
            keys = list(item.keys())
            values = list(set(list(item.values())))
        else:
            keys = []
            values = []

        # Convert the lists of keys and values to strings and add to the respective lists
        unique_keys.append(', '.join(keys))
        unique_values.append(', '.join(map(str, values)))

    # Create a DataFrame with unique keys and values columns
    result_df = pd.DataFrame({
        series.name + '_': unique_keys,
        series.name+ '_percent': unique_values
    })

    return result_df

extract_text_from_pdf("2017/agric_2017.pdf")

# List of functions
data_functions = [get_data_2017, get_data_2018, get_data_2019, get_data_2020, get_data_2021, get_data_2022]

# Collect DataFrames
df_s = [func() for func in data_functions]
dfs= pd.concat(df_s, ignore_index=True)
df = pd.concat([dfs, split_series_into_columns(dfs["injuries_by_gender"])
            ,split_series_to_unique_columns(dfs["age_with_highest_injury_claims"]),
            split_series_to_columns_numbers(dfs["commonly_injured_parts"]),
            split_series_to_columns_numbers(dfs["top_three_causes"]),
                split_series_to_columns_numbers(dfs["common_types_of_injuries"]) ],axis=1)
df.drop(columns=["injuries_by_gender","commonly_injured_parts","top_three_causes","common_types_of_injuries", "age_with_highest_injury_claims"], inplace= True)
df["age_with_highest_injury_claims_percent"] = df["age_with_highest_injury_claims_percent"].astype("float64")


replace_dict ={'Backincluding spine,spinal cord': 'Back including spine,spinal cord', 
               'Back': 'Back including spine,spinal cord',
               'Hands' :'Wrist(s) and Hand(s) except ﬁnger(s)',
               'Legs' : 'Leg(s)',
               'Finger' : 'Wrist(s) and Hand(s) except ﬁnger(s)',                                
               'Fingers' : 'Wrist(s) and Hand(s) except ﬁnger(s)',
               'Finger(s),ﬁngernails' : 'Finger(s),Fingernail(s)',
               'Finger(s), /f_ingernail(s)': 'Finger(s),Fingernail(s)',
                'Finger(s), ﬁngernail(s)': 'Finger(s),Fingernail(s)',
               'Finger(s),/f_ingernails': 'Finger(s),Fingernail(s)',
               'Finger(s),ﬁngernail(s)': 'Finger(s),Fingernail(s)',
               'Wrist(s) and hand(s) except /f_inger(s)': 'Wrist(s) and hand(s) except ﬁnger(s)',
               'Wrist(s), Hand(s)except ﬁnger(s)': 'Wrist(s) and hand(s) except ﬁnger(s)',                      
               'Wrist(s) and Hand(s) except /f_inger(s)': 'Wrist(s) and hand(s) except ﬁnger(s)',
               'Wrist(s) and Hand(s) except ﬁnger(s)': 'Wrist(s) and hand(s) except ﬁnger(s)', 
               'Wrist(s), Hand(s)except /f_inger(s)': 'Wrist(s) and hand(s) except ﬁnger(s)',
               'Hand or wrist': 'Wrist(s) and hand(s) except ﬁnger(s)',
               'Foot, ankle  or toe' : 'Foot (feet), ankle(s), toe(s)',
               'Feet' : 'Foot (feet), ankle(s), toe(s)',
               'Ankle, foot  or toe':'Foot (feet), ankle(s), toe(s)',
               'Ankle(s), Foot (feet)except toes' : 'Foot (feet), ankle(s), toe(s)',
               'Ankle(s), foot (feet)except toes' : 'Foot (feet), ankle(s), toe(s)',
               'Foot, ankle \nor toe' : 'Foot (feet), ankle(s), toe(s)',
               'Foot, ankle or toe' : 'Foot (feet), ankle(s), toe(s)',
               'Ankle(s) and foot except toes': 'Foot (feet), ankle(s), toe(s)'
               }

# Combine Back and Back including spinal cord, spine commonly_injured_parts_1
df['commonly_injured_parts_1'] = df['commonly_injured_parts_1'].replace(replace_dict)

# Combine Back and Back including spinal cord, spine commonly_injured_parts_2
df['commonly_injured_parts_2'] = df['commonly_injured_parts_2'].replace(replace_dict)

# Combine Back and Back including spinal cord, spine commonly_injured_parts_3
df['commonly_injured_parts_3'] = df['commonly_injured_parts_3'].replace(replace_dict)

replace_dict_cause ={'Exposures to harmful substance': 'Exposure to harmful substances',
                     'Exposure to harmful substance': 'Exposure to harmful substances',
                     'Overexertion':'Bodily reaction  and exertion',
                    'Bodily reaction': 'Bodily reaction  and exertion',
                    'Bodily Reaction': 'Bodily reaction  and exertion',
                    'Bodily reaction or exertion':'Bodily reaction  and exertion',
                    'Bodily reaction   a nd exertion': 'Bodily reaction  and exertion',
                    'Bodily reaction   o r exertion': 'Bodily reaction  and exertion',
                    'Falls': 'Slips, trips and falls',
                    'Slip, trip or fall':'Slips, trips and falls',
                    'Slips, trips  and falls': 'Slips, trips and falls',
                    'Struck by object':'Struck by or against objects',
                    'Struck by or   a gainst object': 'Struck by or against objects', 
                    'Struck by object    15%49%': 'Struck by or against objects',
                    'Struck by or  against objects': 'Struck by or against objects',
                    'Struck by or against object': 'Struck by or against objects',
                    'Struck b y or against object':'Struck by or against objects'}

df["top_three_causes_1"].replace(replace_dict_cause, inplace=True)
df["top_three_causes_2"].replace(replace_dict_cause, inplace=True)
df["top_three_causes_3"].replace(replace_dict_cause, inplace=True)

replace_dict_injury ={'Sprain / Strain / Tear': 'Sprains/ Strains/ Tears',
                      'Sprains / Strains / Tears': 'Sprains/ Strains/ Tears',
                      'Sprains/ strains/ tears': 'Sprains/ Strains/ Tears',
                      'Sprains / strains / tears': 'Sprains/ Strains/ Tears',
                      'Sprains /  strains / tears': 'Sprains/ Strains/ Tears',
                      'Sprain, strain or tear': 'Sprains/ Strains/ Tears',
                      'Fractures & dislocations':'Fractures/ Dislocations/ Nerve Damage',
                      'Fractures/ Dislocations/ \nNerve damage': 'Fractures/ Dislocations/ Nerve Damage',
                      'Fractures/ Dislocations/ \nNerve Damage' : 'Fractures/ Dislocations/ Nerve Damage',
                      'Fractures/ dislocations/ nerve damage':'Fractures/ Dislocations/ Nerve Damage',
                      'Fractures/ dislocations/  nerve damage': 'Fractures/ Dislocations/ Nerve Damage',
                      'Open wounds': 'Wounds and  bruises',
                      'Superﬁcial wounds': 'Wounds and  bruises',
                      'Super/f_icial wounds': 'Wounds and  bruises',
                      'Wound or bruise':'Wounds and  bruises',
                      'Systemic diseases and  disorders': 'Systemic diseases and disorders',
                      'Other injury': 'Other injuries'
                      }
df["common_types_of_injuries_3"].replace(replace_dict_injury, inplace=True)


# Save DataFrame to CSV
df.to_csv('HS.csv', index=False)









