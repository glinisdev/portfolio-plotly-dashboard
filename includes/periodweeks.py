import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# read data from postgres, return dataframe

def periodweeks() -> pd.DataFrame:

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
            WHEN LD.periodweeks <= 1 THEN '< 1 week'
            WHEN LD.periodweeks > 1 AND LD.periodweeks <= 2 THEN '1 - 2 weeks'
            WHEN LD.periodweeks > 2 AND LD.periodweeks <= 3 THEN '2 - 3 weeks'
            WHEN LD.periodweeks > 3 AND LD.periodweeks <= 4 THEN '3 - 4 weeks'
            WHEN LD.periodweeks > 4 AND LD.periodweeks <= 5 THEN '4 - 5 weeks'
            WHEN LD.periodweeks > 5 THEN '> 5 weeks'
            END categories, STRING_AGG(DISTINCT(LA._id), ', ')
            
        FROM loanapplications LA
        JOIN loandeals LD ON LA.dealid = LD._id
        WHERE LD.periodweeks > 0
        GROUP BY categories
        ORDER BY count
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=['Amount', 'Period Weeks Range', 'Loans'])
    conn.commit()

    return df
