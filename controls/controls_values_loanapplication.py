from datetime import datetime, date


product_type_controls = [
  'livestock', 
  'inputs', 
  'crop', 
  'animal_feed', 
  'animal_byproduct'
]

weeks_range_controls = [
  '< 1 week', 
  '1 - 2 weeks', 
  '2 - 3 weeks', 
  '4 - 5 weeks', 
  '3 - 4 weeks',
  '> 5 weeks'
]

min_offer_range_controls = [
  '< 700k', 
  '700k - 1kk',
  '1kk - 3kk', 
  '3kk - kk',
  '> 5kk', 
]

total_buying_range_controls = [
  '< 700k', 
  '700k - 1kk',
  '1kk - 3kk', 
  '3kk - kk',
  '> 5kk', 
]

trade_desk_score_range_controls = [
  '0.2 - 0.3',
  '0.3 - 0.4',
  '0.4 - 0.5', 
  '0.5 - 0.6', 
  '0.6 - 0.7',
  '0.7 - 0.8', 
  '0.8 - 0.9',  
  ]

portfolio_date_picker_range_controls = [date(2021, 1, 1), datetime.today().date()]