import pandas as pd
pd.options.mode.chained_assignment = None

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

from dash import dcc, html, callback
from dash.dependencies import Output, Input
from datetime import datetime
from controls.controls_portfolio import *
from includes.google_sheets import *
from plotly.subplots import make_subplots
from utils.utils import *


dash.register_page(__name__)

# Application layout
def serve_layout():
    return html.Div([
            dbc.Row([
                dbc.Col([html.H2('Select start and end date:', 
                        style={'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', 'font-size': '18px', 'text-align': 'left'}),
                       dcc.DatePickerRange(
                        min_date_allowed = portfolio_date_picker_range_controls[0],
                        max_date_allowed = portfolio_date_picker_range_controls[1],
                        display_format='DD/MM/YYYY',
                        updatemode = 'bothdates',
                        number_of_months_shown = 4,
                        start_date = date(2022, 1, 1),
                        end_date = datetime.today().date(),
                        initial_visible_month = datetime.today().date(),                                                 
                        id='portfolio_date_picker' 
                            )], 
                        style={'margin-left': '2.5%', 'margin-top': '1%', 'display': 'inline-block', 'vertical-align': 'top'}),
                dbc.Col([
                    html.Div([html.P(id='total_disbursements')]),
                    html.Div([html.P(id='disbursements')]), 
                    html.Div([html.P(id='pending_disbursements')])
                            ], 
                    style={'margin-left': '2%', 'margin-top': '1%', 'display': 'inline-block', 'vertical-align': 'top'}),
                        
                dbc.Col([
                    html.Div([html.P(id='total_repayments')]), 
                    html.Div([html.P(id='repaid')]),
                            ], 
                    style={'margin-left': '2%', 'margin-top': '1%', 'display': 'inline-block', 'vertical-align': 'top'}),
                
                dbc.Col([
                    html.Div([html.P(id='default')]), 
                    html.Div([html.P(id='succeed_to_collect')])
                            ], 
                    style={'margin-left': '2%', 'margin-top': '1%', 'display': 'inline-block', 'vertical-align': 'top'}),
                        
            ], style={'width':'99.3%', "border": border_portfolio}),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='payments_summary'),
                    dcc.Graph(id='ROI_summary'),
                    dcc.Graph(id='repayment_status')
                ], style={'width': '48%', 'height': '100%', 'display': 'inline-block', 'vertical-align': 'top', "border": border_portfolio}),
                dbc.Col([
                    dcc.Graph(id='repaid_disb'),                                                                           
                    dcc.Graph(id='how_long_at_risk_clients'),
                    dcc.Graph(id='late_repayments_month')
                ], style={'width': '25.5%', 'height': '100%', 'display': 'inline-block', 'vertical-align': 'top', 
                        "border-bottom": border_portfolio,
                        "border-left": border_portfolio,
                        "border-top": border_portfolio}),
                dbc.Col([
                    dcc.Graph(id='repayment_status_count'),
                    dcc.Graph(id='count_status'),
                    dcc.Graph(id='late_repayments_stage')
                ], style={'width': '25.5%', 'height': '100%', 'display': 'inline-block', 'vertical-align': 'top', 
                        "border-bottom": border_portfolio,
                        "border-right": border_portfolio,
                        "border-top": border_portfolio}),
            ]),
            dcc.Store(id='intermediate-disburs-data'),
            dcc.Store(id='intermediate-repayments-data'),
            dcc.Store(id='intermediate-delayed-data'),
            dcc.Store(id='intermediate-bad_client-data'),
            dcc.Interval(n_intervals=0, max_intervals=0, interval=1, id='interval-component')
        ])

layout = serve_layout

@callback(
    Output('intermediate-disburs-data', 'data'),
    Output('intermediate-repayments-data', 'data'),
    Output('intermediate-delayed-data', 'data'),
    Output('intermediate-bad_client-data', 'data'),
    Input('interval-component', 'n_intervals')
)
def read_data(n_intervals):
    df_disbursement = read_disbursements_data()
    df_repayments = read_repayments_data()
    df_delayed_collection = read_delayed_collection()
    df_bad_client_collection = read_bad_clients_repayments()

    return df_disbursement.to_json(date_format='iso', orient='split'), df_repayments.to_json(date_format='iso', orient='split'), df_delayed_collection.to_json(date_format='iso', orient='split'), df_bad_client_collection.to_json(date_format='iso', orient='split')

