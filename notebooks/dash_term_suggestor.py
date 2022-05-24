from turtle import width
import dash
import dash_bootstrap_components as dbc
from dash import html

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [ 
        dbc.Container(
            dbc.Alert("Welcome to the GetGabby Demo!", color="primary"),
            className="p-5",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dbc.Button('test', id='btn-01', size="sm", outline=True, className="me-2 pt-0 pb-0", color="primary"),
                            dbc.Button('test', id='btn-02', size="sm", outline=True, className="me-2 pt-0 pb-0", color="primary"),
                            dbc.Button('test3', id='btn-03', size="sm", outline=True, className="me-2 pt-0 pb-0", color="primary"),
                            dbc.Button('test', id='btn-04', size="sm", outline=True, className="me-2 pt-0 pb-0", color="primary"),
                            dbc.Button('test', id='btn-05', size="sm", outline=True, className="me-2 pt-0 pb-0", color="primary")
                        ]
                    ),
                    width={"size": 8, "offset": 2}
                )
            ]
        )
    ]
)



if __name__ == "__main__":
    app.run_server(debug=True)