from fastapi import APIRouter, HTTPException, Query, Header, Depends
from typing import Optional
from pydantic import BaseModel
from jose import JWTError, jwt
from db.connection import get_db_connection
from datetime import datetime
from datetime import date 
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router Initialization
router = APIRouter()
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Helper Functions
def validate_headers(authorization: Optional[str], xtenantid: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    if not xtenantid:
        raise HTTPException(status_code=400, detail="Missing X_TENANT_ID header")

def execute_query(query, params=None, commit=False):
    connection = None
    try:
        connection = get_db_connection()  # Ensure this function returns a valid connection
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())

        # Commit changes only if commit=True
        if commit:
            connection.commit()

        # Fetch data only for SELECT queries
        data = None
        if cursor.description:  # Check if the query returns rows
            data = cursor.fetchall()

        cursor.close()
        return data
    except Exception as e:
        if connection:
            connection.rollback()  # Rollback if something goes wrong
        logger.error(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            connection.close()  # Ensure connection is closed


def create_response(data=None, message="Success", status="success"):
    return { "data": data}

def create_response_msg(data=None, message="Success", status="success"):
    return {"status": status, "message": message, "data": data}


# Routes
@router.get("/po")
def get_purchase_orders():
    query = "SELECT * FROM mechine_master WHERE type_of_mechine=8 AND company_id=2 ORDER BY mech_code"
    logger.info(f"Executing Query: {query}")
    data = execute_query(query)
    return create_response(data)

@router.get("/spreadermcno")
def get_purchase_orders():
    query = "SELECT mechine_id,mech_code FROM mechine_master WHERE type_of_mechine=8 AND company_id=2 ORDER BY mech_code"
    logger.info(f"Executing Query: {query}")
    data = execute_query(query)
    return create_response(data)


@router.get("/rolls11")
async def get_frameno_data(
    spreader_no: str | None = Query(None, description="Filter rolls by spreader number")
):
    logger.info(f"Executing Queryss: {spreader_no}")
    query = """select roll_weight numbers from EMPMILL12.tbl_std_roll_range tsrr where mechine_id =%s order by roll_weight"""
    logger.info(f"Executing Query: {query}")
    data = execute_query(query, (spreader_no,))
      
    return create_response(data)


@router.get("/rolls")
async def get_frameno_data(
    spreader_no: Optional[str] = Query(None, description="Filter rolls by spreader number"), 
    entry_date: Optional[str] = Query(None, description="Entry date for filtering"),
    entry_spell: Optional[str] = Query(None, description="Entry spell for filtering")
):
    # Logging the received query parameters
    logger.info(f"Request parameters: spreader_no={spreader_no}, entryDate={entry_date}, entrySpell={entry_spell}")
    
    # Check if the required parameters are missing
    if not spreader_no or not entry_date or not entry_spell:
        raise HTTPException(status_code=422, detail="Missing one or more query parameters")
    
    # First query to get roll weight data based on spreader_no
    query1 = """SELECT roll_weight FROM EMPMILL12.tbl_std_roll_range tsrr WHERE mechine_id = %s ORDER BY roll_weight"""
    logger.info(f"Executing Query1: {query1} with spreader_no={spreader_no}")
    data1 = execute_query(query1, (spreader_no,))
    
    # Second query to get summary data (e.g., number of rolls, total weight, etc.)
    query2 = """
    SELECT mechine_id, COUNT(*) AS no_of_rolls, SUM(roll_weight) AS rollweight,
    ROUND(SUM(roll_weight)/COUNT(*), 0) AS avgwt
    FROM EMPMILL12.tbl_spreader_roll_weight
    WHERE mechine_id = %s AND spell = %s AND trans_date = %s
    """
    
    query2 = """select prd.*,std.std_roll_weight from 
        (select * from EMPMILL12.tbl_std_roll_range where mechine_id=%s  limit 1) std 
        left join
        (select mechine_id,count(*) no_of_rolls,sum(roll_weight) as rollweight,round(sum(roll_weight)/count(*),0) avgwt  from 
        EMPMILL12.tbl_spreader_roll_weight where mechine_id =%s and spell=%s and trans_date=%s and is_active=1
        ) prd on prd.mechine_id=std.mechine_id """
    
    
    logger.info(f"Executing Query2: {query2} with spreader_no={spreader_no}, entrySpell={entry_spell}, entryDate={entry_date}")
    data2 = execute_query(query2, (spreader_no,spreader_no, entry_spell, entry_date))
    
    # Return the results
    return {
        "data": {
            "rolls": data1,   # Roll weight data
            "summary": data2  # Summary data (rolls count, total weight, etc.)
        }
    }

@router.get("/summaryreport")
async def get_frameno_data(
    
    entry_date: Optional[str] = Query(None, description="Entry date for filtering"),
    entry_spell: Optional[str] = Query(None, description="Entry spell for filtering")
):
    # Logging the received query parameters
    logger.info(f"Request parameters:  entryDate={entry_date}, entrySpell={entry_spell}")
    
    # Check if the required parameters are missing
    if not  entry_date or not entry_spell:
        raise HTTPException(status_code=422, detail="Missing one or more query parameters")
    
    # First query to get roll weight data based on spreader_no
   
    # Second query to get summary data (e.g., number of rolls, total weight, etc.)
    entryspell = entry_spell.strip()
    
    query2 = """SELECT 
    prd.*, 
    std.std_roll_weight, 
    mm.mech_code, 
    mm.mechine_name, 
    rng.less_than_90pc, 
    rng.between9095pc, 
    rng.between95100pc, 
    rng.equal_to_std, 
    rng.between_100_105pc, 
    rng.between_105_110pc, 
    rng.more_than_110pc,    %s AS entry_date, 
    %s AS entry_spell
    FROM 
    -- Standard roll weight data
    (SELECT DISTINCT mechine_id, std_roll_weight   
     FROM EMPMILL12.tbl_std_roll_range) std
    LEFT JOIN
    -- Roll weight details by machine
    (SELECT 
        mechine_id,
        COUNT(*) AS no_of_rolls,
        SUM(roll_weight) AS rollweight,
        ROUND(SUM(roll_weight) / COUNT(*), 0) AS avgwt  
     FROM EMPMILL12.tbl_spreader_roll_weight 
     WHERE spell = %s 
       AND trans_date = %s
       AND is_active = 1 
     GROUP BY mechine_id) prd 
    ON prd.mechine_id = std.mechine_id
    LEFT JOIN 
    -- Machine master details
    mechine_master mm 
ON mm.mechine_id = std.mechine_id
LEFT JOIN 
    -- Roll weight comparison
    (SELECT 
        tsrw.mechine_id,
        SUM(CASE WHEN roll_weight < ROUND(std_roll_weight * 0.9, 0) THEN 1 ELSE 0 END) AS less_than_90pc,
        SUM(CASE WHEN roll_weight >= ROUND(std_roll_weight * 0.9, 0) 
                     AND roll_weight < ROUND(std_roll_weight * 0.95, 0) THEN 1 ELSE 0 END) AS between9095pc,
        SUM(CASE WHEN roll_weight >= ROUND(std_roll_weight * 0.95, 0) 
                     AND roll_weight < ROUND(std_roll_weight * 1.0, 0) THEN 1 ELSE 0 END) AS between95100pc,
        SUM(CASE WHEN roll_weight = std_roll_weight THEN 1 ELSE 0 END) AS equal_to_std,
        SUM(CASE WHEN roll_weight >= ROUND(std_roll_weight * 1.0, 0) 
                     AND roll_weight < ROUND(std_roll_weight * 1.05, 0) THEN 1 ELSE 0 END) AS between_100_105pc,
        SUM(CASE WHEN roll_weight >= ROUND(std_roll_weight * 1.05, 0) 
                     AND roll_weight < ROUND(std_roll_weight * 1.10, 0) THEN 1 ELSE 0 END) AS between_105_110pc,
        SUM(CASE WHEN roll_weight >= ROUND(std_roll_weight * 1.10, 0) THEN 1 ELSE 0 END) AS more_than_110pc
     FROM EMPMILL12.tbl_spreader_roll_weight tsrw
     LEFT JOIN 
         (SELECT DISTINCT mechine_id, std_roll_weight
          FROM EMPMILL12.tbl_std_roll_range) std 
     ON std.mechine_id = tsrw.mechine_id
     WHERE trans_date = %s
       AND spell =%s and is_active=1
     GROUP BY tsrw.mechine_id) rng 
    ON std.mechine_id = rng.mechine_id
    """
 
# Log the SQL query for debugging
    logger.info(f"Executing Query2 with entrySpell={entry_spell}, entryDate={entry_date}")

# Execute the query with proper parameters
    data2 = execute_query(query2, (entry_date, entry_spell, entry_spell, entry_date, entry_date, entry_spell))
 
    
    logger.info(f"Executing Query2: {query2} with  entrySpell={entry_spell}, entryDate={entry_date},query={query2} ")
    data2 = execute_query(query2, ( entry_date,entryspell,entryspell, entry_date,entry_date,entryspell))
    
    # Return the results
    return {
        "data": {
             # Roll weight data
            "summary": data2  # Summary data (rolls count, total weight, etc.)
        }
    }


@router.get("/detailreport")
async def get_frameno_data(
    spreader_no: Optional[str] = Query(None, description="Spreader for filtering"),
    entry_date: Optional[str] = Query(None, description="Entry date for filtering"),
    entry_spell: Optional[str] = Query(None, description="Entry spell for filtering")
):
    # Logging the received query parameters
    logger.info(f"Request parameters:  entryDate={entry_date}, entrySpell={entry_spell}")
    
    # Check if the required parameters are missing
    if not  entry_date or not entry_spell:
        raise HTTPException(status_code=422, detail="Missing one or more query parameters")
    
    # First query to get roll weight data based on spreader_no
   
    # Second query to get summary data (e.g., number of rolls, total weight, etc.)
    entryspell = entry_spell.strip()
    
    query2 = """SELECT
    tsrw.mechine_id,
    mech_code,
    %s AS entry_date, 
    %s AS entry_spell,
    tsrw.roll_weight,
    std.std_roll_weight AS td,
    CASE 
        WHEN tsrw.roll_weight < ROUND(std.std_roll_weight * 0.9, 0) THEN '#faafc9'
        WHEN tsrw.roll_weight >= ROUND(std.std_roll_weight * 0.9, 0) 
             AND tsrw.roll_weight < ROUND(std.std_roll_weight * 0.95, 0) THEN '#f9d1df'
        WHEN tsrw.roll_weight >= ROUND(std.std_roll_weight * 0.95, 0) 
             AND tsrw.roll_weight < ROUND(std.std_roll_weight * 1, 0) THEN '#fce9f0'
        WHEN roll_weight = std_roll_weight THEN '#e0fad8'     
        WHEN tsrw.roll_weight >= ROUND(std.std_roll_weight * 1, 0) 
             AND tsrw.roll_weight <= ROUND(std.std_roll_weight * 1.05, 0) THEN '#d2f9c5'
        WHEN tsrw.roll_weight >= ROUND(std.std_roll_weight * 1.05, 0) 
             AND tsrw.roll_weight <= ROUND(std.std_roll_weight * 1.10, 0) THEN '#c5f9b4'
        WHEN roll_weight >= ROUND(std_roll_weight * 1.10, 0) THEN  '#a6fa8b'   
        ELSE 'other' END AS colorsg
FROM 
    EMPMILL12.tbl_spreader_roll_weight tsrw
LEFT JOIN
    (SELECT DISTINCT mechine_id, std_roll_weight
     FROM EMPMILL12.tbl_std_roll_range 
     WHERE mechine_id = %s) std 
ON std.mechine_id = tsrw.mechine_id
left join mechine_master mm on mm.mechine_id=tsrw.mechine_id
WHERE 
    tsrw.spell = %s
    AND tsrw.trans_date = %s
    AND tsrw.is_active = 1
    AND tsrw.mechine_id = %s;
    """
 
# Log the SQL query for debugging
    logger.info(f"Executing Query2 with entrySpell={entry_spell}, entryDate={entry_date}")

# Execute the query with proper parameters
     
    
    logger.info(f"Executing Query2: {query2} with  entrySpell={entry_spell}, entryDate={entry_date},query={query2} ")
    data2 = execute_query(query2, ( entry_date,entryspell,spreader_no,entryspell, entry_date,spreader_no))
    
    # Return the results
    return {
        "data": {
             # Roll weight data
            "detail": data2  # Summary data (rolls count, total weight, etc.)
        }
    }





class WeightEntry(BaseModel):
    number: str
    weight: float
    date: date
    spell: str
    spreaderNo: str


@router.post("/saveentry")
async def save_weight_entry(entry: WeightEntry):
    # Access data from the entry object
    number = entry.number
    weight = entry.weight
    date = entry.date
    spell = entry.spell
    spreaderNo = entry.spreaderNo

    logger.info(f"Received entry: {entry.dict()}")

    # Validate inputs
    if not all([number, weight, date, spell, spreaderNo]):
        logger.error("Invalid input parameters.")
        raise HTTPException(status_code=400, detail="Invalid input parameters.")

    # Insert Query
    query = """
        INSERT INTO EMPMILL12.tbl_spreader_roll_weight (trans_date, spell, mechine_id, roll_weight)
        VALUES (%s, %s, %s, %s)
    """
    try:
        logger.info(f"Executing Query: {query} with params: {date}, {spell}, {spreaderNo}, {weight}")
        execute_query(query, (date, spell, spreaderNo, weight), commit=True)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to save weight entry.")

    # Return a success response
    return {"message": "Weight entry saved successfully"}

@router.post("/POsave")
def save_purchase_order(order_number: str, supplier: str, amount: float):
    query = "INSERT INTO purchase_orders (order_number, supplier, amount) VALUES (%s, %s, %s)"
    execute_query(query, (order_number, supplier, amount))
    return create_response(message="Purchase order saved.")

@router.get("/fetchframeno-data")
async def get_frameno_data(
    varfromdate: str = Query(...),
    company_id: int = Query(...),
    varmechine_id: int = Query(...),
    spell: str = Query(...),
    authorization: Optional[str] = Header(None),
    xtenantid: Optional[str] = Header(None),
):
    validate_headers(authorization, xtenantid)
    logger.info(f"Received Headers: authorization={authorization}, xtenantid={xtenantid}")
    query = """
        SELECT * FROM dofftable 
        WHERE doffdate = %s AND company_id = %s AND spell = %s
    """
    formatted_date = varfromdate  # Modify if required
    data = execute_query(query, (formatted_date, company_id, spell))
    return create_response(data)
