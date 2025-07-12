from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx
import os
from datetime import datetime
from database import get_db
from models.order import (
    OrderORM, OrderMerchantORM, OrderCustomerORM, OrderDeliveryORM,
    OrderItemORM, OrderItemOptionORM, OrderItemCustomizationORM,
    OrderPaymentORM, OrderAdditionalFeeORM
)
import json
from printing.zpl_utils import gerar_zpl_ifood
from printing.printnode_utils import imprimir_zpl_printnode
# from labelary_utils import gerar_pdf_labelary  # Se quiser PDF

router = APIRouter()

IFOOD_CLIENT_ID = os.getenv("IFOOD_CLIENT_ID")
IFOOD_CLIENT_SECRET = os.getenv("IFOOD_CLIENT_SECRET")
IFOOD_AUTH_URL = "https://merchant-api.ifood.com.br/authentication/v1.0/oauth/token"
IFOOD_ORDER_URL = "https://merchant-api.ifood.com.br/order/v1.0/orders/{}"

async def get_ifood_token():
    async with httpx.AsyncClient() as client:
        data = {
            "grantType": "client_credentials",
            "clientId": IFOOD_CLIENT_ID,
            "clientSecret": IFOOD_CLIENT_SECRET
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = await client.post(IFOOD_AUTH_URL, data=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Erro ao autenticar no iFood: {response.text}")
        return response.json()["accessToken"]

async def get_ifood_order(order_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(IFOOD_ORDER_URL.format(order_id), headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar detalhes do pedido no iFood: {response.text}")
        return response.json()

def parse_datetime(dt):
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except Exception:
        return None

def populate_order_from_payload(payload, full_code, db: Session):
    # Merchant
    merchant_data = payload.get("merchant", {})
    merchant = db.query(OrderMerchantORM).filter_by(merchant_id=merchant_data.get("id")).first()
    if not merchant:
        merchant = OrderMerchantORM(
            merchant_id=merchant_data.get("id"),
            name=merchant_data.get("name")
        )
        db.add(merchant)
        db.flush()

    # Customer
    customer_data = payload.get("customer", {})
    customer = db.query(OrderCustomerORM).filter_by(customer_id=customer_data.get("id")).first()
    if not customer:
        customer = OrderCustomerORM(
            customer_id=customer_data.get("id"),
            name=customer_data.get("name"),
            document_number=customer_data.get("documentNumber"),
            phone_number=customer_data.get("phone", {}).get("number"),
            phone_localizer=customer_data.get("phone", {}).get("localizer"),
            phone_localizer_expiration=parse_datetime(customer_data.get("phone", {}).get("localizerExpiration")),
            orders_count_on_merchant=customer_data.get("ordersCountOnMerchant"),
            segmentation=customer_data.get("segmentation")
        )
        db.add(customer)
        db.flush()

    # Delivery
    delivery_data = payload.get("delivery", {})
    address = delivery_data.get("deliveryAddress", {})
    delivery = OrderDeliveryORM(
        mode=delivery_data.get("mode"),
        description=delivery_data.get("description"),
        delivered_by=delivery_data.get("deliveredBy"),
        delivery_datetime=parse_datetime(delivery_data.get("deliveryDateTime")),
        observations=delivery_data.get("observations"),
        pickup_code=delivery_data.get("pickupCode"),
        address_street=address.get("streetName"),
        address_number=address.get("streetNumber"),
        address_formatted=address.get("formattedAddress"),
        address_neighborhood=address.get("neighborhood"),
        address_complement=address.get("complement"),
        address_postal_code=address.get("postalCode"),
        address_city=address.get("city"),
        address_state=address.get("state"),
        address_country=address.get("country"),
        address_reference=address.get("reference"),
        address_latitude=address.get("coordinates", {}).get("latitude"),
        address_longitude=address.get("coordinates", {}).get("longitude"),
    )
    db.add(delivery)
    db.flush()

    # Order
    total = payload.get("total", {})
    order = OrderORM(
        order_id=payload.get("id"),
        display_id=payload.get("displayId"),
        created_at=parse_datetime(payload.get("createdAt")),
        category=payload.get("category"),
        order_timing=payload.get("orderTiming"),
        order_type=payload.get("orderType"),
        preparation_start=parse_datetime(payload.get("preparationStartDateTime")),
        is_test=payload.get("isTest"),
        sales_channel=payload.get("salesChannel"),
        status=full_code,
        order_amount=total.get("orderAmount"),
        sub_total=total.get("subTotal"),
        delivery_fee=total.get("deliveryFee"),
        benefits=total.get("benefits"),
        additional_fees_total=total.get("additionalFees"),
        details=payload,
        merchant_id=merchant.id,
        customer_id=customer.id,
        delivery_id=delivery.id
    )
    db.add(order)
    db.flush()

    # Items
    for idx, item in enumerate(payload.get("items", [])):
        order_item = OrderItemORM(
            order_id=order.id,
            index=idx,
            item_id=item.get("id"),
            unique_id=item.get("uniqueId"),
            name=item.get("name"),
            external_code=item.get("externalCode"),
            ean=item.get("ean"),
            quantity=item.get("quantity"),
            unit=item.get("unit"),
            unit_price=item.get("unitPrice"),
            options_price=item.get("optionsPrice"),
            total_price=item.get("totalPrice"),
            price=item.get("price"),
            observations=item.get("observations"),
            image_url=item.get("imageUrl"),
            type=item.get("type")
        )
        db.add(order_item)
        db.flush()
        # Options
        for oidx, option in enumerate(item.get("options", [])):
            order_option = OrderItemOptionORM(
                item_id=order_item.id,
                index=oidx,
                option_id=option.get("id"),
                name=option.get("name"),
                type=option.get("type"),
                group_name=option.get("groupName"),
                external_code=option.get("externalCode"),
                ean=option.get("ean"),
                quantity=option.get("quantity"),
                unit=option.get("unit"),
                unit_price=option.get("unitPrice"),
                addition=option.get("addition"),
                price=option.get("price"),
                option_type=option.get("optionType")
            )
            db.add(order_option)
            db.flush()
            # Customizations
            for cidx, customization in enumerate(option.get("customizations", [])):
                order_customization = OrderItemCustomizationORM(
                    option_id=order_option.id,
                    customization_id=customization.get("id"),
                    external_code=customization.get("externalCode"),
                    name=customization.get("name"),
                    group_name=customization.get("groupName"),
                    type=customization.get("type"),
                    quantity=customization.get("quantity"),
                    unit_price=customization.get("unitPrice"),
                    addition=customization.get("addition"),
                    price=customization.get("price")
                )
                db.add(order_customization)
    # Payments
    for payment in payload.get("payments", []):
        if isinstance(payment, dict):
            order_payment = OrderPaymentORM(
                order_id=order.id,
                value=payment.get("value"),
                currency=payment.get("currency"),
                method=payment.get("method"),
                prepaid=payment.get("prepaid"),
                type=payment.get("type"),
                card_brand=payment.get("card", {}).get("brand")
            )
            db.add(order_payment)
        else:
            print("Pagamento ignorado (não é dict):", payment)

    # Additional Fees
    for fee in payload.get("additionalFees", []):
        order_fee = OrderAdditionalFeeORM(
            order_id=order.id,
            type=fee.get("type"),
            description=fee.get("description"),
            full_description=fee.get("fullDescription"),
            value=fee.get("value"),
            liabilities=fee.get("liabilities")
        )
        db.add(order_fee)
    db.commit()
    db.refresh(order)
    return order

@router.post("")
async def receive_ifood_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()

    # Checagem rápida de KEEPALIVE no corpo cru
    if b"KEEPALIVE" in raw_body:
        return JSONResponse(status_code=200, content={})

    try:
        # Tenta decodificar o corpo como JSON
        payload = json.loads(raw_body)
    except Exception as e:
        # Se não for JSON, retorna erro
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": f"Payload inválido: {str(e)}"}
        )

    full_code = payload.get("fullCode", "CONFIRMED")
    if full_code != "CONFIRMED":
        # Ignora qualquer evento que não seja CONFIRMED
        return JSONResponse(status_code=200, content={})

    order_id = payload.get("orderId") or payload.get("id")
    merchant_id = payload.get("merchantId") or (payload.get("merchant") or {}).get("id") or (
        payload.get("merchantIds")[0] if isinstance(payload.get("merchantIds"), list) and payload.get("merchantIds") else None
    )
    if not order_id or not merchant_id:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "orderId ou merchantId não encontrado no payload"}
        )

    try:
        token = await get_ifood_token()
        order_details = await get_ifood_order(order_id, token)
    except HTTPException as e:
        print(f"Erro ao buscar detalhes do pedido no iFood: {e.detail}")
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"Pedido não encontrado no iFood: {order_id}"}
        )
    order = populate_order_from_payload(order_details, full_code, db)

    # --- Gera ZPL e imprime ---
    zpl = gerar_zpl_ifood(order)
    try:
        await imprimir_zpl_printnode(zpl)
    except Exception as e:
        print(f"Erro ao imprimir etiqueta: {e}")

    # --- (Opcional) Gera PDF para visualização/armazenamento ---
    # pdf_bytes = await gerar_pdf_labelary(zpl)
    # with open(f"pedido_{order.order_id}.pdf", "wb") as f:
    #     f.write(pdf_bytes)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "order_db_id": order.id,
            "order_id": order.order_id
        }
    )
