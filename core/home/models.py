from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from enum import Enum
import datetime,json
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import uuid 

# Create your models here.
class DemandStatus(Enum):
    PROCUREMENT="in procurement"
    SELECTVENDOR="select vendor"
    VENDORALLOCATION="vendor allocation"
    QUOTEAPPROVAL="quote approval"

class Department(Enum):
    Engineering='engineering'
    Finance='finance'
    IT='it'
    Admin='admin'
    HR='hr'
    Sales='sales'
    Marketing='marketing'
    PROCUREMENT='procurement'

class Cities(Enum):
    USA="usa"
    DUBAI="dubai"
    MUMBAI="mumbai"
    DUBLIN="dublin"
    NOIDA="noida"


class Role(Enum):
    ADMIN="admin"
    USER="user"

class AssetsMaster(Enum):
    MOBILE="mobile"
    LAPTOP="laptop"
    SERVER="server"
    PRINTER="printer"
    WIRE="wire"
    SWITCH="switch"
    AIRPURIFIER="air purifier"
    OFR="oft"
    MONITOR="monitor"
    TV="tb"
    AIRCONDITIONER="air conditioner"
    CCTVCAMERA="cctv camera"
    FURNITURE="furniture"
    DOORACCESSMACHINE="door access machine"
    BIOMETRICMACHINE="biometric machine"
    RACKS="racks"
    PROJECTOR="projector"

class ProcurementStatus(Enum):
    PENDING="pending"
    READYFORQUOTE="ready for quote"
    REJECT="reject"
    QUOTED="quoted"

class RegisterUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=100,blank=False)
    email=models.EmailField(max_length=250,unique=True)
    department=models.CharField(
        max_length=11,
        choices=[(dep.value,dep.name) for dep in Department],
        blank=False
    )
    role=models.CharField(
        max_length=10,
        choices=[(role.value,role.name) for role in Role],
        blank=False,
        default="admin"
    )
    created_at=models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=['name','department']
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set', 
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    def to_json(self):
        return ({
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'role': self.role,
            'created_at': self.created_at.isoformat(),  # Convert datetime to string
        })
    

class Vendor(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50,blank=False)
    address=models.CharField(max_length=200,blank=False)
    city=models.CharField(max_length=40,blank=False)
    country=models.CharField(
        max_length=10,
        blank=False
    )
    GST=models.CharField(
        max_length=15,
        validators=[
            MinLengthValidator(15),
            MaxLengthValidator(15)
        ],
        blank=False
    )
    PAN=models.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10)
        ],
        blank=False
    )
    contactNumber=models.CharField(max_length=15)
    emailId=models.EmailField(max_length=100,unique=True)
    password = models.CharField(
        max_length=128,
        validators=[
            MinLengthValidator(8),
            MaxLengthValidator(128)
        ],
        blank=False
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

class Demand(models.Model):
    id=models.AutoField(primary_key=True),
    personId=models.CharField(max_length=100,blank=False)
    demandId=models.CharField(max_length=100,blank=False,primary_key=True)
    productId=models.CharField(         
        max_length=100,blank=False
    )
    assetType=models.CharField(
        max_length=19,
        choices=[(assets.value,assets.name) for assets in AssetsMaster],
        blank=False,
    )
    leased=models.CharField(max_length=3,choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
    default="no")
    subAsset=models.CharField(max_length=50,blank=True)
    location=models.CharField(
        max_length=11,
        choices=[(location.value,location.name) for location in Cities],
        blank=False
    )
    department=models.CharField(
        max_length=11,
        choices=[(dep.value,dep.name) for dep in Department],
        blank=False,
    )
    category=models.CharField(max_length=50,blank=False)
    description=models.CharField(max_length=100,blank=True)
    make=models.CharField(max_length=100,blank=True)
    model=models.CharField(max_length=20,blank=True)
    version=models.CharField(max_length=50,blank=True)
    quantity=models.CharField(max_length=5,blank=False)
    quantityPlaced=models.CharField(max_length=5,blank=False,default=0)
    partCode=models.CharField(max_length=10,blank=True)
    delivery=models.DateField(blank=False,default=timezone.now)
    leasedEndDate=models.DateField(blank=True,null=True)
    status=models.CharField(
        max_length=50,
        choices=[(stat.value, stat.name) for stat in DemandStatus],
        blank=False,
        default="in procurement"
    )
    created_at=models.DateField(default=timezone.now)
    updated_at=models.DateField(default=timezone.now)

class Procurement(models.Model):
    id=models.AutoField(primary_key=True)
    productId=models.ForeignKey(Demand,on_delete=models.CASCADE)
    demandId=models.ForeignKey(Demand,on_delete=models.CASCADE)
    vendorId=models.ForeignKey(Vendor,on_delete=models.CASCADE)
    quoteValidTill=models.DateField()
    status=models.CharField(
        max_length=25,
        choices=[(status.value,status.name) for status in ProcurementStatus],
        blank=False,
        default=ProcurementStatus.PENDING
    )
    quantity=models.CharField(max_length=100,blank=True)
    trackId=models.CharField(max_length=100,blank=True)
    rates=models.CharField(max_length=100,blank=True)
    tax=models.CharField(max_length=100,blank=True)
    customDuty=models.CharField(max_length=100,blank=True)
    others=models.CharField(max_length=100,blank=True)
    totalCost=models.CharField(max_length=100,blank=True)
    supplyTargetDate=models.DateField(blank=True)
    warranty=models.CharField(max_length=3,choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
    ])
    warrantyValidTill=models.DateField(blank=True)
    PONumber=models.CharField(max_length=100,blank=True)
    challanNumber=models.CharField(max_length=100,blank=True)
    invoiceNumber=models.CharField(max_length=100,blank=True)
    invoiceAmount=models.CharField(max_length=100,blank=True)
    lastDate=models.DateField(blank=True)


    


    


