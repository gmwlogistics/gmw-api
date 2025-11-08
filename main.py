from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gspread
# from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os
import json
import uuid

app = FastAPI(title="THM Booking API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Canva domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Booking(BaseModel):
    customer_name: str
    email: str
    phone: str
    move_date: str
    move_time: str
    move_type: str
    origin_address: str
    destination_address: str
    home_size: str | None = None
    special_items: str | None = None
    packing_service: str | None = None
    packing_materials: str | None = None
    specialty_items_check: str | None = None
    protection_plan: str | None = None
    estimated_hours: str | None = None
    payment_method: str | None = None
    estimated_cost: str | None = None
    notes: str | None = None

def get_sheet():
    try:
        scopes = [ "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        credentials_dict = json.loads(credentials_json)
        print('credentials_json')
        print(credentials_json)
        print('credentials_dict')
        print(credentials_dict)

        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        print('sheet_id')
        print(sheet_id)

        creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        print('creds')
        print(type(creds))

        credss = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scopes)

        client = gspread.authorize(credss)
        print('client')
        print(type(client))

        spreadsheets = client.list_spreadsheet_files() 
        print('spreadsheets')
        print(spreadsheets)

        spreadsheet = client.open_by_key(sheet_id)
        print('spreadsheet')
        print(spreadsheet)
        
        
    except Exception as e:
        print(f"An unexpected error occurred during client creation: {e}")
        exit()

def get_sheets():
    try:
        credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
        print('creds')

        # Authenticate using the dictionary
        gc = gspread.service_account_from_dict(credentials_dict)
        print('gc')

        spreadsheets = gc.list_spreadsheet_files() 
        print(f"Successfully connected to Google API. Found {len(spreadsheets)} files.")
    except gspread.APIError as e:
        print(f"API Error during authentication or connection check: {e}")
        # You might want to print parts of the credentials_dict for debugging (be careful with sensitive keys)
        exit()
    except Exception as e:
        print(f"An unexpected error occurred during client creation: {e}")
        exit()

    try:
        # 2. Open the spreadsheet using its file ID
        spreadsheet_file_id = os.getenv("GOOGLE_SHEET_ID")
        sh = gc.open_by_key(spreadsheet_file_id)
        print('sh')
        print(f"Successfully opened spreadsheet: {sh.title}")

        # Select a worksheet
        worksheet = sh.get_worksheet(0)
        print('worksheet')

        return worksheet
    except Exception as e:
        raise RuntimeError(f"❌ Failed to get gspread: {e}")
    except gspread.SpreadsheetNotFound:
        print(f"Error: Spreadsheet with ID '{spreadsheet_file_id}' not found.")
    except gspread.APIError as e:
        print(f"Error when opening spreadsheet: {e}")

    # try:
    #     print("get_sheet")
    #     creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
    #     print("creds_dict")
    #     creds = Credentials.from_service_account_info(
    #         creds_dict,
    #         scopes=[
    #             "https://www.googleapis.com/auth/spreadsheets",
    #             "https://www.googleapis.com/auth/drive"
    #         ]
    #     )
    #     print("creds")
    #     client = gspread.authorize(creds)
    #     print("client")
    #     print(client)
    # except Exception as e:
    #     raise RuntimeError(f"❌ Failed to load service account credentials: {e}")
    # try:
    #     print(os.getenv("GOOGLE_SHEET_ID"))
    #     spreadsheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    #     print('spreadshit')
    #     print(spreadsheet)
    # except Exception as e:
    #     raise RuntimeError(f"❌ Failed to load spreadsheet: {e}")
    # try:
    #     worksheet = spreadsheet.worksheet("bookings")
    #     print('shit')
    #     print(worksheet)
    #     print("sheet")
    #     return worksheet
    # except Exception as e:
        raise RuntimeError(f"❌ Failed to sheet: {e}")
    
@app.post("/api/bookings")
def create_booking(booking: Booking):
    try:
        print('bookings information')
        print(booking)

        sheet = get_sheet()
        print('got sheet')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('got timestamp')
        order_id = str(uuid.uuid4())
        print('got order-id')
        row = [
            order_id,
            booking.customer_name,
            booking.email,
            booking.phone,
            booking.move_date,
            booking.move_time,
            booking.move_type,
            booking.origin_address,
            booking.destination_address,
            booking.home_size or "",
            booking.special_items or "",
            booking.packing_service or "",
            booking.packing_materials or "",
            booking.specialty_items_check or "",
            booking.protection_plan or "",
            booking.estimated_hours or "",
            booking.payment_method or "",
            booking.estimated_cost or "",
            booking.notes or "",
            timestamp,
            "Pending"
        ]
        row1 = [
            "order_id",
            "booking.customer_name",
            "booking.email",
            "booking.phone",
            "booking.move_date",
            "booking.move_time",
            "booking.move_type",
            "booking.origin_address",
            "booking.destination_address",
            "booking.home_size",
            "booking.special_items",
            "booking.packing_service",
            "booking.packing_materials",
            "booking.specialty_items_check",
            "booking.protection_plan",
            "booking.estimated_hours",
            "booking.payment_method",
            "booking.estimated_cost",
            "booking.notes",
            "timestamp",
            "Pending"
        ]
        print ('rows are ready')
        sheet.append_row(row1)
        return {"status": "success", "order_id": order_id, "message": "Booking saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "ok", "message": "THM Booking API is running successfully."}
