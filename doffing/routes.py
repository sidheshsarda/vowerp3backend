from fastapi import APIRouter, HTTPException, Depends, Query, Header, Depends
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from db.connection import get_db_connection


router = APIRouter()
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

def verify_auth_headers(Authorization: Optional[str] = Header(None), xtenantid: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    
    if not xtenantid:
        raise HTTPException(status_code=400, detail="Missing X_TENANT_IDhssdhsdhsd header")
    SECRET_KEY=ACCESS_TOKEN_SECRET
    token = Authorization.split(" ")[1]  # Extract the token
    algorithm="HS256"
    try:
        # Decode JWT (this would be more detailed validation in real use)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        return payload  # Return the decoded token payload, containing user info
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/po")
def get_purchase_orders():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM assets limit 20"
     
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/POsave")
def save_purchase_order(order_number: str, supplier: str, amount: float):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO purchase_orders (order_number, supplier, amount) VALUES (%s, %s, %s)"
        cursor.execute(query, (order_number, supplier, amount))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "success", "message": "Purchase order saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, HTTPException, Query, Header, Depends
from typing import Optional
from db.connection import get_db_connection

router = APIRouter()

@router.get("/fetchframeno-data")
async def get_frameno_data(
    auth: dict = Depends(verify_auth_headers),  # Authorization and tenant validation
    varfromdate: str = Query(...),
    company_id: int = Query(...),
    varmechine_id: int = Query(...),
    spell: str = Query(...),
    xtenantid: Optional[str] = Header(None)  # Expect X_TENANT_ID here
):
    print("Received X_TENANT_IDagagag:", xtenantid)

    if xtenantid is None:
        raise HTTPException(status_code=400, details="Missing X_TENANT_IDhdshsdhdss header")

    try:
        # Validate required parameters
        if not (varfromdate and company_id and varmechine_id and spell):
            raise HTTPException(status_code=400, detail="Missing required query parameters")
        
        # Optional: Format date
        formatted_date = varfromdate  # Format if necessary, e.g., using a utility function
        
        # Perform the database query
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT * FROM dofftable 
        WHERE doffdate = %s AND company_id =%s and spell = %s
        """
        print("Received paraX_TENANT_IDagagag:", query,varfromdate,company_id,spell,varmechine_id)   
        cursor.execute(query, (formatted_date,company_id, spell,))
        #cursor.execute(query, (company_id,spell))  
        data = cursor.fetchall()
        print("Received X_TENANT_IDagagag:", data)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/fetchframeno-data1")
async def get_framenos(
    varfromdate: str = Query(...),
    company_id: int = Query(...),
    varmechine_id: int = Query(...),
    spell: str = Query(...),
    authorization: Optional[str] = Header(None),
    xtenantid: Optional[str] = Header(None),
):
    # Log incoming query parameters and headers
    print("Received Query Parameters:")
    print(f"varfromdate: {varfromdate}")
    print(f"company_id: {company_id}")
    print(f"varmechine_id: {varmechine_id}")
    print(f"spell: {spell}")

    print("Received Headers:")
    print(f"X_TENANT_ID: {xtenantid}")
    print(f"Authorization: {authorization}")

    # Check for missing headers
    if xtenantid is None:
        raise HTTPException(status_code=400, detail="Missing X_TENANT_ID header")

    if not (varfromdate and company_id and varmechine_id and spell):
        raise HTTPException(status_code=400, detail="Missing required query parameters")

    return {"message": "All parameters received correctly"}


@router.get("/doffdetailrecords")
async def get_frameno_data(
    auth: dict = Depends(verify_auth_headers),  # Authorization and tenant validation
    varfromdate: str = Query(...),
    company_id: int = Query(...),
    spell: str = Query(...),
    xtenantid: Optional[str] = Header(None)  # Expect X_TENANT_ID here
):
    print("Received X_TENANT_IDagagag:", xtenantid)

    if xtenantid is None:
        raise HTTPException(status_code=400, details="Missing X_TENANT_IDhdshsdhdss header")

    try:
        # Validate required parameters
        if not (varfromdate and company_id  and spell):
            raise HTTPException(status_code=400, detail="Missing required query parameters")
        
        # Optional: Format date
        formatted_date = varfromdate  # Format if necessary, e.g., using a utility function
        
        # Perform the database query
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT auto_id, DATE_FORMAT(doffdate, '%d-%m-%Y') AS doffdate, spell, frameno, trollyno, grosswt, tarewt, netwt, entrytime,
        case when entry_mode='M' then 'bg-yellow'
        when entry_mode='W' then    'bg-green' end rowcolor 
        FROM dofftable d
        LEFT JOIN mechine_master mm ON mm.frame_no = d.frameno AND d.company_id = mm.company_id
        WHERE doffdate = %s AND d.company_id = %s AND spell = %s  AND is_active = 1 ORDER BY auto_id DESC
        """
        params = [];
        
        
        print("Received paraX_TENANT_IDagagag:", query,varfromdate,company_id,spell)   
        cursor.execute(query, (formatted_date,company_id, spell,))
        #cursor.execute(query, (company_id,spell))  
        data = cursor.fetchall()
        print("Received X_TENANT_IDagagag:", data)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/doffsummaryrecords")
async def get_frameno_data(
    auth: dict = Depends(verify_auth_headers),  # Authorization and tenant validation
    varfromdate: str = Query(...),
    company_id: int = Query(...),
    spell: str = Query(...),
    xtenantid: Optional[str] = Header(None)  # Expect X_TENANT_ID here
):
    print("Received X_TENANT_IDagagag:", xtenantid)

    if xtenantid is None:
        raise HTTPException(status_code=400, details="Missing X_TENANT_IDhdshsdhdss header")

    try:
        # Validate required parameters
        if not (varfromdate and company_id  and spell):
            raise HTTPException(status_code=400, detail="Missing required query parameters")
        
        # Optional: Format date
        formatted_date = varfromdate  # Format if necessary, e.g., using a utility function
        
        # Perform the database query
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT DATE_FORMAT(doffdate, '%d-%m-%Y') AS doffdate, spell, frameno,count(*) noofdoff,round(sum(netwt),2) netwt, 
        max(entrytime) entrytime
        FROM dofftable d
        WHERE doffdate = %s AND d.company_id = %s  AND spell = %s  AND is_active = 1 GROUP BY doffdate, spell, frameno 
        ORDER BY CAST(frameno AS UNSIGNED)
        """
        params = [];
        
        
        print("Received paraX_TENANT_IDagagag:", query,varfromdate,company_id,spell)   
        cursor.execute(query, (formatted_date,company_id, spell,))
        #cursor.execute(query, (company_id,spell))  
        data = cursor.fetchall()
        print("Received X_TENANT_IDagagag:", data)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
