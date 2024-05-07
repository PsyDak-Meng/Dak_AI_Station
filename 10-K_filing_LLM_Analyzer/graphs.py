import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template
from io import BytesIO
import base64


# Sample data (replace this with your actual DataFrame)


def bar_chart():
    data = {
    'Period': ['2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022'],
    'Revenue': [229234000000, 265595000000, 260174000000, 274515000000, 365817000000, 394328000000],
    'GrossProfit': [88186000000, 101839000000, 98392000000, 104956000000, 152836000000, 170782000000],
    'NetIncome': [48351000000, 59531000000, 55256000000, 57411000000, 94680000000, 99803000000]
}
    df = pd.DataFrame(data)

    # Generate bar graph
    fig, ax = plt.subplots()
    df.plot(kind='bar', x='Period', y=['Revenue', 'GrossProfit'], ax=ax)
    ax.set_title('Revenue and Gross Profit Over Time')
    ax.set_xlabel('Period')
    ax.set_ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot to a bytes buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return plot_data


def line_graph():
    data = {
    'Period': ['2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022'],
    'Revenue': [229234000000, 265595000000, 260174000000, 274515000000, 365817000000, 394328000000],
    'GrossProfit': [88186000000, 101839000000, 98392000000, 104956000000, 152836000000, 170782000000],
    'NetIncome': [48351000000, 59531000000, 55256000000, 57411000000, 94680000000, 99803000000]
}
    df = pd.DataFrame(data)
    
    # Generate line graph
    fig, ax = plt.subplots()
    df.plot(kind='line', x='Period', y=['NetIncome'], ax=ax)
    ax.set_title('Net Income Over Time')
    ax.set_xlabel('Period')
    ax.set_ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot to a bytes buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    line_plot_data = base64.b64encode(buffer.getvalue()).decode()
    return line_plot_data