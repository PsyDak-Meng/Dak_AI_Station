from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, SelectField
import requests
from bs4 import BeautifulSoup
import re
from sec_edgar_downloader import Downloader
import os
from tqdm import tqdm
from CONSTANTS import *
from SEC10K_parser import extract_by_search
from SEC_loader import SEC_loader
from graphs import  bar_chart, line_graph
from llm_api import LLM_API
import matplotlib


"""
    What do they care about?
    Why they care abuot it?
    What is the insight?
    Visualization.
"""

llm_api = LLM_API()

matplotlib.use('agg')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'



# Form for entering company ticker symbol
class TickerForm(FlaskForm):
    # tickers = [('AAPL', 'Apple'), ('MSFT', 'Microsoft'), ('GOOGL', 'Alphabet'), ('AMZN', 'Amazon')]
    # ticker = SelectField('Ticker', choices=tickers, render_kw={"placeholder": "AAPL"}, validators=[validators.InputRequired()])
    ticker = StringField('Enter Company Ticker:', render_kw={"placeholder": "AAPL"}, validators=[validators.InputRequired()])
    submit = SubmitField('Submit', id='submitButton')

# Function to fetch list of SEC 10-K filings file_path
def fetch_10Kfiling_paths(ticker:str) -> list: 
    ticker = ticker.upper()
    filing_paths = {}
    
    # Fetching 10-K filings from SEC
    dl = Downloader("MyCompanyName", "my.email@domain.com")
    # Download 10-Ks from 1995 to 2023
    dl.get(filing_type, ticker, after=start_date, before=end_date, download_details=True)

    # Define .txt path
    ticker_filepath = "sec-edgar-filings"
    ticker_filepath = os.path.join(ticker_filepath, ticker, "10-K")

    # Extracting text from each filing
    for filing_folder in tqdm(os.listdir(ticker_filepath), desc="Extracting text from 10-Ks"):
        pattern = r'-(.*?)-'
        year = re.search(pattern, filing_folder).group(1)

        filing_path = os.path.join(ticker_filepath, filing_folder, "primary-document.html")
        filing_paths[year] = filing_path
        
    return filing_paths




# def load_10k_filings(ticker:str):
#     sec_loader = SEC_loader()
#     sec_loader.fetch_url(ticker=ticker)
#     return sec_loader.load_income_statements()




# Route for homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    form = TickerForm()
    if form.is_submitted():
        form.validate()
        print("form submitted and validated!")
        ticker = form.ticker.data

        # Fetch process 10-K filings paths
        paths = fetch_10Kfiling_paths(ticker)
        print("Retrieved 10-K filings!")

        # Form prompt metadata
        search_texts = ['Segmenting Operating','Total Net Sales']
        metadata_1 = extract_by_search(paths, search_texts[0])
        metadata_2 = extract_by_search(paths, search_texts[1])

        # income_statement = load_10k_filings(ticker)
        print("Retrieved 10-K filings pages!")


        # Feed to LLM for insight
        insight_1 = llm_api.text_analysis(metadata_1)
        insight_2 = llm_api.text_analysis(metadata_2)

        insights_data = {search_texts[0]:insight_1,
                         search_texts[1]:insight_2}
        
        print("10-K filings insights extracted successfully!")


        plot_data = bar_chart()
        line_plot_data = line_graph()


        # Perform text analysis (you can use NLP libraries like NLTK, spaCy, etc.)
        return render_template('visualization.html', ticker=ticker, form=form, 
                               plot_data=plot_data, line_plot_data=line_plot_data,
                               insights=insights_data)
    return render_template('index.html', form=form)


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    # Process user message and generate response (replace this with your actual logic)
    response_message = llm_api.qa(user_message)
    return jsonify({'message': response_message})



if __name__ == '__main__':
    app.run(debug=True)
