from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scripts.core.services.login_services import login_router
from scripts.core.services.category_services import category_router
from scripts.core.services.transaction_services import transactions_router
from scripts.core.services.user_services import user_router

app = FastAPI(title="User Expense Manager",
              description="Manages user expenses and authentication",
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the expense management app!"}


app.include_router(login_router)
app.include_router(category_router)
app.include_router(user_router)
app.include_router(transactions_router)
