from tkinter.font import families
import dash
import plotly.express as px
import pandas as pd
from dash import Input, Output, html, dcc
import pathlib
import numpy as np
import datetime
from datetime import datetime as dt
import dash_bootstrap_components as dbc


app = dash.Dash(__name__)

#=========== PRÉ PROCESSAMENTO ==========#
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

df = pd.read_csv(DATA_PATH.joinpath("clinical_analytics.csv"))
clinic_list = df["Clinic Name"].unique()
df['Admit Source'] = df['Admit Source'].fillna("Not Identified")
admit_list = df["Admit Source"].unique()

df["Check-In Time"] = df["Check-In Time"].apply(lambda x: dt.strptime(x,"%Y-%m-%d %I:%M:%S %p"))

df["Days of Wk"] = df["Check-In Time"].apply(lambda x: dt.strftime(x, "%A")) 
df["Check-In Hour"] = df["Check-In Time"].apply(lambda x: dt.strftime(x, "%I %p")) 

day_list = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

check_in_duration = df["Check-In Time"].describe(datetime_is_numeric=True)
all_departments = df['Department'].unique().tolist()



#=============FUNÇÕES================#

#=============================
#Funções de Layout 

def description_card():
    return html.Div(
        id="description-card", 
        children = [
            html.H5("Clinical Analytics"),
            html.H3("Welcome to the Clinical Analytics Dashboard"),
            html.Div(
                id="intro",
                children="Explore clinic patient volume by time of day, waiting time, and care score."
            )])

def generate_control_card():
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Clinic:"),
            dcc.Dropdown(
                id="clinic-select",
                options=[{"label": i, "value": i} for i in clinic_list],
                value=clinic_list[0]
            ),
            html.P("Select Check-in Time:"),
            dcc.DatePickerRange(
                id='date-picker-select',
                start_date=df["Check-In Time"].min().date(),
                end_date=df["Check-In Time"].max().date(),
                min_date_allowed=df["Check-In Time"].min().date(),
                max_date_allowed=df["Check-In Time"].max().date()
            ),
            html.P("Select Admit Source"),
            dcc.Dropdown(
                id='admit-select',
                options=[{"label": i, "value": i} for i in admit_list],
                value=admit_list[:],
                multi=True
            )
        ]
    )

#=============================
#Funções de manipulção de dados

def get_patient_volume_heatmap(start, end, clinic, admit_type):
    filter_df = df[(df["Clinic Name"] == clinic) & (df["Admit Source"].isin(admit_type))]
    filter_df = filter_df.sort_values("Check-In Time").set_index("Check-In Time")[start:end]

    x_axis = [datetime.time(i).strftime("%I %p") for i in range(24)]
    y_axis = day_list
    z = np.zeros((7,24))

    annotations = []

    for ind_y, day in enumerate(y_axis):
        filter_day = filter_df[["Days of Wk"] == day]
        for ind_x, x_val in enumerate(x_axis):
            sum_of_records = filter_day[filter_day["Check-In Hour"] == x_val]["Number of Records"].sum()
            z=[ind_y, ind_x] = sum_of_records

            ann_dict = dict(
                showarrow = False,
                text="<b>" + str(sum_of_records) + "</b>",
                x=x_val,
                y=day,
                font=(dict(family='sans-serif'))
            )
            annotations.append(ann_dict)

    hovertemplate = "<b> %{y} %{x}<br><br> %<z> Patient Records"

    data = [
        dict(
            x = x_axis,
            y = y_axis,
            z = z,
            type="heatmap",
            hovertemplate = hovertemplate,
            showscale = False,
            colorscale = [[0, "caf3ff"], [1,'#2c82ff']]
        )
    ]

    layout = dict(
        margin=dict(l=70, b=50, t=50, r=50),
        modebar={"orientation": "v"},
        font=dict(family="Open Sans"),
        annotations=annotations,
        xaxis=dict(
            side="top",
            ticks="",
            ticklen=2,
            tickfont=dict(family="sans-serif"),
            tickcolor="#ffffff",
        ),
        yaxis=dict(
            side="left", ticks="", tickfont=dict(family="sans-serif"), ticksuffix=" "
        ),
        hovermode="closest",
        showlegend=False,
    )

    return {"data": data, "layout": layout}

def generate_table_row(id, style, col1, col2, col3):
    return html.Div(id='id',
        className="row table-row",
        style=style,
        children=[
            html.Div(id=col1["id"],
            style={"display": "table", "height": "100%"},
            className="two columns row-department",
            children=col1["children"]
            ),
            html.Div(id=col2["id"],
            style={"text-align": "table", "height": "100%"},
            className="five columns row-department",
            children=col2["children"]
            ),
            html.Div(id=col3["id"],
            style={"text-align": "table", "height": "100%"},
            className="five columns row-department",
            children=col3["children"]
            ),
        ]
    )
    
    pass


#=============LAYOUT================#
app.layout = html.Div(
    id='app-container',
    children=[
    html.Div(       
        id='left-column',
        className='four columns',
        children=[description_card(), generate_control_card()]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)