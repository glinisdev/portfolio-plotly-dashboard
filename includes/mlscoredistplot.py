import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# read data from postgres, return dataframe

def mlscoresdistplot() -> pd.DataFrame: 

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
        SELECT DISTINCT(LA._id), ((1 - ML.score)*0.6 + ML.categoriestotalscore)
        FROM loanapplications LA
        JOIN mlscore ML ON ML.loanid = LA._id
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=['Loans', 'Tradedesk Score'])
    conn.commit()

    return df
