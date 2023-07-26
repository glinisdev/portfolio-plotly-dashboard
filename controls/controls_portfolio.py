from controls.controls_values_portfolio import *
from dash import dcc
from datetime import datetime

# Dropdowns

product_type_dropdown = dcc.Dropdown(
    product_type_controls,
    product_type_controls,
    multi=True,
    id='product_type_dropdown', style={'font-size': '95%', 'height': '50%'}
)

product_sub_type_dropdown = dcc.Dropdown(
    product_sub_type_controls,
    product_sub_type_controls,
    multi=True,
    id='product_sub_type_dropdown', style={'font-size': '95%', 'height': '50%'}
)

weeks_range_dropdown = dcc.Dropdown(
    weeks_range_controls,
    weeks_range_controls,
    multi=True,
    id='weeks_range_dropdown', style={'font-size': '95%', 'height': '50%'}
)

min_offer_dropdown = dcc.Dropdown(
    min_offer_range_controls,
    min_offer_range_controls,
    multi=True,
    id='minoffer_range_dropdown', style={'font-size': '95%', 'height': '50%'}
)

total_buying_dropdown = dcc.Dropdown(
    total_buying_range_controls,
    total_buying_range_controls,
    multi=True,
    id='total_buying_range_dropdown', style={'font-size': '95%', 'height': '50%'}
)

trade_desk_score_dropdown = dcc.Dropdown(
    trade_desk_score_range_controls,
    trade_desk_score_range_controls,
    multi=True,
    id='trade_desk_score_range_dropdown', style={'font-size': '95%', 'height': '50%'}, 
)

delayed_pending_radioelement = dcc.RadioItems(
    ['Pending Clients', 'Delayed Clients', 'Pending and Delayed Clients'], 'Pending Clients',
    id='delayed_pending_radioelement'
)

status_dropdown = dcc.Dropdown(
    status_dropdown_controls,
    ['Pending'],
    multi=True,
    id='status_dropdown', style={'font-size': '95%', 'height': '50%'}
)

portfolio_date_picker = dcc.DatePickerRange(
    min_date_allowed = portfolio_date_picker_range_controls[0],
    max_date_allowed = portfolio_date_picker_range_controls[1],
    display_format='DD/MM/YYYY',
    updatemode = 'bothdates',
    number_of_months_shown = 4,
    start_date = date(2022, 1, 1),
    end_date = datetime.today().date(),
    initial_visible_month = datetime.today().date(),                                                 
    id='portfolio_date_picker' 
)

livebook_date_picker = dcc.DatePickerRange(
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
    100,
    10,
    value=[0, 100],
    id='trade_desk_score_slider',
)

# Margin portfolio
margin_dict_potfolio = dict(l=50, r=50, t=100, b=100)

# Margin portfolio for right side
margin_dict_potfolio_right = dict(l=10, r=10, t=100, b=100)

# Border portfolio
border_portfolio = "3px #b3b3b3 solid"

