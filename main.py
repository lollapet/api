from fastapi import FastAPI
from core.authentication import router as auth_router
from core.order import router as order_router
from marketplace.ifood import router as ifood_router
from marketplace.amazon import router as amazon_router
from marketplace.shopee import router as shopee_router

app = FastAPI()

app.include_router(auth_router, prefix="/users")
app.include_router(order_router, prefix="/orders")
app.include_router(ifood_router, prefix="/webhook/ifood")
app.include_router(amazon_router, prefix="/webhook/amazon")
app.include_router(shopee_router, prefix="/webhook/shopee")
