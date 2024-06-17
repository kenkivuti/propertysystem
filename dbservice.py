import enum
from sqlalchemy import DateTime, Enum,  Numeric, create_engine,Column,Integer,String,ForeignKey,Float
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime 

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:kenkivuti254@localhost:5432/property system"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserRole(enum.Enum):
    TENANT = 'tenant'
    ADMIN = 'admin'
SUPERIORADMIN='superioadmin'



class User( Base ):
    __tablename__ = 'users'
    id = Column(Integer , primary_key = True)
    username= Column( String(100), nullable = False)
    contact = Column( String(15))
    email= Column( String(100),nullable = False)
    password= Column( String ,nullable=False) 
    role = Column(Enum(UserRole), nullable=False, default = UserRole.TENANT)


class House(Base):
    __tablename__ = 'houses'
    id = Column(Integer , primary_key = True)
    house_number = Column(String , nullable = False)
    no_of_rooms = Column(Integer , nullable = False)
    rent = Column(String)
    # relationship
    tenanthouse= relationship("TenantHouse" , back_populates = "house") 


class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(Integer , primary_key = True)
    full_name = Column(String(255))
    email= Column(String(255))
    phone = Column(String)
    tenanthouses= relationship("TenantHouse" , back_populates = "tenant")


class TenantHouse( Base ):
    __tablename__ = 'tenant_houses'
    id = Column( Integer , primary_key = True)
    tenant_id = Column( Integer , ForeignKey('tenants.id'))
    house_id = Column(Integer , ForeignKey('houses.id'))
    start_date = Column( DateTime )
    end_date = Column(String)
    tenant = relationship("Tenant" , back_populates = "tenanthouses")
    house= relationship("House" , back_populates ="tenanthouse")
    tenant_house= relationship("Tenanthousebill" , back_populates="tenant_houses")

   
class Tenanthousebill( Base ):
    __tablename__ = 'tenant_house_bills'
    id = Column( Integer , primary_key = True)
    tenant_house_id = Column( Integer, ForeignKey('tenant_houses.id'), nullable =False)
    billing_date = Column( String)
    due_date= Column( String)
    amount= Column( Numeric)
    payment_status = Column(String)
    tenant_houses = relationship("TenantHouse" , back_populates = "tenant_house")
    payment_date= Column(DateTime )
    payments = relationship("Payment" , back_populates = "tenantbill")


class Payment(Base):
    __tablename__ = 'payments'
    id = Column( Integer ,primary_key = True)
    tenant_house_bill_id = Column(Integer , ForeignKey('tenant_house_bills.id'), nullable =False)
    payment_method= Column( String(255))
    amount_paid = Column(Numeric)
    tenantbill= relationship("Tenanthousebill",back_populates= "payments")


Base.metadata.create_all(bind=engine)    