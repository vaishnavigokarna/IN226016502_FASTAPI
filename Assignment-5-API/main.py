from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

# -------------------------
# DATA
# -------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

orders = []
order_counter = 1


# -------------------------
# MODELS
# -------------------------

class OrderRequest(BaseModel):
    customer_name: str
    product_id: int
    quantity: int
    delivery_address: str


# -------------------------
# BASIC ENDPOINTS
# -------------------------

@app.get("/")
def home():
    return {"message": "Welcome to E-commerce API"}


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# -------------------------
# DAY 6 – SEARCH
# -------------------------

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": f"No products found for: {keyword}", "results": []}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "results": results
    }


# -------------------------
# DAY 6 – SORT
# -------------------------

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    reverse = (order == "desc")

    sorted_products = sorted(
        products,
        key=lambda p: p[sort_by],
        reverse=reverse
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


# -------------------------
# DAY 6 – PAGINATION
# -------------------------

@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=20)
):

    start = (page - 1) * limit
    end = start + limit

    paged_products = products[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": -(-len(products) // limit),
        "products": paged_products
    }


# -------------------------
# PLACE ORDER
# -------------------------

@app.post("/orders")
def place_order(order_data: OrderRequest):

    global order_counter

    product = next((p for p in products if p["id"] == order_data.product_id), None)

    if not product:
        return {"error": "Product not found"}

    total_price = product["price"] * order_data.quantity

    order = {
        "order_id": order_counter,
        "customer_name": order_data.customer_name,
        "product": product["name"],
        "quantity": order_data.quantity,
        "delivery_address": order_data.delivery_address,
        "total_price": total_price
    }

    orders.append(order)
    order_counter += 1

    return {"message": "Order placed successfully", "order": order}


@app.get("/orders")
def get_orders():
    return {"orders": orders, "total": len(orders)}


# -------------------------
# Q4 – SEARCH ORDERS
# -------------------------

@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):

    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# -------------------------
# Q5 – SORT BY CATEGORY
# -------------------------

@app.get("/products/sort-by-category")
def sort_by_category():

    result = sorted(
        products,
        key=lambda p: (p["category"], p["price"])
    )

    return {
        "products": result,
        "total": len(result)
    }


# -------------------------
# Q6 – BROWSE (SEARCH + SORT + PAGE)
# -------------------------

@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):

    result = products

    # SEARCH
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # SORT
    if sort_by in ["price", "name"]:
        result = sorted(
            result,
            key=lambda p: p[sort_by],
            reverse=(order == "desc")
        )

    # PAGINATION
    total = len(result)

    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }


# -------------------------
# BONUS – ORDERS PAGINATION
# -------------------------

@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20)
):

    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders": orders[start:start + limit]
    }
