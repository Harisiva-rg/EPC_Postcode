import dash
from dash import html, dash_table, dcc
import pandas as pd
from dash.dependencies import Input, Output, State
from datasets import load_dataset

dataset = load_dataset('HarisivaRG/EPC_Postcode_grouped')
EPC_postcode_group = pd.DataFrame(dataset['train'])

EPC_top_100 = EPC_postcode_group.head(100)
# EPC_top_100.loc[:, 'Serial No'] = range(1, 101)

app = dash.Dash(__name__)
server = app.server
app.title = "Domestic Buildings Based on Postcodes"

app.layout = html.Div([
    html.H2("Top 100 postcodes based on building counts", id="subtitle"),
    html.Label("Filter on"),
    dcc.Dropdown(
        id='built-form-dropdown',
        options=[{'label': i, 'value': i} for i in EPC_postcode_group['BUILT_FORM'].unique()],
        value=EPC_postcode_group['BUILT_FORM'].unique()[0],
        multi=True
    ),
    # dcc.Checklist(
    #     id='built-form-checkbox',
    #     options=[{'label': i, 'value': i} for i in EPC_postcode_group['BUILT_FORM'].unique()],
    #     value=[EPC_postcode_group['BUILT_FORM'].unique()[0]]
    # ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in EPC_top_100.columns],
        data=EPC_top_100.to_dict('records'), 
        page_size=50  # Set the page size
    ),
    html.Button('Load More', id='load-more-button', n_clicks=0),  # Add a button component
    html.Div(id='page-number', style={'display': 'none'})  # Hidden div to store the current page number
])

@app.callback(
    Output('table', 'data'),
    Output('subtitle', 'children'),
    Input('built-form-dropdown', 'value'),
    State('table', 'page_current'),  # Get the current page number
    State('page-number', 'children')  # Get the previous page number
)

def update_table(built_forms, current_page_number, prev_page_number):
    if isinstance(built_forms, str):
        built_forms = [built_forms]
    filtered_df = EPC_postcode_group[EPC_postcode_group['BUILT_FORM'].isin(built_forms)]
    page_size = 50  # Set the page size
    if prev_page_number is None:
        prev_page_number = 0
    current_page_number = int(prev_page_number) + 1  # Increment the current page number
    start_index = current_page_number * page_size
    end_index = start_index + page_size
    page_df = filtered_df.iloc[:end_index]  # Slice the DataFrame to return the current page
    page_df = page_df.iloc[start_index:end_index]  # Slice the DataFrame to return the next page
    page_df['Serial No'] = range(start_index + 1, end_index + 1)  # Add serial number column
    subtitle = f"Top {len(page_df)} postcodes with {', '.join(built_forms)} buildings"
    return page_df.to_dict('records'), subtitle

@app.callback(
    Output('page-number', 'children'),
    Input('load-more-button', 'n_clicks'),
    State('page-number', 'children')
)
def update_page_number(n_clicks, prev_page_number):
    if prev_page_number is None:
        prev_page_number = 0
    current_page_number = int(prev_page_number) + 1  # Increment the current page number
    return current_page_number

if __name__ == '__main__':
    app.run_server(debug=True)
