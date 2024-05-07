from urllib.request import urlopen
import os
import re
import json
import pandas as pd
from tqdm import tqdm
import time
from bs4 import BeautifulSoup

# Extracts text from filing by searching targeted_string
# Feeds to LLM for insight
def extract_by_search(paths:dict, targeted_string:str):
    def search_strings(texts:list,target_string:str):
            targeted_texts = []
            for text in texts:
                if target_string in text:
                    targeted_texts.append(text)
            return targeted_texts 
    
    metadata = []

    for year, path in tqdm(paths.items(), 'Extracting text from 10-Ks in each year...'):
        # Open the HTML file
        try:
            with open(path) as f:
                s = f.read()
            # Parse HTML content using BeautifulSoup
            soup = BeautifulSoup(s, 'html5lib')
            texts = soup.get_text(strip=True)
            # print(texts)
            pages = texts.split('Form 10-K')

            metadata.append(year + ' '.join(search_strings(pages, targeted_string)) + '\n')
        
        except:
             pass

    return ''.join(metadata)[:2000]
            

        # tables = BeautifulSoup(s,"html.parser").find_all('table')
        # # Function to search for a string within elements
        # def search_string_within_elements(elements, target_string):
        #     for elem in elements:
        #         if target_string in elem.get_text():
        #             return elements
        #     found_elements = []
        #     for elem in elements:
        #         if target_string in elem.text:
        #             for elem in elements:
        #                 found_elements.append(elem.text)
        #             return found_elements
        #     return None

        # # Find all <hr> tags
        # hr_tags = soup.find_all('hr')

        # # Capture everything between <hr> tags
        # captured_content = []
        # for idx in range(len(hr_tags) - 1):
        #     start_hr = hr_tags[idx]
        #     end_hr = hr_tags[idx + 1]
        #     content_between_hr = start_hr.find_next_siblings()  # Find siblings between <hr> tags
        #     content_between_hr = remove_tags(content_between_hr)
        #     for elem in content_between_hr:
        #         if elem == end_hr:  # Stop capturing at the next <hr> tag
        #             break
        #         captured_content.append(elem)

        # # Search for a string within the captured elements
        # found_elements = search_string_within_elements(captured_content, targeted_string)

        # # Print the found elements
        # if found_elements:
        #     print(f"Found '{targeted_string}' in the following elements:")
        #     for elem in found_elements:
        #         print(elem)
        # else:
        #     print(f"'{targeted_string}' not found in any element.")
    
    

    # # Extract table data into a list of DataFrames
    # dfs = []
    # for table in tables:
    #     # Convert each table to a DataFrame
    #     df = pd.read_html(str(table), flavor='lxml')
    #     if len(df)==0:
    #         pass
    #     else:
    #         df = df[0]  # read_html returns a list of DataFrames, we take the first (and only) one
    #         dfs.append(df)
    
    # # Filter the DataFrames based on the target string
    # targeted_dfs = []
    # for df in dfs:
    #     if check_string_in_dataframe(df,'Total net sales'):
    #         targeted_dfs.append(df)
    # return targeted_dfs



