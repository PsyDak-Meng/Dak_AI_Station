from sec_api import XbrlApi, QueryApi
import requests
import json
from CONSTANTS import *
from tqdm import tqdm
import pandas as pd

class SEC_loader():
    def __init__(self, api_key:str='93df89d84ccd1ae5df2e918be50b9cb5bf3d20848f14b98fb70e11378f7144af'):
        self.ticker = None    
        self.api_key = api_key
        self.xbrl_api = XbrlApi(self.api_key)
        self.query_api = QueryApi(self.api_key)
        self.metadata = None
        self.income_statements = []
        self.urls = []

    def fetch_url(self, ticker:str,):
        self.ticker = ticker
        query = {
            "query": f"ticker:{self.ticker} AND formType:\"10-K\" AND filedAt:[1995-01-01 TO 2023-12-31]",
            "from": "0",
            "sort": [{ "filedAt": { "order": "asc"}}]
            }

        endpoint_url = f'https://api.sec-api.io?token={self.api_key}'

        response = self.query_api.get_filings(query)
        metadata = pd.DataFrame.from_records(response['filings'])
        # print(metadata.columns)


        # cols = ['ticker', 'formType', 'filedAt','linkToHtml', 'linkToXbrl', 'accessionNo', 'linkToFilingDetails']
        # metadata = metadata[cols]
        metadata['filedAt'] = metadata['filedAt'].apply(lambda x: x.split('-')[0])

        for index, row in metadata.iterrows():
            url = row['documentFormatFiles'][0]['documentUrl']
            url = row['linkToHtml']
            if '.htm' in url:
                self.urls.append(url)
                    # print(len(row['documentFormatFiles']))
                    # print(row['documentFormatFiles'][0]['documentUrl'])
                    # self.urls.append(row['linkToHtml'])
        # print(self.urls)
        print(url)
        respone = requests.get(url)
        response = response
        print(response['filings'][0])
        # print(len(self.urls))
        self.metadata = metadata




    # convert XBRL-JSON of income statement to pandas dataframe
    def get_income_statement(self, xbrl_json):
        # Turn html into XBRL json
        income_statement_store = {}

        # iterate over each US GAAP item in the income statement
        for usGaapItem in xbrl_json['StatementsOfIncome']:
            values = []
            indicies = []

            for fact in xbrl_json['StatementsOfIncome'][usGaapItem]:
                # only consider items without segment. not required for our analysis.
                if 'segment' not in fact:
                    index = fact['period']['startDate'] + '-' + fact['period']['endDate']
                    # ensure no index duplicates are created
                    if index not in indicies:
                        values.append(fact['value'])
                        indicies.append(index)                    

            income_statement_store[usGaapItem] = pd.Series(values, index=indicies) 

        income_statement = pd.DataFrame(income_statement_store)
        # switch columns and rows so that US GAAP items are rows and each column header represents a date range
        return income_statement.T 

      

    def load_income_statements(self):
        for url in tqdm(self.urls[:2],'Loading Income Statements'):
            try:
                xbrl_json = self.xbrl_api.xbrl_to_json(htm_url='https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm')
                xbrl_json = self.get_income_statement(xbrl_json)
                self.income_statements.append(xbrl_json)
            except:
                pass

        print(len(self.income_statements))

        income_statements_merged = pd.concat(self.income_statements, axis=0, sort=False)

        # sort & reset the index of the merged dataframe
        income_statements_merged = income_statements_merged.sort_index().reset_index()

        # convert cells to float
        income_statements_merged = income_statements_merged.applymap(lambda x: pd.to_numeric(x, errors='ignore'))
             
        income_statements = income_statements_merged.groupby('index').max()

        # reindex the merged dataframe using the index of the first dataframe
        income_statements = income_statements.reindex(self.income_statements[0].index)

        # loop over the columns
        for col in income_statements.columns[1:]:
            # extract start and end dates from the column label
            splitted = col.split('-')
            start = '-'.join(splitted[:3])
            end = '-'.join(splitted[3:])

            # convert start and end dates to datetime objects
            start_date = pd.to_datetime(start)
            end_date = pd.to_datetime(end)

            # calculate the duration between start and end dates
            duration = (end_date - start_date).days / 360

            # drop the column if duration is less than a year
            if duration < 1:
                income_statements.drop(columns=[col], inplace=True)

        # convert datatype of cells to readable format, e.g. "2.235460e+11" becomes "223546000000"
        income_statements = income_statements.apply(lambda row: pd.to_numeric(row, errors='coerce', downcast='integer').astype(str), axis=1) 
        print(income_statements.columns)
        print(income_statements.iloc[0,:])

        return income_statements
        






# sec_loader = SEC_loader()
# sec_loader.fetch_url(ticker='AAPL')
# income_statements = sec_loader.load_income_statements()