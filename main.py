from fastapi import FastAPI
from sqlalchemy import func
from dbservice import *
from pydanticmodel import *
from fastapi.middleware.cors import CORSMiddleware
from security import *



app = FastAPI()
db = SessionLocal()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8000"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.post("/register")
def addUser(user : UserCreate):
    password = pwd_context.hash(user.password)
    existinguser = db.query(User).filter(User.username == user.username).first()
    if not existinguser:
       new_user = User(username=user.username , email=user.email , contact=user.contact , password = password)
       db.add(new_user)
       db.commit()
       db.refresh(new_user)
       db.close()
    else:
         db.rollback()
         raise HTTPException(
            status_code=400, detail="Username already registered")
    
@app.get("/get_user" , response_model= list[UserResponse])
def get_user():
    existing_user = db.query(User).all()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return existing_user


@app.post("/registerTenant")
def addtenant(tenant : TenantCreate):
    existingtenant = db.query(Tenant).filter(Tenant.full_name == tenant.full_name).first()
    if not existingtenant:
       new_tenant = Tenant(full_name=tenant.full_name , email=tenant.email  , phone = tenant.phone)
       db.add(new_tenant)
       db.commit()
       db.refresh(new_tenant)
       db.close()
    else:
         db.rollback()
         raise HTTPException(
            status_code=400, detail="Username already registered")
    
@app.get('/get_tenant' , response_model = list[TenantResponse])
def get_tenant():
    existingtenant = db.query(Tenant).all()

    if existingtenant is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return existingtenant

@app.post('/user_login')
def login_user(form_data: UserLogin):

    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post('/houses')
def add_house(house: HouseCreate):
    existing_houses=db.query(House).filter(House.house_number == house.house_number).first()

    if not existing_houses:
        new_house= House(
            house_number = house.house_number,
            no_of_rooms=house.no_of_rooms,
            rent=house.rent
        )
        db.add(new_house)
        db.commit()
        db.refresh(new_house)
        db.close()

    else:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="House number already exists")
    
@app.get('/houses' , response_model=list[HouseResponse])
def get_houses():
    existinghouse=db.query(House).all()
    
    return existinghouse

@app.post('/tenant_house')
def create_tenant_house(tenant_house: TenantHousesCreate):
    existing_tenant_house=db.query(TenantHouse).filter(TenantHouse.house_id == tenant_house.house_id).first()

    if not existing_tenant_house:
        new_tenant_house= TenantHouse(
            tenant_id=tenant_house.tenant_id,
            house_id=tenant_house.house_id,
            # start_date=tenant_house.start_date,
            end_date = tenant_house.end_date
        )
        db.add(new_tenant_house)
        db.commit()
        db.refresh(new_tenant_house)
        db.close()

        
        return new_tenant_house 
        
    else:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="House occupied")
    
@app.get('/tenant_house' , response_model= list[TenantHouseResponse])
def get_tenant_house():
    existing_tenant_houses = db.query(TenantHouse).all()

    if existing_tenant_houses is None:
        raise HTTPException(status_code=404, detail="vacant")
    
    return existing_tenant_houses

@app.post('/tenant_house_bill')
def create_tenant_house_bill(tenant_house_bill: TenantHouseBillCreate):
    house_bill= Tenanthousebill(
        tenant_house_id=tenant_house_bill.tenant_house_id,
        billing_date= tenant_house_bill.billing_date,
        due_date=tenant_house_bill.due_date,
        payment_status=tenant_house_bill.payment_status,
        amount=tenant_house_bill.amount
    )
    db.add(house_bill)
    db.commit()
    db.refresh(house_bill)
    db.close()


@app.get('/tenant_house_bill' , response_model=list[TenantHouseBillResponse])
def get_tenant_house_bill():
    house_bills=db.query(Tenanthousebill).all()
    
    if house_bills is None:
        raise HTTPException(status_code=404, detail="null")
    
    return house_bills

@app.post('/payment')
def create_payment(payment:PaymentCreate):

    payments=Payment(
        tenant_house_bill_id=payment.tenant_house_bill_id,
        payment_method=payment.payment_method,
        amount_paid=payment.amount_paid
    )
    db.add(payments)
    db.commit()
    db.refresh(payments)

    return payments

@app.get('/payment' , response_model=list[PaymentResponse])
def get_payments():
    payments_made=db.query(Payment).all()

    
    if payments_made is None:
        raise HTTPException(status_code=404, detail="null")
    
    return payments_made

@app.get('/house/status/{house_id}')
def check_house_status(house_id : int, tenant_id : int):

    current_date = datetime.utcnow()

    house = db.query(House).filter(House.id == house_id).first()

    if house is None:
        raise HTTPException(status_code=404, detail="House not found")
    
    tenant_house = db.query(TenantHouse).filter(TenantHouse.house_id == house_id , TenantHouse.tenant_id == tenant_id , TenantHouse.end_date <= current_date).first()

    if tenant_house :
        
        house.status = HouseStatus.OCCUPIED

    else:
        house.status = HouseStatus.VACANT

    db.commit()
    db.refresh(house)

    return {"house_id" :house.id , "status" : house.status.value}
        

@app.get('/payment/status/{tenant_house_bill_id}')
def check_payment_status(tenant_house_bill_id : int):
    tenant_house_bill = db.query(Tenanthousebill).filter(Tenanthousebill.id == tenant_house_bill_id).first()

    if not tenant_house_bill:
         raise HTTPException(status_code=404, detail="tenant_house_bill not found")
        
    total_paid = db.query(func.sum(Payment.amount_paid)).filter(Payment.tenant_house_bill_id == tenant_house_bill_id).scalar() or 0

    if total_paid >= tenant_house_bill.amount:
        tenant_house_bill.payment_status = PaymentStatus.PAID
    
    else:
        tenant_house_bill.payment_status = PaymentStatus.PENDING


    db.commit()
    db.refresh(tenant_house_bill)

    return {'tenant_house_bill_id' : tenant_house_bill.id , "payment_status" : tenant_house_bill.payment_status.value}

@app.post("/apartmentbills/")
def create_apartment_bill(bill: ApartmentBillCreate):
    db_bill = Apartmentbill(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

@app.get("/apartmentbills/{bill_id}")
def read_apartment_bill(bill_id: int):
    db_bill = db.query(Apartmentbill).filter(Apartmentbill.id == bill_id).first()
    if db_bill is None:
        raise HTTPException(status_code=404, detail="ApartmentBill not found")
    db_bill.update_status()
    db.commit()
    db.refresh(db_bill)
    return db_bill

        
    
         


       
       
    


