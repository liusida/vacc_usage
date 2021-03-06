"""
Author: Sida Liu, 2021
Compute the historical usage by querying VACC slurm logging database produced by David Matthew.
Generate a plot into a html file `history.plots.html`.
"""

import argparse
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pd.options.plotting.backend = "plotly"

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", default='vacc_database.backup_2021_06_03.db', help='path to VACC usage database.')
args = parser.parse_args()

con = sqlite3.connect(args.database)
cur = con.cursor()


from datetime import datetime
now = datetime.now()
current_time = now.strftime("%A, %B %d, %Y %H:%M:%S")
timestamp = datetime.timestamp(now)

plot_settings = [
    [
        {'title': '24h CPU Usage', 'measure': 'CPU', 'timespan': 24*60*60 },
        {'title': '7d CPU Usage', 'measure': 'CPU', 'timespan': 7*24*60*60 },
        {'title': '30d CPU Usage', 'measure': 'CPU', 'timespan': 30*24*60*60 },
    ],
    [
        {'title': '24h GPU Usage', 'measure': 'GPU', 'timespan': 24*60*60 },
        {'title': '7d GPU Usage', 'measure': 'GPU', 'timespan': 7*24*60*60 },
        {'title': '30d GPU Usage', 'measure': 'GPU', 'timespan': 30*24*60*60 },
    ],
]

subplot_titles = []
for i in range(3):
    for j in range(2):
        subplot_titles.append(plot_settings[j][i]['title'])

fig = make_subplots(rows=3, cols=2, subplot_titles=subplot_titles)

for i in range(2):
    for j in range(3):
        p = plot_settings[i][j]
        query_sql = f"SELECT user,lab, sum({p['measure']}Time) as measure FROM JOBS WHERE date>{timestamp-p['timespan']} GROUP BY user,lab ORDER BY measure DESC"
        df = pd.read_sql_query(query_sql, con)
        df['name'] = df['user'] + " / " + df['lab']
        df['percentage'] = 100. * df['measure'] / df['measure'].sum()
        df = df[df['percentage']>1.0]
        df = df.append({
                    'name': 'others',
                    'measure': p['measure'],
                    'percentage': 100.-df['percentage'].sum(),
                }, ignore_index=True)
        fig.add_trace(
                go.Bar(
                    x=df['name'], 
                    y=df['percentage'], 
                    text=df['percentage'].round(1).astype(str) + '%', 
                    textposition='auto', 
                    marker_color='#6287a2' if p['measure']=='CPU' else '#80c8bc',
                ),
                row=j+1, col=i+1,
            )
        fig.update_xaxes(title_text="Username / Lab", row=j+1, col=i+1)
        fig.update_yaxes(title_text=f"{p['measure']} Percentage", row=j+1, col=i+1)

fig.update_layout(
    showlegend=False,
    font_size=16,
    title=f"Recent Usage of VACC resources (Generated at {current_time})",
)

fig.write_html("public_html/history.plots.html", default_height=1500)