@callback(
    Output('payments_summary', 'figure'),
    Output('ROI_summary', 'figure'),
    Output('repayment_status', 'figure'),
    Output('repaid_disb', 'figure'),
    
    Output('repayment_status_count', 'figure'),
    Output('how_long_at_risk_clients', 'figure'),
    Output('late_repayments_month', 'figure'),
    Output('count_status', 'figure'),
    Output('late_repayments_stage', 'figure'),
           
    Output('total_disbursements', 'children'),
    Output('total_repayments', 'children'),
    Output('pending_disbursements', 'children'),
    Output('repaid', 'children'),
    Output('disbursements', 'children'),
    Output('default', 'children'),
    Output('succeed_to_collect', 'children'),

    [   
        Input('interval-component', 'n_intervals'),
        Input('portfolio_date_picker', 'start_date'),
        Input('portfolio_date_picker', 'end_date'),

        Input('intermediate-disburs-data', 'data'),
        Input('intermediate-repayments-data', 'data'),
        Input('intermediate-delayed-data', 'data'),
        Input('intermediate-bad_client-data', 'data'),

    ]
)
def date_update(n, start_date, end_date, intermediate_disburs_data, intermediate_repayments_data, intermediate_delayed_data, intermediate_bad_client_data):
   
    df_disbursement = pd.read_json(intermediate_disburs_data, orient='split')
    df_repayments = pd.read_json(intermediate_repayments_data, orient='split')
    df_delayed_collection = pd.read_json(intermediate_delayed_data, orient='split')
    df_bad_client_collection = pd.read_json(intermediate_bad_client_data, orient='split')

    df_bad_client_collection['Date'] = pd.to_datetime(df_bad_client_collection['Date'])
    df_delayed_collection['Due Date'] = pd.to_datetime(df_delayed_collection['Due Date'])
    df_disbursement['Disb Date'] = pd.to_datetime(df_disbursement['Disb Date'])
    df_repayments['Due Date'] = pd.to_datetime(df_repayments['Due Date'])

    df_bad_client_collection.set_index('Date', inplace=True)
    df_bad_client_collection['Date'] = df_bad_client_collection.index
    df_delayed_collection.set_index('Due Date', inplace=True)
    df_disbursement.set_index('Disb Date', inplace=True)
    df_repayments.set_index('Due Date', inplace=True)

    # Payments Summary
    first_date = np.datetime64(datetime.strptime(start_date, '%Y-%m-%d'))
    last_date = np.datetime64(datetime.strptime(end_date, '%Y-%m-%d'))

    df_disbursement_filtered = df_disbursement[(df_disbursement.index >= first_date) & (df_disbursement.index <= last_date)]
    df_repayments_filtered = df_repayments[(df_repayments.index >= first_date) & (df_repayments.index <= last_date)]
    df_delayed_collection_filtered = df_delayed_collection[(df_delayed_collection.index >= first_date) & (df_delayed_collection.index <= last_date)]
    df_bad_client_collection_filtered = df_bad_client_collection[(df_bad_client_collection.index >= first_date) & (df_bad_client_collection.index <= last_date)]

    df_disbursement_grouped = df_disbursement_filtered.groupby(pd.Grouper(freq='M'))['Disb Value'].agg(['sum', 'count'])
    df_repayments_grouped = df_repayments_filtered.groupby(pd.Grouper(freq='M'))[['amount due', 'Repaid']].agg(['sum', 'count'])

    df_disbursement_grouped['month'] = df_disbursement_grouped.index.strftime('%B %Y')
    df_repayments_grouped['month'] = df_repayments_grouped.index.strftime('%B %Y')

    # ROI 
    df_ROI = df_disbursement_filtered.groupby(pd.Grouper(freq='M'))[['Annual', 'Weighted ROI', 'Period ROI', 'Period']].agg(['sum', 'mean'])
    df_ROI['Average ROI'] = df_ROI['Annual']['mean']/12
    df_ROI['Weighted ROI average'] = df_ROI['Weighted ROI']['sum']/12
    df_ROI['Disb month'] = df_disbursement_grouped.index.strftime('%B %Y')

    # Repayment status
    df_repayments_status = df_repayments_filtered.groupby([df_repayments_filtered.index.to_period('M'), 'Status']).sum(numeric_only=True).reset_index()[['Due Date', 'Status', 'amount due']]
    df_repayments_status_grouped = repayment_status(df_repayments_status)
    df_repayments_status_grouped['month'] = df_repayments_status_grouped['month'].apply(lambda x: x.to_timestamp())

    # Numbers
    total_disbursements_num = df_disbursement_grouped['sum'].sum(numeric_only=True)
    total_repayments_num = df_repayments_grouped['amount due']['sum'].sum(numeric_only=True)
    pending_disbersements_num = df_disbursement_filtered[df_disbursement_filtered['Status'] == 'Pending']['Disb Value'].sum(numeric_only=True)
    repaid_num = df_repayments_grouped['Repaid']['sum'].sum(numeric_only=True)
    disbursements_num = total_disbursements_num - pending_disbersements_num
    default_num = df_disbursement_filtered[df_disbursement_filtered['Status'] == 'default']['Disb Value'].sum(numeric_only=True)
    succeed_to_collect_num = df_bad_client_collection_filtered[df_bad_client_collection_filtered['Status'].isin(['Warning', 'LOD', 'on time', 'OTHER/OLD'])]['repayment (w/o full)'].sum(numeric_only=True)

    df_payments = pd.DataFrame(columns=['Num of Repayments', 'Num Of Disbursements', 'Repayments Due', 'Repaid', 'Total Disbursements', 'month'])
    df_payments['Num of Repayments'] = df_repayments_grouped['amount due']['count']
    df_payments['Num Of Disbursements'] = df_disbursement_grouped['count']
    df_payments['Repayments Due'] = df_repayments_grouped['amount due']['sum']
    df_payments['Repaid'] = df_repayments_grouped['Repaid']['sum']
    df_payments['Total Disbursements'] = df_disbursement_grouped['sum']
    df_payments['month'] = df_repayments_grouped.index

    # Plots
    fig_payments_summary = make_subplots(
        specs=[[{"secondary_y": True}]])
    fig_payments_summary.add_bar(
        x=df_payments['month'], y=df_payments['Num of Repayments'], marker_color='#FDAB3D', marker_line_color='black', marker_line_width=1,  name='Num of Repayments'
    )
    fig_payments_summary.add_bar(
        x=df_payments['month'], y=df_payments['Num Of Disbursements'], marker_color='#037F4C', marker_line_color='black', marker_line_width=1, name='Num Of Disbursements'
    )
    fig_payments_summary.add_trace(go.Scatter(
        x=df_payments['month'], y=df_payments['Repayments Due'], marker=dict(size=8), marker_color='#9900FF', name='Repayments Due'), secondary_y=True
    )
    fig_payments_summary.add_trace(go.Scatter(
        x=df_payments['month'], y=df_payments['Repaid'], marker=dict(size=8), marker_color='#00FF00', name='Repaid'), secondary_y=True
    )
    fig_payments_summary.add_trace(go.Scatter(
        x=df_payments['month'], y=df_payments['Total Disbursements'], marker=dict(size=8), marker_color='#0000FF', name='Total Disbursements'), secondary_y=True
    )
    fig_payments_summary.update_layout(legend=dict(
        orientation="h"), 
        xaxis={'type': 'date'}, 
        title='Payments summary',
        margin=margin_dict_potfolio,
        template='plotly_white')

    # Repayment status count
    df_repayment_status_count = df_repayments_filtered[['Status', 'amount due']].groupby(['Status']).sum(numeric_only=True)
    df_repayment_status_count['status'] = df_repayment_status_count.index

    # How long at risk clients
    df_how_long_at_risk_clients = df_delayed_collection_filtered[['group', 'Status']].groupby('group').count()
    df_how_long_at_risk_clients['group'] = df_how_long_at_risk_clients.index

    # Count_status
    df_count_status = df_repayments_filtered[['Status', 'amount due']].groupby(['Status']).count()
    df_count_status['status'] = df_repayment_status_count.index

    # Late_repayments_month
    df_late_repayments_month = df_bad_client_collection_filtered[['repayment (w/o full)', 'Date']].groupby(pd.Grouper(freq='M'))[['repayment (w/o full)']].agg('sum')
    df_late_repayments_month['month repayment'] = df_late_repayments_month.index.strftime('%B %Y')

    # Late_repayments_stage
    df_late_repayments_stage = df_bad_client_collection_filtered[['repayment (w/o full)', 'Status']].groupby('Status').sum(numeric_only=True)
    df_late_repayments_stage['status'] = df_late_repayments_stage.index

    # ROI
    df_ROI = df_ROI[df_ROI['Disb month'] != 'October 2021']

    fig_ROI = go.FigureWidget()
    fig_ROI.add_trace(go.Scatter(
        x=df_ROI.index, y=df_ROI['Average ROI'], marker=dict(size=8), marker_color='#FF0000', name='Average ROI')
    )
    fig_ROI.add_trace(go.Scatter(
        x=df_ROI.index, y=df_ROI['Weighted ROI average'], marker=dict(size=8), marker_color='#0000FF', name='Weighted ROI')
    )
    fig_ROI.update_layout(legend=dict(
        orientation="h"), 
        title='Average ROI, Weighted ROI',
        yaxis_tickformat='.2%',
        margin=margin_dict_potfolio,
        template='plotly_white')

    # Repayment status
    fig_repayment_status = go.FigureWidget()
    fig_repayment_status.add_bar(x=df_repayments_status_grouped['month'], y=df_repayments_status_grouped['Delayed/Collection'],
                                marker_color='#FFC000', marker_line_color='black', marker_line_width=0.5, name='Delayed/Collection')
    fig_repayment_status.add_bar(x=df_repayments_status_grouped['month'], y=df_repayments_status_grouped['Rollover Paid'],
                                marker_color='#ED7D31', marker_line_color='black', marker_line_width=0.5, name='Rollover Paid')
    fig_repayment_status.add_bar(x=df_repayments_status_grouped['month'], y=df_repayments_status_grouped['Pending'],
                                marker_color='#999999', marker_line_color='black', marker_line_width=0.5, name='Pending')
    fig_repayment_status.add_bar(x=df_repayments_status_grouped['month'], y=df_repayments_status_grouped['Fully Repaid'],
                                marker_color='#4472C4', marker_line_color='black', marker_line_width=0.5, name='Fully Repaid')
    fig_repayment_status.update_layout(legend=dict(
        orientation="h"),
        barmode='stack', 
        title='Repayments status',
        margin=margin_dict_potfolio,
        template='plotly_white')

    # Repaid and Disbursements
    fig_repaid_disb = go.FigureWidget()
    fig_repaid_disb.add_bar(x=['disb'], y=[disbursements_num],
                                marker_color='#FFC000', marker_line_color='black', marker_line_width=0.5, name='Disbursements')
    fig_repaid_disb.add_bar(x=['repaid'], y=[repaid_num],
                                marker_color='#ED7D31', marker_line_color='black', marker_line_width=0.5, name='Repaid')
    fig_repaid_disb.update_xaxes({'showgrid': False, 'zeroline': False,  'visible': False})
    fig_repaid_disb.update_layout(legend=dict(
        orientation="h"),
        title='Disbursements/Repaid',
        barmode='group',
        bargap = 0.05,
        margin=margin_dict_potfolio,
        template='plotly_white')
            
    # Repayment status count
    fig_repayment_status_count = go.Figure(data=[go.Pie(labels=df_repayment_status_count['status'], values=df_repayment_status_count['amount due'], marker=dict(colorssrc='Viridis'))])
    fig_repayment_status_count.update_layout(
        title='Repayments status',
        margin=margin_dict_potfolio_right,
        template='seaborn')

    # How long at risk clients
    fig_how_long_at_risk_clients = go.Figure(data=[go.Pie(labels=df_how_long_at_risk_clients['group'], values=df_how_long_at_risk_clients['Status'])])
    fig_how_long_at_risk_clients.update_layout(
        title='How long at risk clients',
        margin=margin_dict_potfolio_right,
        template='seaborn')

    # Late_repayments_month
    fig_late_repayments_month = go.Figure(data=[go.Pie(labels=df_late_repayments_month['month repayment'], values=df_late_repayments_month['repayment (w/o full)'])])
    fig_late_repayments_month.update_layout(
        legend=dict(

        font=dict(size=10),
            ),
        xaxis={'type': 'category'},
        legend_traceorder='grouped',
        title='Late repayments by month',
        margin=margin_dict_potfolio_right,
        template='seaborn')

    # Count_status
    fig_count_status = go.Figure(data=[go.Pie(labels=df_count_status['status'], values=df_count_status['amount due'])])
    fig_count_status.update_layout(
        title='Count status',
        margin=margin_dict_potfolio_right,
        template='seaborn')

    # Late_repayments_stage
    fig_late_repayments_stage = go.Figure(data=[go.Pie(labels=df_late_repayments_stage['status'], values=df_late_repayments_stage['repayment (w/o full)'])])
    fig_late_repayments_stage.update_layout(
        title='Late repayments by stage',
        margin=margin_dict_potfolio_right,
        template='seaborn')

    # Numbers
    total_disbursements = html.P(children = [
        html.Strong(f'Total Disbursements: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{total_disbursements_num}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    total_repayments = html.P(children = [
        html.Strong(f'Total Repayments: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{total_repayments_num}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    pending_disbursements = html.P(children = [
        html.Strong(f'Pending Disburesements: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{pending_disbersements_num}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    repaid  = html.P(children = [
        html.Strong(f'Repaid: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{repaid_num}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    disbursements = html.P(children = [
        html.Strong(f'Disburesements: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{disbursements_num}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    default = html.P(children = [
        html.Strong(f'Default: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{default_num}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])

    succeed_to_collect = html.P(children = [
        html.Strong(f'Succeed To Collect: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{succeed_to_collect_num}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])
    
    return fig_payments_summary, fig_ROI,fig_repayment_status,  fig_repaid_disb, fig_repayment_status_count, fig_how_long_at_risk_clients, fig_late_repayments_month, fig_count_status, fig_late_repayments_stage ,total_disbursements, total_repayments, pending_disbursements, repaid, disbursements, default, succeed_to_collect