from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from db.connection import get_db_connection

# Load environment variables
load_dotenv()

ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
USER_API = os.getenv("REACT_APP_USER_API")

# Initialize router
router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/authRoutes/login")

# In-memory storage for refresh tokens
refresh_tokens = []

# Helper function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Helper function to generate access token
def generate_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm="HS256")

# Helper function to generate refresh token
def generate_refresh_token(data: dict):
    return jwt.encode(data, REFRESH_TOKEN_SECRET, algorithm="HS256")

# Login request model
class LoginRequest(BaseModel):
    username: str
    password: str

  

USER_API=os.getenv("APP_USER_API")
# Login route
@router.post("/login")
async def login(request: LoginRequest):
    try:
        # Connect to the database and execute the query
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        query = f"SELECT * FROM {USER_API} WHERE user_login_id = %s"
        print(f"Executing query: {query}")
        cursor.execute(query, (request.username,))
        user = cursor.fetchone()

        # Log the query result
        print(f"Query result: {user}")

        # Check if the user exists
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Verify the password
        if not verify_password(request.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Generate tokens
        try:
            access_token = generate_access_token(
                {"id": user["user_id"], "username": user["user_login_id"]}
            )
            refresh_token = generate_refresh_token(
                {"id": user["user_id"], "username": user["user_login_id"]}
            )
        except Exception as token_error:
            print(f"Error generating tokens: {token_error}")
            raise HTTPException(status_code=500, detail="Token generation failed")

        # Add refresh token to storage
        refresh_tokens.append(refresh_token)

        # Return the tokens
        return {
            "success": True,
            "message": "Login successful",
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }

   
    except Exception as e:
        print(f"Unhandled exception: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    


# Refresh token route
@router.post("/refresh-token")
async def refresh_token(token: str):
    if token not in refresh_tokens:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=["HS256"])
        new_access_token = generate_access_token({"id": payload["id"], "username": payload["username"]})
        return {"accessToken": new_access_token}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# Protected route
@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
        return {"message": f"Welcome {payload['username']}!"}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
