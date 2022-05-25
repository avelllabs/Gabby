from email.policy import default
from pydoc import classname
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash import Dash, html, Input, Output, callback_context

from collections import defaultdict

import phrase_data_model
phrase_data_model.load_data_models()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [ 
        dbc.Container(
            dbc.Alert("Welcome to the GetGabby Demo!", color="primary"),
            className="p-5",
        ),
        dbc.Row( #category selection
            [
                dbc.Col(
                    html.Div(
                        [
                            dcc.Dropdown(['TVs', 'Speakers', 'Headphones', 'Tablets', 'Smartwatches'], 
                                id='dropdown-category',
                                placeholder='Select a Category...'),
                            html.Div(id='category-message'),
                            html.Hr()
                        ]
                    ),
                    width={"size": 8, "offset": 2},
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Button('test', id='btn-01', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-02', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-03', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-04', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-05', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-06', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-07', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-08', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-09', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                dbc.Button('test', id='btn-10', size="sm", outline=True, className="me-2 mt-3", color="primary"),
                                
                            ], 
                            className="align-middle text-left"
                        ),
                        html.Br(),
                        html.Div(
                            [
                                "Suggested terms ...",
                                html.Br(),
                                dbc.Button('test', id='btn-sg-01', size="sm", outline=True, className="me-2 mt-3", color="secondary"),
                                dbc.Button('test', id='btn-sg-02', size="sm", outline=True, className="me-2 mt-3", color="secondary"),
                                dbc.Button('test', id='btn-sg-03', size="sm", outline=True, className="me-2 mt-3", color="secondary"),
                                dbc.Button('test', id='btn-sg-04', size="sm", outline=True, className="me-2 mt-3", color="secondary"),
                                dbc.Button('test', id='btn-sg-05', size="sm", outline=True, className="me-2 mt-3", color="secondary"),
                                

                            ],
                            className=" text-left me-6 mt-6" 
                        )
                    ],
                    width={"size": 6, "offset": 2},
                    
                ),
                dbc.Col(
                    [ 
                        dbc.Button('Show more Terms', id='btn-more', className="me-2 mt-3", color="primary"),
                        html.Hr(),
                        html.Div(id='selected-terms'),
                    ],
                    width={"size": 2},
                    className="border-start border-primary align-top text-center"
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id='suggested-terms'),
                    width={"size": 8, "offset": 2}, 
                )
            ]
        )
    ]
)

btn_terms = {f'btn-{i+1:02d}': f'feature-{i+1:02d}' for i in range(10)}
user_terms = set()

@app.callback(
    [
        Output('category-message', 'children'),
        Output('btn-01', 'children'),
        Output('btn-02', 'children'),
        Output('btn-03', 'children'),
        Output('btn-04', 'children'),
        Output('btn-05', 'children'),
        Output('btn-06', 'children'),
        Output('btn-07', 'children'),
        Output('btn-08', 'children'),
        Output('btn-09', 'children'),
        Output('btn-10', 'children'),
    ],
    [ 
        Input('dropdown-category', 'value'),
        Input('btn-more', 'n_clicks')
    ]
)
def choose_category(selected_category, btn_more):
    global btn_terms
    message = ""
    seed_terms = list(btn_terms.values())
    if selected_category is not None:
        message = f'Getting reviews for "{selected_category}"... Please choose terms / features / aspects about {selected_category} that are important to you!'
        seed_terms = phrase_data_model.select_top_terms(10)
        for i in range(10):
            btn_terms[f'btn-{i+1:02d}'] = seed_terms[i]
    return message, *seed_terms



@app.callback(
    Output('selected-terms', 'children'),
    [
        Input('btn-01', 'n_clicks'),
        Input('btn-02', 'n_clicks'),
        Input('btn-03', 'n_clicks'),
        Input('btn-04', 'n_clicks'),
        Input('btn-05', 'n_clicks'),
        Input('btn-06', 'n_clicks'),
        Input('btn-07', 'n_clicks'),
        Input('btn-08', 'n_clicks'),
        Input('btn-09', 'n_clicks'),
        Input('btn-10', 'n_clicks')
    ]
)
def displayClick(btn1, btn2, btn3, btn4, btn5,
                    btn6, btn7, btn8, btn9, btn10):
    global user_terms
    global btn_terms

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    #print(btn1, btn2, btn3, btn4, btn5)

    #print(changed_id)
    if 'btn' in changed_id:
        btn_id = changed_id.split('.')[0]
        _term = btn_terms[btn_id]
        if _term in user_terms:
            user_terms.remove(_term)
        else:
            user_terms.add(_term)
    
    return html.Div(
        [html.P(ut) for ut in sorted(user_terms)]
    )

#TODO: toggle the outline
#TODO: make the suggestions
#TODO: integrate the search
#TODO: run it all with category data


if __name__ == "__main__":
    app.run_server(debug=True)