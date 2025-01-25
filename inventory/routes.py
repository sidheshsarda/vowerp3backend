from fastapi import APIRouter, HTTPException
from db.connection import get_db_connection

router = APIRouter()

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
