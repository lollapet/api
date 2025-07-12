import base64
import httpx
import os

PRINTNODE_API_KEY = os.getenv("PRINTNODE_API_KEY")
PRINTNODE_PRINTER_ID = int(os.getenv("PRINTNODE_PRINTER_ID", "0"))  # Defina no .env

async def imprimir_zpl_printnode(zpl: str, printer_id: int = None, api_key: str = None):
    if printer_id is None:
        printer_id = PRINTNODE_PRINTER_ID
    if api_key is None:
        api_key = PRINTNODE_API_KEY
    url = "https://api.printnode.com/printjobs"
    data = {
        "printerId": printer_id,
        "title": "Etiqueta iFood",
        "contentType": "raw_base64",
        "content": base64.b64encode(zpl.encode()).decode()
    }
    auth = (api_key, "")
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, auth=auth)
        if response.status_code != 201:
            raise Exception(f"Erro ao imprimir: {response.text}")
        return response.json()