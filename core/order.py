from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.authentication import get_current_user  # Adicione esta linha
from models.order import (
    OrderORM, OrderMerchantORM, OrderCustomerORM, OrderDeliveryORM,
    OrderItemORM, OrderItemOptionORM, OrderItemCustomizationORM,
    OrderPaymentORM, OrderAdditionalFeeORM
)

router = APIRouter()

@router.get("/{order_id}")
def get_order_by_id(
    order_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)  # Protege o endpoint com autenticação
):
    order = db.query(OrderORM).filter_by(order_id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    merchant = db.query(OrderMerchantORM).filter_by(id=order.merchant_id).first()
    customer = db.query(OrderCustomerORM).filter_by(id=order.customer_id).first()
    delivery = db.query(OrderDeliveryORM).filter_by(id=order.delivery_id).first()
    items = db.query(OrderItemORM).filter_by(order_id=order.id).all()
    payments = db.query(OrderPaymentORM).filter_by(order_id=order.id).all()
    additional_fees = db.query(OrderAdditionalFeeORM).filter_by(order_id=order.id).all()

    items_payload = []
    for item in items:
        options = db.query(OrderItemOptionORM).filter_by(item_id=item.id).all()
        options_payload = []
        for option in options:
            customizations = db.query(OrderItemCustomizationORM).filter_by(option_id=option.id).all()
            options_payload.append({
                "id": option.option_id,
                "name": option.name,
                "type": option.type,
                "groupName": option.group_name,
                "externalCode": option.external_code,
                "ean": option.ean,
                "quantity": option.quantity,
                "unit": option.unit,
                "unitPrice": option.unit_price,
                "addition": option.addition,
                "price": option.price,
                "optionType": option.option_type,
                "customizations": [
                    {
                        "id": c.customization_id,
                        "externalCode": c.external_code,
                        "name": c.name,
                        "groupName": c.group_name,
                        "type": c.type,
                        "quantity": c.quantity,
                        "unitPrice": c.unit_price,
                        "addition": c.addition,
                        "price": c.price
                    }
                    for c in customizations
                ]
            })
        items_payload.append({
            "id": item.item_id,
            "uniqueId": item.unique_id,
            "name": item.name,
            "externalCode": item.external_code,
            "ean": item.ean,
            "quantity": item.quantity,
            "unit": item.unit,
            "unitPrice": item.unit_price,
            "optionsPrice": item.options_price,
            "totalPrice": item.total_price,
            "price": item.price,
            "observations": item.observations,
            "imageUrl": item.image_url,
            "type": item.type,
            "options": options_payload
        })

    payload = {
        "id": order.order_id,
        "displayId": order.display_id,
        "createdAt": order.created_at.isoformat() if order.created_at else None,
        "category": order.category,
        "orderTiming": order.order_timing,
        "orderType": order.order_type,
        "preparationStartDateTime": order.preparation_start.isoformat() if order.preparation_start else None,
        "isTest": order.is_test,
        "salesChannel": order.sales_channel,
        "fullCode": order.status,
        "merchant": {
            "id": merchant.merchant_id,
            "name": merchant.name
        } if merchant else {},
        "customer": {
            "id": customer.customer_id,
            "name": customer.name,
            "documentNumber": customer.document_number,
            "phone": {
                "number": customer.phone_number,
                "localizer": customer.phone_localizer,
                "localizerExpiration": customer.phone_localizer_expiration.isoformat() if customer.phone_localizer_expiration else None
            },
            "ordersCountOnMerchant": customer.orders_count_on_merchant,
            "segmentation": customer.segmentation
        } if customer else {},
        "delivery": {
            "mode": delivery.mode,
            "description": delivery.description,
            "deliveredBy": delivery.delivered_by,
            "deliveryDateTime": delivery.delivery_datetime.isoformat() if delivery.delivery_datetime else None,
            "observations": delivery.observations,
            "pickupCode": delivery.pickup_code,
            "deliveryAddress": {
                "streetName": delivery.address_street,
                "streetNumber": delivery.address_number,
                "formattedAddress": delivery.address_formatted,
                "neighborhood": delivery.address_neighborhood,
                "complement": delivery.address_complement,
                "postalCode": delivery.address_postal_code,
                "city": delivery.address_city,
                "state": delivery.address_state,
                "country": delivery.address_country,
                "reference": delivery.address_reference,
                "coordinates": {
                    "latitude": delivery.address_latitude,
                    "longitude": delivery.address_longitude
                }
            }
        } if delivery else {},
        "items": items_payload,
        "payments": [
            {
                "value": p.value,
                "currency": p.currency,
                "method": p.method,
                "prepaid": p.prepaid,
                "type": p.type,
                "card": {"brand": p.card_brand} if p.card_brand else None
            }
            for p in payments
        ],
        "additionalFees": [
            {
                "type": f.type,
                "description": f.description,
                "fullDescription": f.full_description,
                "value": f.value,
                "liabilities": f.liabilities
            }
            for f in additional_fees
        ],
        "total": {
            "orderAmount": order.order_amount,
            "subTotal": order.sub_total,
            "deliveryFee": order.delivery_fee,
            "benefits": order.benefits,
            "additionalFees": order.additional_fees_total
        },
        "details": order.details
    }

    return payload
