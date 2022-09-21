import dash
import plotly.express as px
import pandas as pd
from dash import Input, Output, html, dcc
import pathlib
from datetime import datetime as dt


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
                options=[{"labels": i, "value": i} for i in clinic_list],
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
                options=[{"labels": i, "value": i} for i in admit_list],
                value=admit_list[:],
                multi=True
            )
        ]
    )




app.layout = html.Div([

])

if __name__ == '__main__':
    app.run_server(debug=True)