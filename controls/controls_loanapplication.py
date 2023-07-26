from controls.controls_values_loanapplication import *
from dash import dcc
from datetime import datetime, timedelta

# Dropdowns

product_type_dropdown = dcc.Dropdown(
    product_type_controls,
    product_type_controls,
    multi=True,
    id='product_type_dropdown', style={'font-size': '110%', 'height': '50%'}
)

weeks_range_dropdown = dcc.Dropdown(
    weeks_range_controls,
    weeks_range_controls,
    multi=True,
    id='weeks_range_dropdown', style={'font-size': '100%', 'height': '50%'}
)

min_offer_dropdown = dcc.Dropdown(
    min_offer_range_controls,
    min_offer_range_controls,
    multi=True,
    id='minoffer_range_dropdown', style={'font-size': '110%', 'height': '50%'}
)

total_buying_dropdown = dcc.Dropdown(
    total_buying_range_controls,
    total_buying_range_controls,
    multi=True,
    id='total_buying_range_dropdown', style={'font-size': '110%', 'height': '50%'}
)

trade_desk_score_dropdown = dcc.Dropdown(
    trade_desk_score_range_controls,
    trade_desk_score_range_controls,
    multi=True,
    id='trade_desk_score_range_dropdown', style={'font-size': '100%', 'height': '50%'}, 
)

# Sliders

weeks_slider = dcc.RangeSlider(
    0,
    10,
    1,
    value=[0, 10],
    id='weeks_slider'
)

trade_desc_score_slider = dcc.RangeSlider(
    0,
    1,
    0.1,
    value=[0, 1],
    id='trade_desk_score_slider',
)

# Margin loan dash
margin_dict = dict(l=0, r=0, t=40, b=40)

# Border loan dash
border = "5px #e6f3ff solid"

