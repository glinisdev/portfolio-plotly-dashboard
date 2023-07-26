from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np


def group_product_type(df):
    grouped_df = df.groupby(['loan_id', 'product_type']
                            ).count().groupby('product_type').count()
    grouped_df.sort_values(by=['date_created'], inplace=True)

    return grouped_df


def group_product_name(df):
    grouped_df = df.groupby(['loan_id', 'product_name']
                            ).count().groupby('product_name').count()
    grouped_df.sort_values(by=['date_created'], inplace=True)
    grouped_df = grouped_df[grouped_df['date_created'] > 3]

    return grouped_df


def group_min_offer(df):
    grouped_df = df.drop_duplicates(
        subset=['loan_id']).groupby('min_offer_range').count()

    return grouped_df


def group_total_buying(df):
    grouped_df = df.drop_duplicates(subset=['loan_id']).groupby(
        'total_buying_range').count()

    return grouped_df


def group_week(df):
    grouped_df = df.drop_duplicates(
        subset=['loan_id']).groupby('weeks_range').count()

    return grouped_df


def group_tradedesk_score(df):
    grouped_df = df.drop_duplicates(subset=['loan_id']).groupby(
        'trade_desk_score_range').count()

    return grouped_df


def get_today_loans(df):

    return df[df.date_created == date.today() - timedelta(days=1)].shape[0]


def get_new_loans(df):

    return df[df.status == 'new'].shape[0]


def get_filter_for_moving_year():
    curent_date = datetime.now()
    first_month = curent_date - relativedelta(months=12)
    first_date = datetime(first_month.year, first_month.month, day=1)
    last_date = datetime(curent_date.year, curent_date.month, curent_date.day)

    return np.datetime64(first_date.date()),  np.datetime64(last_date.date())


def calculate_sum_amount_due(df, days_dict, days_dict_count):
    
    disbs_less_0 = []
    disbs_more_31 = []
    disbs_all = []

    for i in range(df.shape[0]):
        if int(df['Days Until Repayemnt'].iloc[i]) < 0:
            days_dict['0-'] += df['Expected Repaym'].iloc[i]

            if df['Deal Name'].iloc[i] not in disbs_less_0:
                days_dict_count['0-'] += 1

            disbs_less_0.append(df['Deal Name'].iloc[i])

        elif int(df['Days Until Repayemnt'].iloc[i]) > 30:
            days_dict['31+'] += df['Expected Repaym'].iloc[i]

            if df['Deal Name'].iloc[i] not in disbs_more_31:
                days_dict_count['31+'] += 1
            
            disbs_more_31.append(df['Deal Name'].iloc[i])

        else:
            try:
                days_dict[df['Days Until Repayemnt Str'].iloc[i]] += df['Expected Repaym'].iloc[i]

                if df['Deal Name'].iloc[i] not in disbs_all:
                    days_dict_count[df['Days Until Repayemnt Str'].iloc[i]] += 1

                disbs_all.append(df['Deal Name'].iloc[i])

            except KeyError:
                continue

    return days_dict, days_dict_count


def group_day_since_repayment(df):
    group = []
    
    for i in df['days_since_repayment_date']:

        if i > 0 and i <= 30:
            group.append('0-30')
        
        elif i >= 31 and i <= 60:
            group.append('31-60')
            
        elif i >= 61 and i <= 90:
            group.append('61-90')
         
        elif i >= 91 and i <= 120:
            group.append('91-120')
            
        elif i >= 121 and i <= 150:
            group.append('121-150')
            
        elif i >= 151 and i <= 180:
            group.append('151-180')
                    
        elif i >= 181 and i <= 210:
            group.append('181-210')
            
        elif i >= 211 and i <= 240:
            group.append('211-240')
            
        elif i >= 241 and i <= 270:
            group.append('241-270')
            
        elif i >= 271 and i <= 300:
            group.append('271-300')
            
        else:
            group.append('300+')

    return group


def business_matcher(df_prods, df_disb):

    loan_id = ['other' for i in range(df_disb.shape[0])]
    
    for i in range(df_disb.shape[0]):
        for j in range(df_prods.shape[0]):
            
            if df_disb['Client Name'].iloc[i].lower() in df_prods['business_name'].iloc[j].lower():
                loan_id[i] = df_prods['loan_id'].iloc[j]
                break
    
            elif df_disb['Client email'].iloc[i] == df_prods['email'].iloc[j]:
                loan_id[i] = df_prods['loan_id'].iloc[j]
                break
                
            elif df_disb['Client phonenumber'].iloc[i] == df_prods['phone_number'].iloc[j]:
                loan_id[i] = df_prods['loan_id'].iloc[j]
                break

    return loan_id


def calculate_disb(df):
    for i in range(df.shape[0]):
        df['Disb Value'].iloc[i] = int(df['Disb Value'].iloc[i] / df['count_products'].iloc[i])
        
    return df


def repayment_status(df):
    new_df = pd.DataFrame(columns = ['month', 'Delayed', 'Collections', 'Default', 'Rollover Paid', 'Pending', 'Fully Repaid'])
    
    month = df['Due Date'].unique()
    
    delayed = [0 for i in range(len(month))]
    collections = [0 for i in range(len(month))]
    default = [0 for i in range(len(month))]
    rollover_paid = [0 for i in range(len(month))]
    pending = [0 for i in range(len(month))]
    fully_repaid = [0 for i in range(len(month))]
    
    new_df['month'] = month
    
    for i in range(len(month)):
        df_month = df[df['Due Date'] == month[i]]
        
        for j in range(df_month.shape[0]):
            if df_month['Status'].iloc[j] == 'Delayed':
                delayed[i] += df_month['amount due'].iloc[j]
                
            elif df_month['Status'].iloc[j] == 'Collections':
                collections[i] += df_month['amount due'].iloc[j]
                
            elif df_month['Status'].iloc[j] == 'Default':
                default[i] += df_month['amount due'].iloc[j]
                
            elif df_month['Status'].iloc[j] == 'Rollover Paid':
                rollover_paid[i] += df_month['amount due'].iloc[j]
                
            elif df_month['Status'].iloc[j] == 'Pending':
                pending[i] += df_month['amount due'].iloc[j]
            
            elif df_month['Status'].iloc[j] == 'Fully Repaid':
                fully_repaid[i] += df_month['amount due'].iloc[j]
                
    new_df['Delayed'] = delayed
    new_df['Collections'] = collections
    new_df['Default'] = default
    new_df['Rollover Paid'] = rollover_paid
    new_df['Pending'] = pending
    new_df['Fully Repaid'] = fully_repaid
    new_df['Delayed/Collection'] = new_df['Delayed'] + new_df['Collections'] + new_df['Default']
    
    return new_df


def calculate_period_weeks(df):
    period_weeks = []

    for i in df['Period Weeks']:
        if i <= 1:
            period_weeks.append('< 1 week')
        elif i > 1 and i <= 2:
            period_weeks.append('1 - 2 weeks')
        elif i > 2 and i <= 3:
            period_weeks.append('2 - 3 weeks')
        elif i > 3 and i <= 4:
            period_weeks.append('3 - 4 weeks')
        elif i > 4 and i <= 5:
            period_weeks.append('4 - 5 weeks')
        elif i > 5:
            period_weeks.append('> 5 weeks')
            
    return period_weeks