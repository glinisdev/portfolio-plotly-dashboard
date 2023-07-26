import pandas as pd
pd.options.mode.chained_assignment = None

import dash
import plotly.graph_objects as go

from datetime import datetime
from dash import dcc, html, callback, dash_table as dt
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from controls.controls_portfolio import *
from includes.google_sheets import *
from includes.data_query import *
from plotly.subplots import make_subplots
from utils.utils import *

dash.register_page(__name__, path='')

# Read data
df_disburesments = read_disbursements_data()
df_product_data = read_product_types_for_livebook()

df_disburesments_current_month = df_disburesments[(df_disburesments['Status'] == 'Pending')]
loan_id = business_matcher(df_product_data, df_disburesments_current_month)
df_disburesments_current_month['loan_id_matched'] = loan_id
df_disburesments_current_month = df_product_data.merge(df_disburesments_current_month, how='right', left_on=['loan_id'], right_on=['loan_id_matched'])

# Filling NaNs 
df_disburesments_current_month['fraction'] = df_disburesments_current_month['fraction'].apply(lambda x: 1 if pd.isna(x) else float(x))
df_disburesments_current_month['products'] = df_disburesments_current_month['products'].apply(lambda x: 'other' if pd.isna(x) else x)
df_disburesments_current_month['min_offer_range'] = df_disburesments_current_month['min_offer_range'].apply(lambda x: 'other' if pd.isna(x) else x)
df_disburesments_current_month['total_buying_range'] = df_disburesments_current_month['total_buying_range'].apply(lambda x: 'other' if pd.isna(x) else x)

df_disburesments_current_month['Period Weeks Range'] = calculate_period_weeks(df_disburesments_current_month)

# Calculate based on fraction
df_disburesments_current_month['Disb Value Original'] = df_disburesments_current_month['Disb Value']
df_disburesments_current_month['Disb Value'] = df_disburesments_current_month['Disb Value'] * df_disburesments_current_month['fraction']
df_disburesments_current_month['Expected Repaym'] = df_disburesments_current_month['Expected Repaym'] * df_disburesments_current_month['fraction']
df_disburesments_current_month['Total Repaid'] = df_disburesments_current_month['Total Repaid'] * df_disburesments_current_month['fraction']
df_disburesments_current_month['Outstanding'] = df_disburesments_current_month['Outstanding'] * df_disburesments_current_month['fraction']
# df_disburesments_current_month['Max Disb Value'] = df_disburesments_current_month['Max Disb Value'] * df_disburesments_current_month['fraction']

df_count_products = df_disburesments_current_month.groupby(['products']).count()[['loan_id', 'loan_id_matched']]
df_count_products.sort_values(['loan_id_matched'], ascending=False, inplace=True)
list_count_product_controls = list(df_count_products.index)

range_drow_down_month = list(df_disburesments.drop_duplicates('Disb month')['Disb month'])

# Drop down for livebook products
products_dropdown = dcc.Dropdown(
    list_count_product_controls,
    list_count_product_controls,
    multi=True,
    id='products_dropdown', style={'font-size': '100%', 'height': '50%'}
)

# Drop down for month
month_dropdown = dcc.Dropdown(
    range_drow_down_month,
    range_drow_down_month,
    multi=True,
    id='month_dropdown', style={'font-size': '90%', 'height': '50%'}
)

# Application layout

