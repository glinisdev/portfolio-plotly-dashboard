import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# read data from postgres, return dataframe

def totalbuying() -> pd.DataFrame:

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
        WHEN LD.totalbuying <= 700000 THEN '< 700k'
        WHEN LD.totalbuying > 700000 AND LD.totalbuying <= 1000000 THEN '700k - 1kk'
        WHEN LD.totalbuying > 1000000 AND LD.totalbuying <= 3000000 THEN '1kk - 3kk'
        WHEN LD.totalbuying > 3000000 AND LD.totalbuying <= 5000000 THEN '3kk - kk'
        WHEN LD.totalbuying > 5000000 THEN '> 5kk'
        END categories, STRING_AGG(DISTINCT(LA._id), ', ')
	
        FROM loanapplications LA
        JOIN loandeals LD ON LA.dealid = LD._id
        WHERE LD.totalbuying > 0
        GROUP BY categories
        ORDER BY count
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=['Amount', 'Total Buying Range', 'Loans'])
    conn.commit()

    return df
