from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/")
async def receive_shopee_webhook(request: Request):
    payload = await request.json()
    # Processa o pedido da Shopee
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Evento da Shopee recebido"}
    )
