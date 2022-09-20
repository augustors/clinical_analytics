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

#FUNÇÕES



app.layout = html.Div([

])

if __name__ == '__main__':
    app.run_server(debug=True)