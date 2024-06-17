from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username : str
    email : str
    contact :str
    password : str


class UserResponse(UserCreate):
    id : int 
    class Config:
       from_attributes = True

class UserLogin (BaseModel):
    email : str
    password :str

class PaymentCreate(BaseModel):
    tenant_house_bill_id : str
    payment_method :  str 
    amount_paid : float

class PaymentResponse(PaymentCreate):
    id : int

class TenantCreate(BaseModel):
    full_name : str
    email : str
    phone : str

class TenantResponse(TenantCreate):
    id : int 

class HouseCreate(BaseModel):
    house_number : int
    no_of_rooms : int
    rent : float

class HouseResponse(HouseCreate):
    id : int

class  TenantHousesCreate(BaseModel):
    tenant_id : int
    house_id : int
    start_date : datetime
    end_date : str 

class TenantHouseResponse(TenantHousesCreate):
    id : int

class TenantHouseBillCreate(BaseModel):
    tenant_house_id : int
    billing_date : str
    due_date : str
    payment_status : str
    payment_date : datetime

class TenantHouseBillResponse(TenantHouseBillCreate):
    id : str
