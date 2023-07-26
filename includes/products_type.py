import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# read data from mongo, return dataframe

def product_type() -> pd.DataFrame:

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
        SELECT COUNT(*), sub.producttype, STRING_AGG(DISTINCT(_id), ', ') FROM 
        (SELECT COUNT(*), LP.producttype, LA._id FROM loanapplications LA
        JOIN loandeals LD ON LA.dealid = LD._id
        JOIN loanproducts LP ON LA.products = LP._id
        GROUP BY LA._id, LP.producttype) sub
        GROUP BY producttype
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=['Amount', 'Product Type', 'Loans'])
    conn.commit()

    return df

