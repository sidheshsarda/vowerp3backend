from fastapi import APIRouter, HTTPException
from db.connection import get_db_connection

router = APIRouter()

@router.get("/combobox-frameno")

def get_framenos():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT mechine_id, frame_no
        FROM mechine_master mm
        WHERE type_of_mechine = 36 AND company_id = 2
        ORDER BY CAST(frame_no AS UNSIGNED)"""
     
        cursor.execute(query)
        data = cursor.fetchall()
    
        return { "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


     

@router.get("/spool-quality-name")

def get_spoolquatity():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = """SELECT wnd_quality_id,wnd_q_code,quality,CONCAT(wnd_q_code, '-', quality, '') AS name 
        FROM EMPMILL12.WINDING_QUALITY_MASTER wqm WHERE company_id =2 ORDER BY wnd_q_code,quality"""
     
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return { "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/po")

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
