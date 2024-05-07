# SEC-API Filing LLM Analyzer

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)

## Description

SEC-API Filing Analyzer is a Flask-based web application that automates the downloading of 10-K filing HTML files from the SEC-API database. It then performs text parsing to extract relevant pages based on targeted keywords. The extracted data is visualized using Matplotlib, and the application connects to the OpenAI API to provide AI-powered insight analysis.

## Features

- Automatic download of 10-K filing HTML files using SEC-API
- Text parsing to extract relevant pages based on targeted keywords
- Visualization of extracted data using Matplotlib
- Integration with OpenAI API for AI-powered insight analysis
- User-friendly web interface built with Flask

## Acknowledgement

- The static nature of visualizations in this application is due to potential SEC-API service failures. Dynamic visualizations can be implemented with additional parsing and dynamic data retrieval efforts.

- Cloud Platform Deployment

This application can be easily deployed on cloud platforms such as AWS and Azure if necessary for research work. Feel free to reach out for assistance with cloud deployment.


## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/sec-api-filing-analyzer.git
```
2. Navigate to folder:
```bash
cd Sec-api-Filing-LLM-Analyzer
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run application:
```bash
python app.py
```