def serve_layout():
    return html.Div([

    dbc.Row([
        dbc.Col([
            html.Div([html.P(id='total_disbursed')]),
                                ], 
            style={'margin-left': '2%', 'margin-top': '0.5%','margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}), 
        dbc.Col([
            html.Div([html.P(id='total_expected')])
                    ], 
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}),
        dbc.Col([
            html.Div([html.P(id='total_pending')])
                    ], 
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}),
        dbc.Col([
            html.Div([html.P(id='expected_pending_repayments')]),
                              ], 
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}),
        dbc.Col([
            html.Div([html.P(id='invoice_disb')]),
                              ],
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}),
           ],

    style={'width':'98.2%', 
           "border-right": border_portfolio,
           "border-left": border_portfolio,
           "border-top": border_portfolio}),

    dbc.Row([
        dbc.Col([
            html.Div([html.P(id='total_disbursed_by_selected_category')]),
                              ],
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}),
        dbc.Col([
            html.Div([html.P(id='total_expected_by_selected_category')]),
                              ],
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}),
        dbc.Col([
            html.Div([html.P(id='number_of_current_clients')]),
                              ],
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'}),
        dbc.Col([
            html.Div([html.P(id='number_of_current_disburesments')]),
                              ],
            style={'margin-left': '2%', 'margin-top': '0.5%', 'margin-bottom': '0.5%', 'display': 'inline-block', 'vertical-align': 'top'})
    ], 
    style={'width':'98.2%', 
           "border-right": border_portfolio,
           "border-left": border_portfolio,
           "border-top": border_portfolio}),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='fig_amount_due_per_days'),
            dcc.Graph(id='fig_amount_due_per_score'),
            dcc.Graph(id='fig_amount_due_product_type'),
            dcc.Graph(id='fig_amount_due_product_sub_type'),
            ], style={'width': '58%', 'height': '100%', 'display': 'inline-block', 'vertical-align': 'top',
                      "border-right": border_portfolio,
                      "border-left": border_portfolio,
                      "border-top": border_portfolio}),
        dbc.Col([
            dcc.DatePickerRange(
                min_date_allowed = livebook_date_picker_range_controls[0],
                max_date_allowed = livebook_date_picker_range_controls[1],
                display_format='DD/MM/YYYY',
                updatemode = 'bothdates',
                number_of_months_shown = 4,
                start_date = date(2021, 1, 1),
                end_date = datetime.today().date(),
                initial_visible_month = datetime.today().date(),                                                 
                id='livebook_date_picker', 
                style={"margin-left": "2%","margin-top": "2%", "margin-bottom": "2%"}
            ),
            month_dropdown,
            html.H5("Clients status", style={
                "margin-left": "2%","margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            status_dropdown,
            html.H5("Clients categories", style={
                "margin-left": "2%","margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            product_type_dropdown,
            html.H5("Clients sub categories", style={
                "margin-left": "2%","margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            product_sub_type_dropdown,
            html.H5("Products", style={
                "margin-left": "2%", "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            products_dropdown,
            html.H5("Period weeks ranges", style={
                "margin-left": "2%", "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            weeks_range_dropdown,
            html.H5("Total buying ranges", style={
                "margin-left": "2%", "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            total_buying_dropdown,
            html.H5("Offers ranges", style={
                "margin-left": "2%", "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            min_offer_dropdown,
            html.H5("Trade Desk Scores ranges", style={
                "margin-left": "2%", "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            trade_desk_score_dropdown,
            html.H5("Trade Desk Score", style={
                "margin-left": "2%", "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            trade_desc_score_slider,
            html.H5("Period weeks", style={
                "margin-left": "2%", "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "110%"}),
            weeks_slider,

            dcc.Graph(id='fig_live_concentration'),
        ], style={'width': '40%', 'height': '100%', 'display': 'inline-block', 'vertical-align': 'top',
                  "border-right": border_portfolio,
                  "border-top": border_portfolio}),
    ]),
    dbc.Row([
            dbc.Col([dcc.Graph(id='fig_status_disb')],
                    style={"margin-left": "0%", "margin-right": "0%",  "margin-top": "0%", 'width': "28%", 'display': 'inline-block'}),
            dbc.Col([dcc.Graph(id='fig_status_count')], 
                    style={"margin-left": "0%", "margin-right": "0%",  "margin-top": "0%", 'width': "28%", 'display': 'inline-block'}),
            dbc.Col([dcc.Graph(id='fig_delayed_clients')], 
                    style={"margin-left": "0%", "margin-top": "0%", 'width': "43%", 'display': 'inline-block', "border-left": border_portfolio}),

            dbc.Row(
                    [
                    html.Div([
                    html.Button("Download full report", id="btn_csv_2"), 
                    dcc.Download(id="download-dataframe-csv_2")], style={"margin-left": "1%",  "margin-top": "1%", 'width': "100%", 'display': 'inline-block'}),

                    html.Div([
                    html.Button("Download full report (division into products)", id="btn_csv"),
                    dcc.Download(id="download-dataframe-csv")], style={"margin-left": "1%", "margin-top": "1%",  "margin-bottom": "1%", 'width': "100%", 'display': 'inline-block'}),
                    ], style= {"border-top": border_portfolio})],

            style={'width': "98.2%", 'display': 'inline-block', 
                   "border-right": border_portfolio,
                   "border-top": border_portfolio,
                   "border-bottom": border_portfolio, 
                   "border-left": border_portfolio}),
    
    html.Div(id='table_2', style={"margin-left": "2.5%", "margin-right": "5%",  "margin-top": "5%", 'width': "70%"}),
    html.Div(id='table_1', style={"margin-left": "2.5%", "margin-right": "5%",  "margin-top": "2.5%"}),
    dcc.Store(id='intermediate-disb-data'),
    dcc.Store(id='intermediate-product-data'),
    dcc.Interval(n_intervals=0, max_intervals=0, interval=1, id='interval-component'),
    ])

layout = serve_layout

@callback(
     Output('month_dropdown', 'value'),
    [
        Input('livebook_date_picker', 'start_date'),
        Input('livebook_date_picker', 'end_date'),
        Input('intermediate-disb-data', 'data'),
    ]
)
def set_months_dropdown(start_date, end_date, intermediate_disb_data):

    df_disburesments = pd.read_json(intermediate_disb_data, orient='split') 

    df_disburesments_filtered = df_disburesments

    df_disburesments_filtered['Disb Date'] = pd.to_datetime(df_disburesments_filtered['Disb Date'])
    df_disburesments_filtered.set_index('Disb Date', inplace=True)

    first_date = np.datetime64(datetime.strptime(start_date, '%Y-%m-%d'))
    last_date = np.datetime64(datetime.strptime(end_date, '%Y-%m-%d'))

    df_disburesments_filtered = df_disburesments_filtered[(df_disburesments_filtered.index >= first_date) & (df_disburesments_filtered.index <= last_date)]
    range_drow_down_month = list(df_disburesments_filtered.drop_duplicates('Disb month')['Disb month'])

    return range_drow_down_month

@callback(
    Output('intermediate-disb-data', 'data'),
    Output('intermediate-product-data', 'data'),
    Input('interval-component', 'n_intervals')
)
def read_data(n_intervals):
    df_disburesments = read_disbursements_data()
    df_product_data = read_product_types_for_livebook()

    return df_disburesments.to_json(date_format='iso', orient='split'), df_product_data.to_json(date_format='iso', orient='split')

@callback(
    Output('product_type_dropdown', 'value'),

    [
        Input('status_dropdown', 'value'),
        Input('intermediate-disb-data', 'data'),
    ]
)
def set_sub_categories_option(status_dropdown, intermediate_disb_data,):

    df_disburesments = pd.read_json(intermediate_disb_data, orient='split')
    df_disburesments_current_month = df_disburesments[df_disburesments['Status'].isin(status_dropdown)]
    
    df_count_category = df_disburesments_current_month.drop_duplicates(['Client Category'])
    list_count_categories_controls = sorted(list(df_count_category['Client Category']))

    return list_count_categories_controls

@callback(
    Output('product_sub_type_dropdown', 'value'),

    [
        Input('product_type_dropdown', 'value'),
        Input('status_dropdown', 'value'),
        Input('intermediate-disb-data', 'data'),
    ]
)
def set_products_option(selected_types, status_dropdown, intermediate_disb_data):

    df_disburesments = pd.read_json(intermediate_disb_data, orient='split')
    df_disburesments_current_month = df_disburesments[(df_disburesments['Status'].isin(status_dropdown)) & (df_disburesments['Client Category'].isin(selected_types))]

    df_count_sub_products = df_disburesments_current_month.drop_duplicates(['Sub Category'])
    list_count_sub_product_controls = sorted(list(df_count_sub_products['Sub Category']))
                                             

    return list_count_sub_product_controls

@callback(
    Output('products_dropdown', 'value'),

    [
        Input('product_type_dropdown', 'value'),
        Input('product_sub_type_dropdown', 'value'),
        Input('status_dropdown', 'value'),
        Input('intermediate-disb-data', 'data'),
        Input('intermediate-product-data', 'data'),
    ]
)
def set_categories_option(selected_types, selected_sub_types, status_dropdown, intermediate_disb_data, intermediate_product_data):

    df_disburesments = pd.read_json(intermediate_disb_data, orient='split')
    df_product_data = pd.read_json(intermediate_product_data, orient='split')

    df_disburesments_current_month = df_disburesments[
        (df_disburesments['Status'].isin(status_dropdown)) & 
        (df_disburesments['Client Category'].isin(selected_types)) &
        (df_disburesments['Sub Category'].isin(selected_sub_types))
        ]
    
    loan_id = business_matcher(df_product_data, df_disburesments_current_month)
    df_disburesments_current_month['loan_id_matched'] = loan_id
    df_disburesments_current_month = df_product_data.merge(df_disburesments_current_month, how='right', left_on=['loan_id'], right_on=['loan_id_matched'])
    df_disburesments_current_month['products'] = df_disburesments_current_month['products'].apply(lambda x: 'other' if pd.isna(x) else x)
 
    df_count_products = df_disburesments_current_month.groupby(['products']).count()[['loan_id', 'loan_id_matched']]
    df_count_products.sort_values(['loan_id_matched'], ascending=False, inplace=True)
    list_count_product_controls = sorted(list(df_count_products.index))

    return list_count_product_controls

@callback(
    Output("download-dataframe-csv", "data"),
    [
        Input("btn_csv", "n_clicks"),        
        Input('intermediate-disb-data', 'data'),
        Input('intermediate-product-data', 'data')
    ],
    prevent_initial_call=True,
)
def func(n_clicks, intermediate_disb_data, intermediate_product_data):

    if n_clicks:

        # Read data
        df_disburesments = pd.read_json(intermediate_disb_data, orient='split')
        df_product_data = pd.read_json(intermediate_product_data, orient='split')

        df_disburesments_current_month = df_disburesments[(df_disburesments['Status'] == 'Delayed') | (df_disburesments['Status'] == 'Pending')]

        loan_id = business_matcher(df_product_data, df_disburesments_current_month)
        df_disburesments_current_month['loan_id_matched'] = loan_id
        df_disburesments_current_month = df_product_data.merge(df_disburesments_current_month, how='right', left_on=['loan_id'], right_on=['loan_id_matched'])

        # Filling NaNs 
        df_disburesments_current_month['fraction'] = df_disburesments_current_month['fraction'].apply(lambda x: 1 if pd.isna(x) else float(x))
        df_disburesments_current_month['products'] = df_disburesments_current_month['products'].apply(lambda x: 'other' if pd.isna(x) else x)
        df_disburesments_current_month['min_offer_range'] = df_disburesments_current_month['min_offer_range'].apply(lambda x: 'other' if pd.isna(x) else x)
        df_disburesments_current_month['total_buying_range'] = df_disburesments_current_month['total_buying_range'].apply(lambda x: 'other' if pd.isna(x) else x)
        df_disburesments_current_month['Period Weeks Range'] = calculate_period_weeks(df_disburesments_current_month)

        # Calculate based on fraction
        df_disburesments_current_month['Disb Value Original'] = df_disburesments_current_month['Disb Value']
        df_disburesments_current_month['Disb Value'] = df_disburesments_current_month['Disb Value'] * df_disburesments_current_month['fraction']
        df_disburesments_current_month['Expected Repaym'] = df_disburesments_current_month['Expected Repaym'] * df_disburesments_current_month['fraction']
        df_disburesments_current_month['Total Repaid'] = df_disburesments_current_month['Total Repaid'] * df_disburesments_current_month['fraction']
        df_disburesments_current_month['Outstanding'] = df_disburesments_current_month['Outstanding'] * df_disburesments_current_month['fraction']
        # df_disburesments_current_month['Max Disb Value'] = df_disburesments_current_month['Max Disb Value'] * df_disburesments_current_month['fraction']

        df_disburesments_current_month_for_report = df_disburesments_current_month[[
                'Client Name', 
                'Deal Name', 
                'Status', 
                'Disb Value Original', 
                'Disb Value',  
                'Expected Repaym', 
                'Disb Date', 
                'Disb month', 
                'Repaym Due Date', 
                'Repaym Due Date Month', 
                'Days Until Repayemnt', 
                'Client Category',
                'Sub Category',
                'products', 
                'Period Weeks', 
                'Period Weeks Range', 
                'min_offer_range', 
                'total_buying_range', 
                'TD Score',
                'loan_id_matched'
            ]]
        
        df_disburesments_current_month_for_report.columns = [
                'Client Name',
                'Deal Name',
                'Status',
                'Disb Value',
                'Disb Value by Products',
                'Expected Repaym',
                'Disb Date',
                'Disb month',
                'Repaym Due Date',
                'Repaym Due Date Month',
                'Days Until Repayemnt',
                'Client Category',
                'Sub Category',
                'products',
                'Period Weeks',
                'Period Weeks Range',
                'Offer Range',
                'Total Buying Range',
                'TD Score',
                'loan_id'
            ]

        return dcc.send_data_frame(df_disburesments_current_month_for_report.to_csv, f"report_products_division_{datetime.now().strftime('%d_%m_%Y')}.csv")

@callback(
    Output("download-dataframe-csv_2", "data"),
    [
        Input("btn_csv_2", "n_clicks"),
        Input('intermediate-disb-data', 'data'),
        Input('intermediate-product-data', 'data')
    ],
    prevent_initial_call=True,
)
def func(n_clicks, intermediate_disb_data, intermediate_product_data):

    if n_clicks:

        # Read data
        df_disburesments = pd.read_json(intermediate_disb_data, orient='split')
        df_product_data = pd.read_json(intermediate_product_data, orient='split')

        df_disburesments_current_month = df_disburesments[(df_disburesments['Status'] == 'Delayed') | (df_disburesments['Status'] == 'Pending')]

        loan_id = business_matcher(df_product_data, df_disburesments_current_month)
        df_disburesments_current_month['loan_id_matched'] = loan_id
        df_disburesments_current_month = df_product_data.merge(df_disburesments_current_month, how='right', left_on=['loan_id'], right_on=['loan_id_matched'])

        # Filling NaNs 
        df_disburesments_current_month['fraction'] = df_disburesments_current_month['fraction'].apply(lambda x: 1 if pd.isna(x) else float(x))
        df_disburesments_current_month['products'] = df_disburesments_current_month['products'].apply(lambda x: 'other' if pd.isna(x) else x)
        df_disburesments_current_month['min_offer_range'] = df_disburesments_current_month['min_offer_range'].apply(lambda x: 'other' if pd.isna(x) else x)
        df_disburesments_current_month['total_buying_range'] = df_disburesments_current_month['total_buying_range'].apply(lambda x: 'other' if pd.isna(x) else x)
        df_disburesments_current_month['Period Weeks Range'] = calculate_period_weeks(df_disburesments_current_month)

        # Calculate based on fraction
        df_disburesments_current_month['Disb Value Original'] = df_disburesments_current_month['Disb Value']
        df_disburesments_current_month['Disb Value'] = df_disburesments_current_month['Disb Value'] * df_disburesments_current_month['fraction']
        df_disburesments_current_month['Expected Repaym'] = df_disburesments_current_month['Expected Repaym'] * df_disburesments_current_month['fraction']
        df_disburesments_current_month['Total Repaid'] = df_disburesments_current_month['Total Repaid'] * df_disburesments_current_month['fraction']
        df_disburesments_current_month['Outstanding'] = df_disburesments_current_month['Outstanding'] * df_disburesments_current_month['fraction']
        # df_disburesments_current_month['Max Disb Value'] = df_disburesments_current_month['Max Disb Value'] * df_disburesments_current_month['fraction']

        df_disburesments_current_month_for_report = df_disburesments_current_month[[
                'Client Name', 
                'Deal Name', 
                'Status', 
                'Disb Value Original', 
                'Expected Repaym', 
                'Disb Date', 
                'Disb month', 
                'Repaym Due Date', 
                'Repaym Due Date Month', 
                'Days Until Repayemnt', 
                'Client Category',
                'Sub Category',            
                'Period Weeks', 
                'Period Weeks Range', 
                'min_offer_range', 
                'total_buying_range', 
                'TD Score',
                'loan_id_matched'
            ]]
        
        df_disburesments_current_month_for_report.columns = [
                'Client Name',
                'Deal Name',
                'Status',
                'Disb Value',
                'Expected Repaym',
                'Disb Date',
                'Disb month',
                'Repaym Due Date',
                'Repaym Due Date Month',
                'Days Until Repayemnt',
                'Client Category',
                'Sub Category',
                'Period Weeks',
                'Period Weeks Range',
                'Offer Range',
                'Total Buying Range',
                'TD Score',
                'loan_id'
            ]
        
        df_disburesments_current_month_for_report.drop_duplicates(['Deal Name'], inplace=True)

        return dcc.send_data_frame(df_disburesments_current_month_for_report.to_csv, f"report_{datetime.now().strftime('%d_%m_%Y')}.csv")

@callback(
    Output('fig_amount_due_per_days', 'figure'),
    Output('fig_amount_due_per_score', 'figure'),
    Output('fig_amount_due_product_type', 'figure'),
    Output('fig_live_concentration', 'figure'),
    Output('fig_status_disb', 'figure'),
    Output('fig_status_count', 'figure'),
    Output('fig_delayed_clients', 'figure'),
    Output('fig_amount_due_product_sub_type', 'figure'),
    
    Output('total_disbursed', 'children'),
    Output('total_expected', 'children'),
    Output('total_pending', 'children'),
    Output('expected_pending_repayments', 'children'),
    Output('invoice_disb', 'children'),
    Output('total_disbursed_by_selected_category', 'children'),
    Output('total_expected_by_selected_category', 'children'),
    Output('number_of_current_clients', 'children'),
    Output('number_of_current_disburesments', 'children'),

    Output('table_1', 'children'),
    Output('table_2', 'children'),

    [
        Input('interval-component', 'n_intervals'),
        Input('product_type_dropdown', 'value'),
        Input('product_sub_type_dropdown', 'value'),
        Input('products_dropdown', 'value'),
        Input('weeks_range_dropdown', 'value'),
        Input('minoffer_range_dropdown', 'value'),
        Input('total_buying_range_dropdown', 'value'),
        Input('trade_desk_score_range_dropdown', 'value'),
        Input('weeks_slider', 'value'),
        Input('trade_desk_score_slider', 'value'),
        Input('status_dropdown', 'value'),
        Input('intermediate-disb-data', 'data'),
        Input('intermediate-product-data', 'data'),
        Input('livebook_date_picker', 'start_date'),
        Input('livebook_date_picker', 'end_date'),
        Input('month_dropdown', 'value')

    ]
)
def display_click_products_data(n, type, sub_type, products, weeks, minoffer, total_buying, trade_desk_score, weeks_slider, trade_desk_score_slider, status_dropdown, intermediate_disb_data, intermediate_product_data, start_date, end_date, month_dropdown):
    
    # Read data
    df_disburesments = pd.read_json(intermediate_disb_data, orient='split')
    df_product_data = pd.read_json(intermediate_product_data, orient='split')

    df_disburesments_current_month = df_disburesments[df_disburesments['Status'].isin(status_dropdown)]

    loan_id = business_matcher(df_product_data, df_disburesments_current_month)
    df_disburesments_current_month['loan_id_matched'] = loan_id
    df_disburesments_current_month = df_product_data.merge(df_disburesments_current_month, how='right', left_on=['loan_id'], right_on=['loan_id_matched'])

    # Filling NaNs 
    df_disburesments_current_month['fraction'] = df_disburesments_current_month['fraction'].apply(lambda x: 1 if pd.isna(x) else float(x))
    df_disburesments_current_month['products'] = df_disburesments_current_month['products'].apply(lambda x: 'other' if pd.isna(x) else x)
    df_disburesments_current_month['min_offer_range'] = df_disburesments_current_month['min_offer_range'].apply(lambda x: 'other' if pd.isna(x) else x)
    df_disburesments_current_month['total_buying_range'] = df_disburesments_current_month['total_buying_range'].apply(lambda x: 'other' if pd.isna(x) else x)

    df_disburesments_current_month['Period Weeks Range'] = calculate_period_weeks(df_disburesments_current_month)

    # Calculate based on fraction
    df_disburesments_current_month['Disb Value Original'] = df_disburesments_current_month['Disb Value']
    df_disburesments_current_month['Disb Value'] = df_disburesments_current_month['Disb Value'] * df_disburesments_current_month['fraction']
    df_disburesments_current_month['Expected Repaym'] = df_disburesments_current_month['Expected Repaym'] * df_disburesments_current_month['fraction']
    df_disburesments_current_month['Total Repaid'] = df_disburesments_current_month['Total Repaid'] * df_disburesments_current_month['fraction']
    df_disburesments_current_month['Outstanding'] = df_disburesments_current_month['Outstanding'] * df_disburesments_current_month['fraction']
    # df_disburesments_current_month['Max Disb Value'] = df_disburesments_current_month['Max Disb Value'] * df_disburesments_current_month['fraction']
    
    df_disburesments_current_month['Disb Date'] = pd.to_datetime(df_disburesments_current_month['Disb Date'])
    df_disburesments_current_month.set_index('Disb Date', inplace=True)

    first_date = np.datetime64(datetime.strptime(start_date, '%Y-%m-%d'))
    last_date = np.datetime64(datetime.strptime(end_date, '%Y-%m-%d'))

    df_disburesments_current_month = df_disburesments_current_month[(df_disburesments_current_month.index >= first_date) & (df_disburesments_current_month.index <= last_date)]

    df_disburesments_current_month = df_disburesments_current_month[
        (df_disburesments_current_month['Client Category'].isin(type)) &
        (df_disburesments_current_month['Sub Category'].isin(sub_type)) &
        (df_disburesments_current_month.products.isin(products)) &
        (df_disburesments_current_month['Period Weeks Range'].isin(weeks)) &
        (df_disburesments_current_month.min_offer_range.isin(minoffer)) &
        (df_disburesments_current_month.total_buying_range.isin(total_buying)) &
        (df_disburesments_current_month['TD group'].isin(trade_desk_score)) &
        (df_disburesments_current_month['TD Score'].between(trade_desk_score_slider[0], trade_desk_score_slider[1], inclusive='both')) & 
        (df_disburesments_current_month['Period Weeks'].between(weeks_slider[0], weeks_slider[1], inclusive='both')) &
        (df_disburesments_current_month['Disb month'].isin(month_dropdown))
        ]
    
    df_disburesments_current_month_for_table = df_disburesments_current_month[['Client Name', 'Deal Name', 'Client Category', 'Sub Category', 'products', 'Disb Value', 'Disb Value Original', 'TD Score']]
    df_disburesments_current_month_for_table.columns = ['Client Name', 'Deal Name', 'Client Category', 'Sub Category', 'Products', 'Disb Value Per Product', 'Disb Value', 'TD Score']
    df_disburesments_current_month_for_table['Disb Value Per Product'] = df_disburesments_current_month_for_table['Disb Value Per Product'].round(0)

    data_table_1 = dt.DataTable(
        df_disburesments_current_month_for_table.to_dict('records'), 
        [{"name": i, "id": i} for i in df_disburesments_current_month_for_table.columns],
        sort_action="native",
        sort_mode="multi"
        )
    
    df_disburesments_current_month_for_table_without_products = df_disburesments_current_month_for_table.drop_duplicates(['Deal Name'])
    df_disburesments_current_month_for_table_without_products = df_disburesments_current_month_for_table_without_products[['Client Name', 'Deal Name', 'Client Category', 'Sub Category', 'Disb Value', 'TD Score']]
    
    data_table_2 = dt.DataTable(
        df_disburesments_current_month_for_table_without_products.to_dict('records'), 
        [{"name": i, "id": i} for i in df_disburesments_current_month_for_table_without_products.columns],
        sort_action="native",
        sort_mode="multi"
        )

    # Amount due per days
    df_amount_due_per_days = pd.DataFrame()
    days_list = list(range(31))
    days_list.append('31+')
    days_list.insert(0, '0-')
    days_list = [str(i) for i in days_list]
    df_amount_due_per_days['days'] = days_list
    days_dict = dict(zip(list(df_amount_due_per_days['days']), [0 for i in range(df_amount_due_per_days.shape[0])]))
    days_dict_count = dict(zip(list(df_amount_due_per_days['days']), [0 for i in range(df_amount_due_per_days.shape[0])]))
    df_disburesments_current_month['Days Until Repayemnt Str'] = df_disburesments_current_month['Days Until Repayemnt'].apply(lambda x: str(x).replace('.0', ''))
    formatted_dict, formatted_dict_count = calculate_sum_amount_due(df_disburesments_current_month, days_dict, days_dict_count)
    df_amount_due_per_days['Amount Due'] = list(formatted_dict.values())
    df_amount_due_per_days['Deals Number'] = list(formatted_dict_count.values())
    df_amount_due_per_days = df_amount_due_per_days.iloc[1: , :]

    # Amount due per score
    df_amount_due_per_days_repayments = df_disburesments_current_month[['Deal Name', 'TD group', 'Expected Repaym']].groupby('TD group').sum(numeric_only=True).sort_index()['Expected Repaym']
    df_amount_due_per_score = df_disburesments_current_month.drop_duplicates(['Deal Name'])
    df_amount_due_per_score = df_amount_due_per_score[['Deal Name', 'TD group']].groupby(['TD group']).count().sort_index()
    df_amount_due_per_score['Expected Repaym'] = df_amount_due_per_days_repayments                                                                                 
    df_amount_due_per_score['TD Score'] = df_amount_due_per_score.index
    custom_dict__td_group = {'<50%':0, '51-60%':1, '61-70%':2, '71-80%':3,  '81-90%':4}
    df_amount_due_per_score = df_amount_due_per_score.sort_values(by=['TD Score'], key=lambda x: x.map(custom_dict__td_group))
    df_amount_due_per_score.columns = ['Deals Number', 'Amount due', 'TD Score']

    # Live concentration
    df_live_concentration = df_disburesments_current_month[['Client Name', 'Deal Name', 'Disb Value Original']]
    df_live_concentration.drop_duplicates(['Deal Name'], inplace=True)
    df_live_concentration = df_live_concentration[['Client Name', 'Disb Value Original']]
    df_live_concentration = df_live_concentration.groupby(['Client Name']).sum()
    df_live_concentration['Client Name'] = df_live_concentration.index
    df_live_concentration.reset_index(inplace=True, drop=True)
    df_live_concentration.sort_values(['Disb Value Original'], inplace=True, ascending=False)
    
    if df_live_concentration.shape[0] >= 6:
        insert_row = {"Disb Value Original": df_live_concentration[5:]['Disb Value Original'].sum(), "Client Name": "Others",}
        df_live_concentration_cut = pd.concat([df_live_concentration[:5], pd.DataFrame(insert_row, index=[7])])
        df_live_concentration_cut['Client Name'] = ['Client 1', 'Client 2', 'Client 3', 'Client 4', 'Client 5', 'Other']
        df_live_concentration_cut.columns = ['sum Disb/Paym Value', 'clients']
    else: 
        df_live_concentration_cut = df_live_concentration
        df_live_concentration_cut['Client Name'] = [f'Client {i+1}' for i in range(df_live_concentration.shape[0])]
        df_live_concentration_cut.columns = ['sum Disb/Paym Value', 'clients']

    # Amount due per product type
    df_amount_due_per_product_type_disbursements = df_disburesments_current_month[['Deal Name', 'Client Category', 'Disb Value']].groupby('Client Category').sum(numeric_only=True).sort_index()['Disb Value']
    df_amount_due_per_product_type = df_disburesments_current_month.drop_duplicates(['Deal Name'])
    df_amount_due_per_product_type = df_amount_due_per_product_type[['Deal Name', 'Client Category']].groupby(['Client Category']).count().sort_index()
    df_amount_due_per_product_type['Disb Value'] = df_amount_due_per_product_type_disbursements
    df_amount_due_per_product_type['Client Category'] = df_amount_due_per_product_type.index
    df_amount_due_per_product_type.columns = ['Deals count', 'sum Disb Value', 'Client Category']

    # Amount due per product type
    df_amount_due_per_product_sub_type_disbursements = df_disburesments_current_month[['Deal Name', 'Sub Category', 'Disb Value']].groupby('Sub Category').sum(numeric_only=True).sort_index()['Disb Value']
    df_amount_due_per_product_sub_type = df_disburesments_current_month.drop_duplicates(['Deal Name'])
    df_amount_due_per_product_sub_type = df_amount_due_per_product_sub_type[['Deal Name', 'Sub Category']].groupby(['Sub Category']).count().sort_index()
    df_amount_due_per_product_sub_type['Disb Value'] = df_amount_due_per_product_sub_type_disbursements
    df_amount_due_per_product_sub_type['Sub Category'] = df_amount_due_per_product_sub_type.index
    df_amount_due_per_product_sub_type.columns = ['Deals count', 'sum Disb Value', 'Sub Category']

    # Status Delayed/Pending
    df_delayed_pending = df_disburesments[(df_disburesments['Status'] == 'Delayed') | (df_disburesments['Status'] == 'Pending')]
    df_delayed_pending = df_delayed_pending[['Client Name', 'Deal Name', 'Status', 'Disb Value']]

    # Status Count
    df_status_count = df_delayed_pending.drop_duplicates(['Client Name'])
    df_status_count = df_status_count.groupby(['Status']).count()
    df_status_count['Status'] = df_status_count.index

    # Status Disb
    df_status_disb = df_delayed_pending.groupby(['Status']).sum(numeric_only=True)
    df_status_disb['Status'] = df_status_disb.index

    # Delayed Clients
    df_delayed = df_disburesments[(df_disburesments['Status'] == 'Delayed')]
    df_delayed = df_delayed[['Client Name', 'Disb Value']]

    # Numbers
    invoice_num_disb = df_disburesments[df_disburesments['Status'] == 'Invoice']['Disb Value'].sum()
    invoice_num_repay = df_disburesments[df_disburesments['Status'] == 'Invoice']['Expected Repaym'].sum()

    total_disbursed_by_selected_category_num = df_disburesments_current_month['Disb Value'].sum()
    total_expected_by_selected_category_num = df_disburesments_current_month['Expected Repaym'].sum()

    total_pending_num = df_disburesments[df_disburesments['Status'] == 'Pending']['Disb Value'].sum()
    expected_pending_repayments_num = df_disburesments[df_disburesments['Status'] == 'Pending']['Expected Repaym'].sum()

    client_at_risk_disb_num = df_disburesments[df_disburesments['Status'] == 'Delayed']['Disb Value'].sum()
    client_at_risk_repay_num = df_disburesments[df_disburesments['Status'] == 'Delayed']['Expected Repaym'].sum()

    total_expected_num = expected_pending_repayments_num + client_at_risk_repay_num + invoice_num_repay
    total_disbursed_num = total_pending_num + client_at_risk_disb_num + invoice_num_disb

    number_of_current_clients_num = df_disburesments_current_month.drop_duplicates(['Client Name'])['Disb Value'].count()
    number_of_current_disburesments_num = df_disburesments_current_month.drop_duplicates(['Deal Name'])['Disb Value'].count()

    # Amount Due Per Days
    fig_amount_due_per_days = make_subplots(
        specs=[[{"secondary_y": True}]])
    fig_amount_due_per_days.add_bar(
        x=df_amount_due_per_days['days'], y=df_amount_due_per_days['Amount Due'], marker_color='#00FFFF', marker_line_color='black', marker_line_width=1,  name='Amount Due')
    fig_amount_due_per_days.add_trace(go.Scatter(
        x=df_amount_due_per_days['days'], y=df_amount_due_per_days['Deals Number'], marker=dict(size=8), marker_color='#0000FF', name='Deals Number'), secondary_y=True
    )
    fig_amount_due_per_days.update_layout(
        legend=dict(orientation="h"),
        xaxis={'type': 'category'}, title='Amount Due per Days', template='plotly_white')

    # Amount Due Per TD Score
    fig_amount_due_per_score = make_subplots(
        specs=[[{"secondary_y": True}]])
    fig_amount_due_per_score.add_bar(
        x=df_amount_due_per_score['TD Score'], y=df_amount_due_per_score['Amount due'], marker_color='#FF9900', marker_line_color='black', marker_line_width=1,  name='Amount Due')
    fig_amount_due_per_score.add_trace(go.Scatter(
        x=df_amount_due_per_score['TD Score'], y=df_amount_due_per_score['Deals Number'], marker=dict(size=8), marker_color='#FCE5CD', name='Deals Number'), secondary_y=True
    )
    fig_amount_due_per_score.update_layout(
        legend=dict(orientation="h"),
        xaxis={'type': 'category'}, title='Amount Due per TD Score', template='plotly_white')

    # Live concentration
    fig_live_concentration = go.Figure(data=[go.Pie(labels=df_live_concentration_cut['clients'], values=df_live_concentration_cut['sum Disb/Paym Value'], hole=.7)])
    fig_live_concentration.update_layout(
        legend=dict(orientation="v", x=-0.25, y=1),
        title='Live concentration',
        template='seaborn',
        margin=go.layout.Margin(l=10, r=10, b=10, t=100))

    # Status delayed/pending count
    fig_status_count = go.Figure(data=[go.Pie(labels=df_status_count['Status'], values=df_status_count['Client Name'], hole=.7)])
    fig_status_count.update_layout(
        legend=dict(orientation="v", x=-0.25, y=0, bgcolor='rgba(0,0,0,0)'),
        title='Count by status',
        template='seaborn',
        margin=go.layout.Margin(l=15, r=20, b=25, t=100))

    # Status delayed/pending disb
    fig_status_disb = go.Figure(data=[go.Pie(labels=df_status_disb['Status'], values=df_status_disb['Disb Value'], hole=.7)])
    fig_status_disb.update_layout(
        legend=dict(orientation="v", x=-0.25, y=0, bgcolor='rgba(0,0,0,0)'),
        title='Disbursements by status',
        template='seaborn',
        margin=go.layout.Margin(l=20, r=15, b=25, t=100))

    # Status delayed/pending disb
    fig_delayed_clients = go.Figure(data=[go.Pie(labels=df_delayed['Client Name'], values=df_delayed['Disb Value'], hole=.7)])
    fig_delayed_clients.update_layout(
        legend=dict(orientation="v", x=-1, y=1, bgcolor='rgba(0,0,0,0)'),
        title='Delayed Clients',
        template='seaborn',  
        # margin=go.layout.Margin(l=50, r=0, b=50, t=100)
        )

    # Amount Due per Client Category
    fig_amount_due_product_type = make_subplots(
        specs=[[{"secondary_y": True}]])
    fig_amount_due_product_type.add_bar(
        x=df_amount_due_per_product_type['Client Category'], y=df_amount_due_per_product_type['sum Disb Value'], marker_color='#6699ff', marker_line_color='black', marker_line_width=1,  name='Disb Value')
    fig_amount_due_product_type.add_trace(go.Scatter(
        x=df_amount_due_per_product_type['Client Category'], y=df_amount_due_per_product_type['Deals count'], marker_color='#339966', name='Deals count'), secondary_y=True
    )
    fig_amount_due_product_type.update_layout(
        legend=dict(orientation="h", x=0, y=-0.15),
        xaxis={'type': 'category'}, title='Disbursements per Client Category', template='plotly_white')
    
    # Amount Due per Product Sub Type
    fig_amount_due_product_sub_type = make_subplots(
        specs=[[{"secondary_y": True}]])
    fig_amount_due_product_sub_type.add_bar(
        x=df_amount_due_per_product_sub_type['Sub Category'], y=df_amount_due_per_product_sub_type['sum Disb Value'], marker_color='#4040bf', marker_line_color='black', marker_line_width=1,  name='Disb Value')
    fig_amount_due_product_sub_type.add_trace(go.Scatter(
        x=df_amount_due_per_product_sub_type['Sub Category'], y=df_amount_due_per_product_sub_type['Deals count'], marker_color='#006666', name='Deals count'), secondary_y=True
    )
    fig_amount_due_product_sub_type.update_layout(
        legend=dict(orientation="h", x=0, y=-0.30),
        xaxis={'type': 'category'}, title='Disbursements per Sub Category', template='plotly_white')

    total_disbursed = html.P(children = [
        html.Strong(f'Total Disbursed: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(total_disbursed_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    total_expected = html.P(children = [
        html.Strong(f'Total Expected: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(total_expected_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    total_pending = html.P(children = [
        html.Strong(f'Total Pending: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(total_pending_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    expected_pending_repayments = html.P(children = [
        html.Strong(f'Expected Pending Repayments: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(expected_pending_repayments_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    invoice_disb = html.P(children = [
        html.Strong(f'Invoice: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(invoice_num_disb)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])
    
    total_disbursed_by_selected_category = html.P(children = [
        html.Strong(f'Dusbursed for selected status: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(total_disbursed_by_selected_category_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    total_expected_by_selected_category = html.P(children = [
        html.Strong(f'Expected Repayments for selected status: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(total_expected_by_selected_category_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    number_of_current_clients = html.P(children = [
        html.Strong(f'Number of current clients: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(number_of_current_clients_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    number_of_current_disburesments = html.P(children = [
        html.Strong(f'Number of current disburesements: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(number_of_current_disburesments_num)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    return fig_amount_due_per_days, fig_amount_due_per_score, fig_amount_due_product_type, fig_live_concentration, fig_status_disb, fig_status_count, fig_delayed_clients, fig_amount_due_product_sub_type, total_disbursed, total_expected, total_pending, expected_pending_repayments, invoice_disb, total_disbursed_by_selected_category, total_expected_by_selected_category, number_of_current_clients, number_of_current_disburesments, data_table_1, data_table_2
