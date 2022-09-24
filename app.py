from select import select
from tabnanny import check
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
            html.Br(),
            html.Br(),
            html.P("Select Admit Source"),
            dcc.Dropdown(
                id='admit-select',
                options=[{"label": i, "value": i} for i in admit_list],
                value=admit_list[:],
                multi=True
            ),
            html.Br()
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
        filter_day = filter_df[filter_df["Days of Wk"] == day]
        for ind_x, x_val in enumerate(x_axis):
            sum_of_records = filter_day[filter_day["Check-In Hour"] == x_val]["Number of Records"].sum()
            z[ind_y][ind_x] = sum_of_records

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
    return html.Div(id=id,
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

def generate_table_row_helper(department):
    return generate_table_row(
        department,
        {},
        {"id": department + "_department", "children":html.B(department)},
        {"id": department + "_wait_time", 
        "children": dcc.Graph(
            id=department + "_wait_time_graph",
            style={"height": "100%", "width": "100%"},
            className = "wait_time_graph",
            config={
                "staticPlot": False,
                "editable": False,
                "displayModeBar": False
            },
            figure={
                "layout": dict(
                    margin=dict(l=0, r=0, b=0, t=0, pad=0),
                    xaxis=dict(
                        showgrid=False,
                        showline=False,
                        showticklabels=False,
                        zeroline=False
                    ),
                    yaxis=dict(
                        showgrid=False,
                        showline=False,
                        showticklabels=False,
                        zeroline=False
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    )
                }
            )
        },
        {"id": department + "_patient_score", 
            "children": dcc.Graph(
                id=department + "_score_graph",
                style={"height": "100%", "width": "100%"},
                className = "_patient_score_graph",
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False
                },
                figure={
                    "layout": dict(
                        margin=dict(l=0, r=0, b=0, t=0, pad=0),
                        xaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False
                        ),
                        yaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                },
            ),
        },
    )

def initialize_table():
    header = [
        generate_table_row(
            "header",
            {"height":"50px"},
            {"id": "header_department", "children": html.B("Department")},
            {"id": "header_wait_time_min", "children": html.B("Wait Time Minutes")},
            {"id": "header_care_score", "children": html.B("Care Score")},
        )
    ]

    rows = [generate_table_row_helper(department) for department in all_departments]
    header.extend(rows)
    empty_table = header
    return empty_table

def create_table_figure(department, filter_df, category, category_xrange, category_yrange):
    aggregation = {
        "Wait Time Minute": "mean",
        "Care Score": "mean",
        "Days of Wk": "first",
        "Check-In Time": "first",
        "Check-In Hour": "first"
    }

    df_by_department = filter_df[filter_df["Department"] == department].reset_index()
    grouped = df_by_department.groupby("Encounter Number").agg(aggregation).reset_index()
    patient_id_list = grouped["Encounter Number"]

    x = grouped[category]
    y = list(department for _ in range(len(x)))

    f = lambda x_val: dt.strftime(x_val, "%Y-%m-%d")
    check_in = (
        grouped["Check-In Time"].apply(f),
        + " "
        + grouped["Days of Wk"]
        + " "
        + grouped["Check-In Hour"].map(str)
    )

    text_wait_time = (
        "Patient # : "
        + patient_id_list
        + "<br>Check-In Time: "
        + check_in
        + "<br> Wait Time: "
        + grouped["Wait Time Min"].round(decimals=1).map(str)
        + " Minutes, Care Score : "
        + grouped["Care Score"].round(decimals=1).map(str)
    )

    layout = dict(
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            range=category_xrange,
        ),
        yaxis=dict(
            showgrid=False, showline=False, showticklabels=False, zeroline=False
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    trace = dict(
        x=x,
        y=y,
        mode="markers",
        color="#2c82ff",
        selected=dict(marker=dict(color="ff6347", opacity=1)),
        unselected=dict(marker=dict(opacity=0.1)),
        hoverinfo="text",
        text=text_wait_time,
        customdata=patient_id_list
    )
    return {"data": [trace], "layout": layout}

def generate_patient_table(figure_list, departments, wait_time_xrange, score_xrange):
    header = [
        generate_table_row(
            "header",
            {"height": "50px"},
            {"id": "header_department", "children": html.B("Department")},
            {"id": "header_wait_time_min", "children": html.B("Wait Time Minutes")},
            {"id": "header_care_score", "children": html.B("Care Score")},
        )
    ]
    rows = [generate_table_row_helper(department) for department in departments]

    empty_departments = [item for item in all_departments if item not in departments]

    empty_rows = [generate_table_row_helper(department) for department in empty_departments]

    for ind, department in enumerate(departments):
        rows[ind].children[1].children.figure = figure_list[ind]
        rows[ind].children[2].children.figure = figure_list[ind + len(departments)]
    
    for row in empty_rows[1:]:
        row.style = {"display": "none"}

    empty_rows[0].children[0].children = html.B(style={"visibility": "hidden"})

    empty_rows[0].children[1].children = html.B(style={"visibility": "hidden"})

    empty_rows[0].children[1].children.figure["layout"].update(
        dict(margin=dict(t=-70, b=50, l=0, pad=0))
    )

    empty_rows[0].children[2].children.figure["layout"].update(
        dict(margin=dict(t=-70, b=50, l=0, pad=0))
    )

    empty_rows[0].children[1].children.config["staticPlot"] = True
    empty_rows[0].children[1].children.figure["layout"]["xaxis"].update(
        dict(
            showline=True,
            showticklabels=True,
            tick0=0,
            dtick=20,
            range=wait_time_xrange
        )
    )

    empty_rows[0].children[2].children.figure["layout"]["xaxis"].update(
        dict(
            showline=True,
            showticklabels=True,
            tick0=0,
            dtick=20,
            range=wait_time_xrange
        )
    )

    header.extend(rows)
    header.extend(empty_rows)

    return header
    
#=============LAYOUT================#
app.layout = html.Div(id='app-container',
    children=[
    html.Div(       
        id='left-column',
        className='four columns',
        children=[description_card(), generate_control_card()]
    ),
    html.Div(
        id='right-column',
        className= "eight columns",
        children=[
            html.Div(
                id="patient_volume_card",
                children=[
                    html.B("Patient Volume"),
                    html.Hr(),
                    dcc.Graph(id="patient_volume_hm")
                ]
            ),
            html.Div(
                id="wait_time_card",
                children=[
                    html.B("Patients Wait Time and Satisfactory Scores"),
                    html.Hr(),
                    html.Div(id="wait_time_table", children=initialize_table())
                ]
            )
        ]
    )
])

#========== CALLBACKS

@app.callback(
    Output("patient_volume_hm", "figure"),
    [
        Input("date-picker-select", "start_date"),
        Input("date-picker-select", "end_date"),
        Input("clinic-select", "value"),
        Input("admit-select", "value")
    ]
)
def update_heatmap(start, end, clinic, admit_type):
    start = start + " 00:00:00"
    end = end + " 00:00:00"
    return get_patient_volume_heatmap(start,end,clinic,admit_type)



if __name__ == '__main__':
    app.run_server(debug=True)