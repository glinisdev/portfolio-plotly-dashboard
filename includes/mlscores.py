import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# read data from postgres, return dataframe

def mlscores() -> pd.DataFrame: 

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
        SELECT COUNT(DISTINCT(LA._id)), 

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
        END scoreCategory, STRING_AGG(DISTINCT(LA._id), ', ')

        FROM loanapplications LA
        JOIN mlscore ML ON ML.loanid = LA._id

        GROUP BY scorecategory
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=['Amount', 'Tradedesk Score', 'Loans'])
    conn.commit()

    return df
