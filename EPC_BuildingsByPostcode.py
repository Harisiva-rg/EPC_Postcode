import pandas as pd
import dash
from dash import html, dash_table, dcc
from dash.dependencies import Input, Output, State
from datasets import load_dataset

dataset = load_dataset('HarisivaRG/EPC_Postcode_grouped')
EPC_postcode_group = dataset['train'].to_pandas()

EPC_top_100 = EPC_postcode_group.head(100)


app = dash.Dash(__name__)
server = app.server
app.title = "Domestic Buildings Based on Postcodes"

app.layout = html.Div([
    html.H2("Top postcodes based on building counts", id="subtitle"),
    html.Label("Built Form"),
    dcc.Dropdown(
        id='built-form-dropdown',
        options=[{'label': i, 'value': i} for i in EPC_postcode_group['BUILT_FORM'].unique()],
        value=EPC_postcode_group['BUILT_FORM'].unique()[0],
        multi=True
    ),
    html.Label("Property type"),
    dcc.Dropdown(
        id='property-type-dropdown',
        options=[{'label': i, 'value': i} for i in EPC_postcode_group['PROPERTY_TYPE'].unique()],
        value=EPC_postcode_group['PROPERTY_TYPE'].unique(),
        multi=True
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": "Serial No", "id": "Serial No"}] + [{"name": i, "id": i} for i in EPC_top_100.columns],
        data=[],
    )
])

@app.callback(
    Output('table', 'data'),
    Output('subtitle', 'children'),
    Input('built-form-dropdown', 'value'),
    Input('property-type-dropdown', 'value')
)

def update_table(built_forms, property_types):
    if isinstance(built_forms, str):
        built_forms = [built_forms]
    if isinstance(property_types, str):
        property_types = [property_types]
    filtered_df = EPC_postcode_group[EPC_postcode_group['BUILT_FORM'].isin(built_forms)]
    filtered_df = filtered_df[filtered_df['PROPERTY_TYPE'].isin(property_types)]
    filtered_df = filtered_df.sort_values(by='count', ascending=False)
    top_100_df = pd.concat([filtered_df[filtered_df['BUILT_FORM'] == bf].head(100) for bf in built_forms])
    top_100_df= top_100_df.sort_values(by='count', ascending=False)
    top_100_df['Serial No'] = range(1, len(top_100_df)+1)
    top_100_df = top_100_df[['Serial No'] + list(top_100_df.columns[:-1])]
    subtitle = f"Top postcodes with {', '.join(built_forms)} buildings"
    return top_100_df.to_dict('records'), subtitle

if __name__ == '__main__':
    app.run_server(debug=True)
