import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, html, callback
from dash.dependencies import Output, Input
from controls.controls_loanapplication import *
from includes.data_query import data_query
from utils.utils import *

dash.register_page(__name__)

layout = html.Div(
    [
        dbc.Row([
                dbc.Col([html.Div([html.P(id='loan_applications_amount')])], 
                        style={'margin-left': '10%', 'display': 'inline-block', 'vertical-align': 'top'}),

                dbc.Col([html.Div([html.P(id='today_loans')])],
                        style={'margin-left': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),

                dbc.Col([html.Div([html.P(id='new_loans')])], 
                        style={'margin-left': '25%', 'display': 'inline-block', 'vertical-align': 'top'})
                ], 
                style={'width': '99%', "border": border}),
        dbc.Row(
            [
                dbc.Col([
                    dcc.Graph(id='product_types',
                              style={'height': '25%'}),
                    dcc.Graph(id='product_names',
                              style={'height': '25%'}),
                    dcc.Graph(id='period_weeks',
                              style={'height': '25%'})
                ],
                    style={'width': '30%', 'height': '50%', 'display': 'inline-block', 'vertical-align': 'top', "border": border}),

                dbc.Col([
                    dcc.Graph(id='minoffer',
                              style={'height': '18.75%'}),
                    dcc.Graph(id='total_buying',
                              style={'height': '18.75%'}),
                    dcc.Graph(id='ml_scores',
                              style={'height': '18.75%'}),    
                ],
                    style={'width': '30%', 'height': '100%', 'display': 'inline-block', 'vertical-align': 'top', "border": border}),

                dbc.Col(
                    [
                        html.H5("Product types", style={
                            "margin-bottom": "2.5%", "margin-top": "0.25%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "130%"}),
                        product_type_dropdown,
                        html.H5("Period weeks ranges", style={
                            "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "130%"}),
                        weeks_range_dropdown,
                        html.H5("Total buying ranges", style={
                            "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "130%"}),
                        total_buying_dropdown,
                        html.H5("Offers ranges", style={
                            "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "130%"}),
                        min_offer_dropdown,
                        html.H5("Trade Desk Scores ranges", style={
                            "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "130%"}),
                        trade_desk_score_dropdown,
                        html.H5("Trade Desk Score", style={
                            "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "130%"}),
                        trade_desc_score_slider,
                        html.H5("Period weeks", style={
                            "margin-bottom": "2.5%", "margin-top": "2.5%", 'font-family': 'system-ui', 'font-weight': 'normal', "font-size": "130%"}),
                        weeks_slider,
                        dcc.Graph(id='ml_distplot',
                                  style={'width': '100%'})

                    ], style={'width': '38%', 'height': '100%', 'display': 'inline-block', 'vertical-align': 'top',  "border": border}),
            ]),
            dcc.Interval(n_intervals=0, max_intervals=0, interval=1, id='interval-component')
    ])


@callback(
    Output('product_types', 'figure'),
    Output('product_names', 'figure'),
    Output('minoffer', 'figure'),
    Output('total_buying', 'figure'),
    Output('period_weeks', 'figure'),
    Output('ml_scores', 'figure'),
    Output('ml_distplot', 'figure'),

    Output('loan_applications_amount', 'children'),
    Output('today_loans', 'children'),
    Output('new_loans', 'children'),

    [   
        Input('interval-component', 'n_intervals'),
        Input('product_type_dropdown', 'value'),
        Input('weeks_range_dropdown', 'value'),
        Input('minoffer_range_dropdown', 'value'),
        Input('total_buying_range_dropdown', 'value'),
        Input('trade_desk_score_range_dropdown', 'value'),
        Input('weeks_slider', 'value'),
        Input('trade_desk_score_slider', 'value')
    ]
)
def product_type_filter(n, type, weeks, minoffer, total_buying, trade_desk_score, weeks_slider, trade_desk_score_slider):

    df = data_query()
    
    df_filtered = df[
        (df.product_type.isin(type)) &
        (df.weeks_range.isin(weeks)) &
        (df.min_offer_range.isin(minoffer)) &
        (df.total_buying_range.isin(total_buying)) &
        (df.trade_desk_score_range.isin(trade_desk_score)) &
        (df['TradeDesk Score'].between(trade_desk_score_slider[0], trade_desk_score_slider[1], inclusive='both')) &
        (df.period_weeks.between(
            weeks_slider[0], weeks_slider[1], inclusive='both'))
    ]

    # Product types histogram
    df_product_types = group_product_type(df_filtered)
    fig_types = go.FigureWidget()
    fig_types.add_bar(x=df_product_types.index,
                      y=df_product_types['date_created'], text=df_product_types['date_created'], marker_color='#008B8B')
    fig_types.update_layout(
        title='Loans Product Types', margin=margin_dict
        # font_size=15
    )
    fig_types.update_yaxes(title_text='Loans')

    # Product names histgram
    df_product_names = group_product_name(df_filtered)
    fig_names = go.FigureWidget()
    fig_names.add_bar(x=df_product_names.index,
                      y=df_product_names['date_created'], text=df_product_names['date_created'], marker_color='#008B8B')
    fig_names.update_layout(
        title='Loans Product Names', margin=margin_dict
        # font_size=15
    )
    fig_names.update_yaxes(title_text='Loans')

    # Min offer histogram
    df_minoffer = group_min_offer(df_filtered)
    df_minoffer = df_minoffer.reindex(min_offer_range_controls)
    fig_minoffer = go.FigureWidget()
    fig_minoffer.add_bar(
        x=df_minoffer.index, y=df_minoffer['date_created'], text=df_minoffer['date_created'], marker_color='#008B8B')
    fig_minoffer.update_layout(
        title='Loans Offer Range', margin=margin_dict
        # font_size=15
    )
    fig_minoffer.update_yaxes(title_text='Loans')

    # Total buying histogram
    df_totalbuying = group_total_buying(df_filtered)
    df_totalbuying = df_totalbuying.reindex(total_buying_range_controls)
    fig_totalbuying = go.FigureWidget()
    fig_totalbuying.add_bar(
        x=df_totalbuying.index, y=df_totalbuying['date_created'], text=df_totalbuying['date_created'], marker_color='#008B8B')
    fig_totalbuying.update_layout(
        title='Loans Total Buying', margin=margin_dict
        # font_size=15
    )
    fig_totalbuying.update_yaxes(title_text='Loans')

    # Period weeks histogram
    df_periodweeks = group_week(df_filtered)
    df_periodweeks = df_periodweeks.reindex(weeks_range_controls)
    fig_periodweeks = go.FigureWidget()
    fig_periodweeks.add_bar(
        x=df_periodweeks.index, y=df_periodweeks['date_created'], text=df_periodweeks['date_created'], marker_color='#008B8B')
    fig_periodweeks.update_layout(
        title='Loans Period Weeks', margin=margin_dict
        # font_size=15
    )
    fig_periodweeks.update_yaxes(title_text='Loans')

    # Trade desk score histogram
    df_mlscores = group_tradedesk_score(df_filtered)
    df_mlscores = df_mlscores.reindex(trade_desk_score_range_controls)
    fig_mlscores = go.FigureWidget()
    fig_mlscores.add_bar(
        x=df_mlscores.index, y=df_mlscores['date_created'], text=df_mlscores['date_created'], marker_color='#008B8B')
    fig_mlscores.update_layout(
        title='Loans Tradedesk Score', margin=margin_dict
        # font_size=15
    )
    fig_mlscores.update_yaxes(title_text='Loans')

    # Dist plot TradeDeskscore
    fig_score_distplot = px.histogram(
        df_filtered,
        x='TradeDesk Score',
        marginal='box',
        histnorm='percent',
        color_discrete_sequence=['darkcyan'],
        opacity=0.6)
    fig_score_distplot.update_layout(
        title='Loans Tradedesk Score', margin=margin_dict
        # font_size=15
    )
    fig_score_distplot.update_yaxes(title_text='%')

    loan_applications_number =df.shape[0]
    today_loans_number = get_today_loans(df)
    new_loans_number = get_new_loans(df)

    loan_applications = html.P(children = [
        html.Strong(f'Loan applications amount: ', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(loan_applications_number)}', style={
        'color': 'black', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])
    
    today_loans = html.P(children = [
        html.Strong(f'Today loans: ', style={
        'color': '#0b9e3f', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(today_loans_number)}', style={
        'color': '#0b9e3f', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])
    
    new_loans = html.P(children = [
        html.Strong(f'New loans: ', style={
        'color': '#0b9e3f', 'font-family': 'system-ui', 'font-weight': 'bold', "font-size": "20px"}),
        html.Span(f'{int(new_loans_number )}', style={
        'color': '#0b9e3f', 'font-family': 'system-ui', 'font-weight': '400', "font-size": "20px"}),
        ])
        
    return fig_types, fig_names, fig_minoffer, fig_totalbuying, fig_periodweeks, fig_mlscores, fig_score_distplot, loan_applications, today_loans, new_loans
