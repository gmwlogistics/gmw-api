from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gspread
from google.oauth2.service_account import Credentials
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
        print("get_sheet")
        creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
        print("creds_dict")
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets"]
        )
        print("creds")
        client = gspread.authorize(creds)
        print("client")
        print(client)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load service account credentials: {e}")
    try:
        print(os.getenv("GOOGLE_SHEET_ID"))
        spreadsheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
        print('spreadshit')
        print(spreadsheet)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load spreadsheet: {e}")
    try:
        worksheet = spreadsheet.worksheet("bookings")
        print('shit')
        print(worksheet)
        print("sheet")
        return worksheet
    except Exception as e:
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
