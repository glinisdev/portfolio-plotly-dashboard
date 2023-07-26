import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# read data from mongo, return dataframe

def product_name() -> pd.DataFrame:

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
            SELECT COUNT(*), sub_name, STRING_AGG(DISTINCT(_id), ', ') FROM 
        (SELECT COUNT(*) as number_of, 
        
            CASE 
            WHEN lower(name) LIKE '%milk%' THEN 'milk'
            WHEN lower(name) LIKE '%dap%' THEN 'dap'
            WHEN lower(name) LIKE '%potato%' THEN 'potato'
            WHEN lower(name) LIKE '%maize%' THEN 'maize'
            WHEN lower(name) LIKE '%sheep%' THEN 'sheeps'
            WHEN lower(name) LIKE '%beans%' THEN 'beans'
            WHEN lower(name) LIKE '%tomato%' THEN 'tomatoes'
            WHEN lower(name) LIKE '%tea%' THEN 'tea leaves'
            WHEN lower(name) LIKE '%seed%' THEN 'seeds'
            WHEN lower(name) LIKE '%chicken%' THEN 'chicken'
            WHEN lower(name) LIKE '%broiler%' THEN 'chicken'
            WHEN lower(name) LIKE '%dairy%' THEN 'dairy meal'
            ELSE lower(name)
            END sub_name, LA._id
                
        FROM loanapplications LA
        JOIN loandeals LD ON LA.dealid = LD._id
        JOIN loanproducts LP ON LA.products = LP._id
        GROUP BY LA._id, sub_name
        ORDER by number_of DESC) sub

        GROUP BY sub_name
        HAVING COUNT(*) > 2
        ORDER BY count DESC
        """
    )

    # Fetch data
    df = pd.DataFrame(cursor.fetchall(), columns=['Amount', 'Product Name', 'Loans'])
    conn.commit()

    return df
