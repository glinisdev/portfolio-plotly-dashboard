from datetime import datetime, date


product_type_controls = [
  'Animal By Product', 
  'Crop', 
  'Exporter', 
  'Inputs',
  'No Type'
]

product_sub_type_controls = [
  'Crop Exporter', 
  'Crop Processor', 
  'Crop Trader', 
  'Fresh Produce', 
  'Inputs',
  'Livestock Processor',
  'Livestock Trader',
  'Product Trader',
  'No Type'
]

weeks_range_controls = [
  '< 1 week', 
  '1 - 2 weeks', 
  '2 - 3 weeks', 
  '4 - 5 weeks', 
  '3 - 4 weeks',
  '> 5 weeks',
]

min_offer_range_controls = [
  '< 700k', 
  '700k - 1kk',
  '1kk - 3kk', 
  '3kk - kk',
  '> 5kk',
  'other'
]

total_buying_range_controls = [
  '< 700k', 
  '700k - 1kk',
  '1kk - 3kk', 
  '3kk - kk',
  '> 5kk',
  'other'
]

trade_desk_score_range_controls = [
  '<50%',
  '50-60%',
  '60-70%', 
  '70-80%', 
  '80-90%',
  'No Score', 
  ]

status_dropdown_controls = [
  'Pending', 
  'Delayed', 
  'Repaid',
  'default',
  'Repaid Late',
  'Rollover Paid'
]

portfolio_date_picker_range_controls = [date(2021, 1, 1), datetime.today().date()]

livebook_date_picker_range_controls = [date(2021, 1, 1), datetime.today().date()]
