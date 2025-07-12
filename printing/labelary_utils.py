import httpx

async def gerar_pdf_labelary(zpl: str, width_mm=100, height_mm=150, dpi=8):
    url = f"https://api.labelary.com/v1/printers/{dpi}dpmm/labels/{width_mm}x{height_mm}/0/"
    headers = {"Accept": "application/pdf"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=zpl.encode(), headers=headers)
        if response.status_code == 200:
            return response.content  # PDF em bytes
        else:
            raise Exception(f"Erro ao gerar PDF: {response.text}")