import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# read data from postgres, return dataframe

def data_query() -> pd.DataFrame:

    load_dotenv()

    # Connect to DB:
    conn = psycopg2.connect(
        host=os.getenv("POSTRGES_HOST"),
        dbname=os.getenv("POSTRGES_DB"),
        user=os.getenv("POSTRGES_USER"),
        password=os.getenv("POSTRGES_DB_PASSWORD"))

    cursor = conn.cursor()

    # Execute query
    cursor.execute(
        """
        SELECT  LA._id, LA.status, LA.datecreated, LP.producttype, LD.minoffer, LD.totalbuying, LD.periodweeks, 
        CASE 
        WHEN lower(LP.name) LIKE '%milk%' THEN 'milk'
        WHEN lower(LP.name) LIKE '%dap%' THEN 'dap'
        WHEN lower(LP.name) LIKE '%potato%' THEN 'potato'
        WHEN lower(LP.name) LIKE '%maize%' THEN 'maize'
        WHEN lower(LP.name) LIKE '%sheep%' THEN 'sheeps'
        WHEN lower(LP.name) LIKE '%beans%' THEN 'beans'
        WHEN lower(LP.name) LIKE '%tomato%' THEN 'tomatoes'
        WHEN lower(LP.name) LIKE '%tea%' THEN 'tea leaves'
        WHEN lower(LP.name) LIKE '%seed%' THEN 'seeds'
        WHEN lower(LP.name) LIKE '%chicken%' THEN 'chicken'
        WHEN lower(LP.name) LIKE '%broiler%' THEN 'chicken'
        WHEN lower(LP.name) LIKE '%dairy%' THEN 'dairy meal'
        ELSE lower(LP.name)

        END product_name,
        CASE
        WHEN LD.minoffer <= 700000 THEN '< 700k'
        WHEN LD.minoffer > 700000 AND LD.minoffer <= 1000000 THEN '700k - 1kk'
        WHEN LD.minoffer > 1000000 AND LD.minoffer <= 3000000 THEN '1kk - 3kk'
        WHEN LD.minoffer > 3000000 AND LD.minoffer <= 5000000 THEN '3kk - kk'
        WHEN LD.minoffer > 5000000 THEN '> 5kk'
        END min_offer_range,
        
        CASE
        WHEN LD.totalbuying <= 700000 THEN '< 700k'
        WHEN LD.totalbuying > 700000 AND LD.totalbuying <= 1000000 THEN '700k - 1kk'
        WHEN LD.totalbuying > 1000000 AND LD.totalbuying <= 3000000 THEN '1kk - 3kk'
        WHEN LD.totalbuying > 3000000 AND LD.totalbuying <= 5000000 THEN '3kk - kk'
        WHEN LD.totalbuying > 5000000 THEN '> 5kk'
        END total_buying_range,
        
        CASE
        WHEN LD.periodweeks <= 1 THEN '< 1 week'
        WHEN LD.periodweeks > 1 AND LD.periodweeks <= 2 THEN '1 - 2 weeks'
        WHEN LD.periodweeks > 2 AND LD.periodweeks <= 3 THEN '2 - 3 weeks'
        WHEN LD.periodweeks > 3 AND LD.periodweeks <= 4 THEN '3 - 4 weeks'
        WHEN LD.periodweeks > 4 AND LD.periodweeks <= 5 THEN '4 - 5 weeks'
        WHEN LD.periodweeks > 5 THEN '> 5 weeks'
        END weeks_range,
        
        CASE
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore <= 0.1 THEN '0.0 - 0.1'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.1 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.2 THEN '0.1 - 0.2'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.2 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.3 THEN '0.2 - 0.3'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.3 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.4 THEN '0.3 - 0.4'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.4 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.5 THEN '0.4 - 0.5'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.5 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.6 THEN '0.5 - 0.6'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.6 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.7 THEN '0.6 - 0.7'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.7 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.8 THEN '0.7 - 0.8'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.8 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.9 THEN '0.8 - 0.9'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.9 THEN '0.9 - 1.0'
        END trade_desk_score_range,
        
        ((1 - ML.score)*0.6 + ML.categoriestotalscore) AS trade_desk_score
        
        
        FROM loanapplications LA
        JOIN loanproducts LP ON LA.products = LP._id
        JOIN loandeals LD ON LA.dealid = LD._id
        JOIN mlscore ML ON ML.loanid = LA._id

        WHERE LD.totalbuying > 0 AND LA.deleted = False
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=[
        'loan_id',
        'status',
        'date_created',
        'product_type',
        'min_offer',
        'total_buying',
        'period_weeks',
        'product_name',
        'min_offer_range',
        'total_buying_range',
        'weeks_range',
        'trade_desk_score_range',
        'TradeDesk Score'
    ])
    conn.commit()

    return df


def read_product_types_for_livebook():
    
    load_dotenv()

    # Connect to DB:
    conn = psycopg2.connect(
        host=os.getenv("POSTRGES_HOST"),
        dbname=os.getenv("POSTRGES_DB"),
        user=os.getenv("POSTRGES_USER"),
        password=os.getenv("POSTRGES_DB_PASSWORD"))

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT LA._id, LA.name, LA.email, LA.phonenumber, LP.producttype, RATIO_TABLE.totalbuying_per_loan, RATIO_TABLE.fraction, LD.minoffer, LD.totalbuying, LD.periodweeks, 

        CASE
        WHEN lower(LP.name) LIKE '%milk%' THEN 'milk'
        WHEN lower(LP.name) LIKE '%potato%' THEN 'potato'
        WHEN lower(LP.name) LIKE '%maize%' THEN 'maize'
        WHEN lower(LP.name) LIKE '%sheep%' THEN 'sheeps'
        WHEN lower(LP.name) LIKE '%beans%' THEN 'beans'
        WHEN lower(LP.name) LIKE '%tomato%' THEN 'tomatoes'
        WHEN lower(LP.name) LIKE '%tea%' THEN 'tea leaves'
        WHEN lower(LP.name) LIKE '%seed%' THEN 'seeds'
        WHEN lower(LP.name) LIKE '%chicken%' THEN 'chicken'
        WHEN lower(LP.name) LIKE '%broiler%' THEN 'chicken'
        WHEN LP.producttype LIKE 'inputs' THEN 'input'
        ELSE lower(LP.name)
        END product_name,

        CASE
        WHEN LD.minoffer <= 700000 THEN '< 700k'
        WHEN LD.minoffer > 700000 AND LD.minoffer <= 1000000 THEN '700k - 1kk'
        WHEN LD.minoffer > 1000000 AND LD.minoffer <= 3000000 THEN '1kk - 3kk'
        WHEN LD.minoffer > 3000000 AND LD.minoffer <= 5000000 THEN '3kk - kk'
        WHEN LD.minoffer > 5000000 THEN '> 5kk'
        END min_offer_range,

        CASE
        WHEN LD.totalbuying <= 700000 THEN '< 700k'
        WHEN LD.totalbuying > 700000 AND LD.totalbuying <= 1000000 THEN '700k - 1kk'
        WHEN LD.totalbuying > 1000000 AND LD.totalbuying <= 3000000 THEN '1kk - 3kk'
        WHEN LD.totalbuying > 3000000 AND LD.totalbuying <= 5000000 THEN '3kk - kk'
        WHEN LD.totalbuying > 5000000 THEN '> 5kk'
        END total_buying_range,

        CASE
        WHEN LD.periodweeks <= 1 THEN '< 1 week'
        WHEN LD.periodweeks > 1 AND LD.periodweeks <= 2 THEN '1 - 2 weeks'
        WHEN LD.periodweeks > 2 AND LD.periodweeks <= 3 THEN '2 - 3 weeks'
        WHEN LD.periodweeks > 3 AND LD.periodweeks <= 4 THEN '3 - 4 weeks'
        WHEN LD.periodweeks > 4 AND LD.periodweeks <= 5 THEN '4 - 5 weeks'
        WHEN LD.periodweeks > 5 THEN '> 5 weeks'
        END weeks_range,

        CASE
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore <= 0.1 THEN '0.0 - 0.1'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.1 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.2 THEN '0.1 - 0.2'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.2 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.3 THEN '0.2 - 0.3'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.3 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.4 THEN '0.3 - 0.4'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.4 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.5 THEN '0.4 - 0.5'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.5 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.6 THEN '0.5 - 0.6'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.6 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.7 THEN '0.6 - 0.7'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.7 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.8 THEN '0.7 - 0.8'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.8 AND (1 - ML.score)*0.6 + ML.categoriestotalscore < 0.9 THEN '0.8 - 0.9'
        WHEN (1 - ML.score)*0.6 + ML.categoriestotalscore >= 0.9 THEN '0.9 - 1.0'
        END trade_desk_score_range,

        ((1 - ML.score)*0.6 + ML.categoriestotalscore) AS trade_desk_score

        FROM loanapplications LA
        JOIN loanproducts LP ON LA.products = LP._id
        JOIN loandeals LD ON LA.dealid = LD._id
        JOIN mlscore ML ON ML.loanid = LA._id

        JOIN 	(SELECT LA._id, LA.products, LP.totalbuyingprice, SUM_LP.sum as totalbuying_per_loan, LP.totalbuyingprice/SUM_LP.sum AS fraction
                FROM loanapplications LA
                JOIN loanproducts LP on LA.products = LP._id
                JOIN (SELECT LA._id, sum(LP.totalbuyingprice)
                        FROM loanapplications LA
                        JOIN loanproducts LP on LA.products = LP._id
                        GROUP BY LA._id) SUM_LP
                ON LA._id = SUM_LP._id) RATIO_TABLE

        ON LA.products = RATIO_TABLE.products

        WHERE status = 'clientApproved'
        ORDER BY _id
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=[
        'loan_id',        
        'business_name',
        'email',
        'phone_number',
        'product_type',
        'totalbuying_per_loan',
        'fraction',
        'min_offer',
        'total_buying',
        'period_weeks',
        'products',
        'min_offer_range',
        'total_buying_range',
        'weeks_range',
        'trade_desk_score_range',
        'trade_desk_score'
    ])
    conn.commit()

    return df
