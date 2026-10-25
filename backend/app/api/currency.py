from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.services.currency_service import currency_service

router = APIRouter(prefix="/currency", tags=["Currency Exchange & Conversion"])

class CurrencyConvertRequest(BaseModel):
    amount: float = Field(..., gt=0)
    from_currency: Optional[str] = None
    to_currency: Optional[str] = None
    from_: Optional[str] = Field(None, alias="from")
    to_: Optional[str] = Field(None, alias="to")

    @field_validator("from_currency", "to_currency", "from_", "to_", mode="before")
    @classmethod
    def normalise_code(cls, value: Optional[str]) -> Optional[str]:
        return value.upper().strip() if isinstance(value, str) else value


def _currency_error(error: ValueError) -> HTTPException:
    return HTTPException(status_code=422, detail=str(error))

@router.get("/rates")
def get_all_exchange_rates(
    base: Optional[str] = Query(None, alias="base"),
    base_currency: Optional[str] = Query(None, alias="base_currency")
):
    target_base = base or base_currency or "USD"
    return currency_service.get_all_rates(target_base)

@router.get("/rate")
def get_exchange_rate(
    from_currency: Optional[str] = None,
    from_alias: Optional[str] = Query(None, alias="from"),
    to_currency: Optional[str] = None,
    to_alias: Optional[str] = Query(None, alias="to")
):
    from_c = from_currency or from_alias or "USD"
    to_c = to_currency or to_alias or "VND"
    try:
        details = currency_service.get_rate_details(from_c, to_c)
    except ValueError as error:
        raise _currency_error(error) from error
    return {
        "from": from_c.upper(),
        "to": to_c.upper(),
        "from_currency": from_c.upper(),
        "to_currency": to_c.upper(),
        "rate": details["rate"],
        "source": details["source"],
        "last_updated": details["last_updated"],
    }

@router.get("/convert")
def convert_currency_get(
    amount: float = Query(1.0, gt=0),
    from_currency: Optional[str] = None,
    from_alias: Optional[str] = Query(None, alias="from"),
    to_currency: Optional[str] = None,
    to_alias: Optional[str] = Query(None, alias="to")
):
    from_c = from_currency or from_alias or "EUR"
    to_c = to_currency or to_alias or "VND"
    try:
        return currency_service.convert(amount, from_c, to_c)
    except ValueError as error:
        raise _currency_error(error) from error

@router.post("/convert")
def convert_currency_post(req: CurrencyConvertRequest):
    from_c = req.from_currency or req.from_ or "EUR"
    to_c = req.to_currency or req.to_ or "VND"
    try:
        return currency_service.convert(req.amount, from_c, to_c)
    except ValueError as error:
        raise _currency_error(error) from error

@router.get("/supported")
def get_supported_currencies():
    return currency_service.get_supported_currencies()
