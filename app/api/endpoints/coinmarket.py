from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.api import dependencies
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

router = APIRouter()

@router.get("")
async def read_coinmarket_config(db: AsyncSession = Depends(dependencies.get_db)):
    db_coinmarket = await crud.coinmarket.get_coinmarket(db)
    if not db_coinmarket:
        db_coinmarket = {
            "coin_market_cap_api_key": "",
            "fetch_limit": 5000,
            "fetch_interval": 24,
            "metadata_interval": 1,
            "id": 0
        }
    return {
        "code": 0,
        "data": db_coinmarket,
        "message": "ok"
    }

@router.post("")
async def create_or_update_coinmarket_config(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    coinmarket_in: schemas.CoinMarketCapCreate,
):
    await crud.coinmarket.create_or_update_coinmarket(db=db, coinmarket=coinmarket_in)
    return {
        "code": 0,
        "data": None,
        "message": "Configuration saved successfully."
    }

@router.post("/verify")
async def verify_coinmarket_api_key(
    payload: dict = Body(...)
):
    api_key = payload.get("coin_market_cap_api_key")
    if not api_key:
        return {
            "code": -1,
            "data": None,
            "error": {},
            "message": "API key is required."
        }

    url = 'https://pro-api.coinmarketcap.com/v1/key/info'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url)
        r = response.json()
        if response.status_code == 200:
            return {
                "code": 0,
                "data": r,
                "message": "ok"
            }
        else:
            return {
                "code": 0,
                "data": r,
                "error": r.get("status", {}),
                "message": r.get("status", {}).get("error_message", "Unknown error")
            }
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return {
            "code": -1,
            "data": None,
            "error": {"error_message": str(e)},
            "message": "Failed to connect to CoinMarketCap API."
        }
    except json.JSONDecodeError:
        return {
            "code": -1,
            "data": None,
            "error": {"error_message": "Invalid JSON response from CoinMarketCap API."},
            "message": "Invalid JSON response from CoinMarketCap API."
        }