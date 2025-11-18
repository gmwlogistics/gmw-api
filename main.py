from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gspread
from google.oauth2 import service_account
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
    packing_service: bool = False
    packing_materials: bool = False
    specialty_items_check: bool = False
    protection_plan: bool = False
    estimated_hours: int = 0
    payment_method: str | None = None
    estimated_cost: float = 0
    notes: str | None = None

class Load(BaseModel):
    id: str
    carrier: str
    pickup: str
    pickup_date: str
    delivery: str
    delivery_date: str
    status: str
    payment_date: str | None = None
    rate: float = 0
    distance: int = 0
    deadhead: int = 0
    weight: int = 0
    equipment: str
    cargo: str | None = None
    notes: str | None = None
    description: str | None = None
    bol: str | None = None
    pickup_longitude: float
    pickup_latitude: float
    delivery_longitude: float
    delivery_latitude: float
    pickup_checkin: str | None = None
    pickup_checkout: str | None = None
    delivery_checkin: str | None = None
    delivery_checkout: str | None = None

def get_sheet():
    try:
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        credentials_dict = json.loads(credentials_json)
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        client = gspread.service_account_from_dict(credentials_dict)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("bookings")
        return sheet
    except Exception as e:
        print(e)
        exit()

def get_load_sheet():
    try:
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        credentials_dict = json.loads(credentials_json)
        sheet_id = os.getenv("JT_LOAD_SHEET_ID")
        client = gspread.service_account_from_dict(credentials_dict)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("Sheet 1")
        return sheet
    except Exception as e:
        print(e)
        exit()



@app.post("/api/jt/load")
def create_load(load: Load):
    try:
        print('func start ----')
        sheet = get_load_sheet()
        print('sheet ----')
        row = [
            load.id,
            load.carrier,
            load.pickup,
            load.pickup_date,
            load.delivery,
            load.delivery_date,
            load.status,
            load.payment_date,
            load.rate,	
            load.distance,	
            load.deadhead,
            load.weight,
            load.equipment,	
            load.cargo,
            load.notes,	
            load.description,
            load.bol,	
            load.pickup_longitude,
            load.pickup_latitude,	
            load.delivery_longitude,	
            load.delivery_latitude,	
            load.pickup_checkin,
            load.pickup_checkout,
            load.delivery_checkin, 
            load.delivery_checkout
        ]
        print('row ----')
        print(row)
        sheet.append_row(row)
        print('append row ----')
        return {"status": "success", "load_id": load.id, "message": "Load saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bookings")
def create_booking(booking: Booking):
    try:
        sheet = get_sheet()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_id = str(uuid.uuid4())
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
            booking.packing_service or False,
            booking.packing_materials or False,
            booking.specialty_items_check or False,
            booking.protection_plan or False,
            booking.estimated_hours or 0,
            booking.payment_method or "",
            booking.estimated_cost or 0,
            booking.notes or "",
            timestamp,
            "Pending"
        ]
        sheet.append_row(row)
        return {"status": "success", "order_id": order_id, "message": "Booking saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "ok", "message": "THM Booking API is running successfully."}
