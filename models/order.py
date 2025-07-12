from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class OrderORM(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    display_id = Column(String)
    created_at = Column(DateTime)
    category = Column(String)
    order_timing = Column(String)
    order_type = Column(String)
    preparation_start = Column(DateTime)
    is_test = Column(Boolean)
    sales_channel = Column(String)
    status = Column(String)  # fullCode do webhook
    order_amount = Column(Float)
    sub_total = Column(Float)
    delivery_fee = Column(Float)
    benefits = Column(Float)
    additional_fees_total = Column(Float)
    details = Column(JSONB)  # payload completo

    # Foreign keys
    merchant_id = Column(Integer, ForeignKey("order_merchants.id"))
    customer_id = Column(Integer, ForeignKey("order_customers.id"))
    delivery_id = Column(Integer, ForeignKey("order_deliveries.id"))

    # Relationships
    merchant = relationship("OrderMerchantORM", back_populates="orders")
    customer = relationship("OrderCustomerORM", back_populates="orders")
    delivery = relationship("OrderDeliveryORM", back_populates="orders")
    items = relationship("OrderItemORM", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("OrderPaymentORM", back_populates="order", cascade="all, delete-orphan")
    additional_fees = relationship("OrderAdditionalFeeORM", back_populates="order", cascade="all, delete-orphan")

class OrderMerchantORM(Base):
    __tablename__ = "order_merchants"
    id = Column(Integer, primary_key=True)
    merchant_id = Column(String, unique=True)
    name = Column(String)
    orders = relationship("OrderORM", back_populates="merchant")

class OrderCustomerORM(Base):
    __tablename__ = "order_customers"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, unique=True)
    name = Column(String)
    document_number = Column(String)
    phone_number = Column(String)
    phone_localizer = Column(String)
    phone_localizer_expiration = Column(DateTime)
    orders_count_on_merchant = Column(Integer)
    segmentation = Column(String)
    orders = relationship("OrderORM", back_populates="customer")

class OrderDeliveryORM(Base):
    __tablename__ = "order_deliveries"
    id = Column(Integer, primary_key=True)
    mode = Column(String)
    description = Column(String)
    delivered_by = Column(String)
    delivery_datetime = Column(DateTime)
    observations = Column(String)
    pickup_code = Column(String)
    address_street = Column(String)
    address_number = Column(String)
    address_formatted = Column(String)
    address_neighborhood = Column(String)
    address_complement = Column(String)
    address_postal_code = Column(String)
    address_city = Column(String)
    address_state = Column(String)
    address_country = Column(String)
    address_reference = Column(String)
    address_latitude = Column(Float)
    address_longitude = Column(Float)
    orders = relationship("OrderORM", back_populates="delivery")

class OrderItemORM(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    index = Column(Integer)
    item_id = Column(String)
    unique_id = Column(String)
    name = Column(String)
    external_code = Column(String)
    ean = Column(String)
    quantity = Column(Integer)
    unit = Column(String)
    unit_price = Column(Float)
    options_price = Column(Float)
    total_price = Column(Float)
    price = Column(Float)
    observations = Column(String)
    image_url = Column(String)
    type = Column(String)
    order = relationship("OrderORM", back_populates="items")
    options = relationship("OrderItemOptionORM", back_populates="item", cascade="all, delete-orphan")

class OrderItemOptionORM(Base):
    __tablename__ = "order_item_options"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("order_items.id"))
    index = Column(Integer)
    option_id = Column(String)
    name = Column(String)
    type = Column(String)
    group_name = Column(String)
    external_code = Column(String)
    ean = Column(String)
    quantity = Column(Integer)
    unit = Column(String)
    unit_price = Column(Float)
    addition = Column(Float)
    price = Column(Float)
    option_type = Column(String)
    item = relationship("OrderItemORM", back_populates="options")
    customizations = relationship("OrderItemCustomizationORM", back_populates="option", cascade="all, delete-orphan")

class OrderItemCustomizationORM(Base):
    __tablename__ = "order_item_customizations"
    id = Column(Integer, primary_key=True)
    option_id = Column(Integer, ForeignKey("order_item_options.id"))
    customization_id = Column(String)
    external_code = Column(String)
    name = Column(String)
    group_name = Column(String)
    type = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    addition = Column(Float)
    price = Column(Float)
    option = relationship("OrderItemOptionORM", back_populates="customizations")

class OrderPaymentORM(Base):
    __tablename__ = "order_payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    value = Column(Float)
    currency = Column(String)
    method = Column(String)
    prepaid = Column(Boolean)
    type = Column(String)
    card_brand = Column(String)
    order = relationship("OrderORM", back_populates="payments")

class OrderAdditionalFeeORM(Base):
    __tablename__ = "order_additional_fees"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    type = Column(String)
    description = Column(String)
    full_description = Column(String)
    value = Column(Float)
    liabilities = Column(JSONB)
    order = relationship("OrderORM", back_populates="additional_fees")