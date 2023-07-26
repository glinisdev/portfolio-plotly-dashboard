import os.path
import pandas as pd
pd.options.mode.chained_assignment = None

from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from includes.utils import *


def read_disbursements_data():
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1ViaHMRU1p79kdgVRRPvYts-RD7pFFkCKznlPPcRGz54'
    SAMPLE_RANGE_NAME = 'Disbursements!A:AH'
   
    creds = None

    if os.path.exists('google_api_auth/token.json'):
        creds = Credentials.from_authorized_user_file('google_api_auth/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_api_auth/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google_api_auth/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        columns = values[0]

        df = pd.DataFrame(columns=columns)

        for i in range(1, len(values)):
            insert_row = dict(zip(columns, values[i]))
            df = pd.concat([df, pd.DataFrame(insert_row, index=[i-1])])

        numeric_columns = ['Disb Value', 
                           'Expected Repaym', 
                           'Total Repaid', 
                           'Outstanding', 
                        #    'Actual Gain',  
                        #    'Max Disb Value', 
                        #    'dis_month', 
                        #    'Rep_month', 
                        #    'Year'
                           ]

        for column in df:
            if column in numeric_columns:
                df[column] = df[column].apply(lambda x: 0 if x == '#N/A' else x)
                df[column] = df[column].apply(lambda x: 0 if x == '-' else x)
                df[column] = df[column].apply(lambda x: float(x.replace(',', '')) if x else None)
                
        df['TD Score'] = pd.to_numeric(df['TD Score'], errors='coerce')
        # df['TD Score'] = df['TD Score'].apply(lambda x: x.strip())
        # df['TD Score'] = df['TD Score'].apply(lambda x: float(x.replace(',', '')) if x else None)

        df['Repaym Due Date'] = df['Repaym Due Date'].apply(lambda x: pd.Timestamp(x).to_pydatetime())
        df['Disb Date'] =  df['Disb Date'].apply(lambda x: pd.Timestamp(x).to_pydatetime())

        df['Period'] = df['Period'].apply(lambda x: x.split('.', 1)[0])
        df['Period'] = df['Period'].apply(lambda x: int(x))

        df['Days Until Repayemnt'] = df['Repaym Due Date'] - datetime.today() + timedelta(days=1)
        df['Days Until Repayemnt'] = df['Days Until Repayemnt'].apply(lambda x: x.days)
        df['Period Weeks'] = df['Period'] / 7
        df['Markup'] = df['Expected Repaym'] - df['Disb Value']
        df['Period ROI'] = df['Markup'] / df['Disb Value']
        df['Annual'] = 52 * df['Period ROI'] / df['Period Weeks']
        df['Weight'] = calculate_month_weight(df)
        df['Weighted ROI'] = df['Annual'] * df['Weight']
        df['TD group'] = td_group(df)
        df['Days Until Repayemnt Str'] = df['Days Until Repayemnt'].apply(lambda x: str(x).replace('.0', ''))

        if not values:
            print('No data found.')
            return
        
    except HttpError as err:
        print(err)
    return df


def read_repayments_data():
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1ViaHMRU1p79kdgVRRPvYts-RD7pFFkCKznlPPcRGz54'
    SAMPLE_RANGE_NAME = 'Repayments!A:AD'

    creds = None

    if os.path.exists('google_api_auth/token.json'):
        creds = Credentials.from_authorized_user_file('google_api_auth/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_api_auth/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google_api_auth/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        columns = values[0]

        df = pd.DataFrame(columns=columns)

        for i in range(1, len(values)):
            insert_row = dict(zip(columns, values[i]))
            df = pd.concat([df, pd.DataFrame(insert_row, index=[i-1])])

        numeric_columns = [
                           'Disb/Paym Value', 
                           'amount due', 
                           'Repaid', 
                           'repaid befor calc', 
                           'Gain', 
                           'Remaining Amount Due',
                           'Amount Repaid Late',
                           'Markup', 
                           'Rollover Fee',
                           '(Markup+Rollover Fee)'
                           ]
        
        for column in df:
            if column in numeric_columns:
                df[column] = df[column].apply(lambda x: 0 if x == '#N/A' else x)
                df[column] = df[column].apply(lambda x: 0 if x == '-' else x)
                df[column] = df[column].apply(lambda x: float(x.replace(',', '')) if x else None)
                
        if not values:
            print('No data found.')
            return
        
    except HttpError as err:
        print(err)
    return df


def read_delayed_collection():
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1ViaHMRU1p79kdgVRRPvYts-RD7pFFkCKznlPPcRGz54'
    SAMPLE_RANGE_NAME = 'delayed/collection!A:Q'

    creds = None

    if os.path.exists('google_api_auth/token.json'):
        creds = Credentials.from_authorized_user_file('google_api_auth/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_api_auth/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google_api_auth/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        columns = values[0]

        df = pd.DataFrame(columns=columns)

        for i in range(1, len(values)):
            insert_row = dict(zip(columns, values[i]))
            df = pd.concat([df, pd.DataFrame(insert_row, index=[i-1])])

        numeric_columns = [
                           'Disb/Paym Value', 
                           'Amount Due', 
                           'remaining due', 
                           'repaid befor calc', 
                           'total repaid (calc)', 
                           ]
        
        for column in df:
            if column in numeric_columns:
                df[column] = df[column].apply(lambda x: 0 if x == '#N/A' else x)
                df[column] = df[column].apply(lambda x: 0 if x == '-' else x)
                df[column] = df[column].apply(lambda x: float(x.replace(',', '')) if x else None)
                
        if not values:
            print('No data found.')
            return
        
    except HttpError as err:
        print(err)
    return df


def read_bad_clients_repayments():
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1ViaHMRU1p79kdgVRRPvYts-RD7pFFkCKznlPPcRGz54'
    SAMPLE_RANGE_NAME = ' bad client part-repayments!A:Q'

    creds = None

    if os.path.exists('google_api_auth/token.json'):
        creds = Credentials.from_authorized_user_file('google_api_auth/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_api_auth/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google_api_auth/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        columns = values[0]

        df = pd.DataFrame(columns=columns)

        for i in range(1, len(values)):
            insert_row = dict(zip(columns, values[i]))
            df = pd.concat([df, pd.DataFrame(insert_row, index=[i-1])])

        numeric_columns = [
                           'Repayment', 
                           'repayment (w/o full)', 
                           ]
        
        for column in df:
            if column in numeric_columns:
                df[column] = df[column].apply(lambda x: 0 if x == '#N/A' else x)
                df[column] = df[column].apply(lambda x: 0 if x == '-' else x)
                df[column] = df[column].apply(lambda x: float(x.replace(',', '')) if x else None)

        df['Date'] =  df['Date'].apply(lambda x: pd.Timestamp(x).to_pydatetime())

        if not values:
            print('No data found.')
            return
        
    except HttpError as err:
        print(err)
    return df