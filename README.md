# Expense-Management-System
A Backend System for Managing Expenses within an Org with Users and Groups as entities.

# Introduction
A backend system for managing expenses within an organization, featuring user management. This project includes functionalities for user registration, authentication, transaction creation, and management, using JWT for secure authentication.

![img_1.png](img_1.png)

### Features
User Management:
- Sign up
- Login
- Logout
- Update user information

Category Management:
- Create category
- Update category
- Fetch category

Transaction Management:
- Create transaction
- Update transaction
- Fetch transaction with filtering and sorting

Authentication:
- JWT-based authentication (Access Token and Refresh Token)

# API Modules

![Auth.png](Auth.png)
![user.png](user.png)
![category.png](category.png)
![transaction.png](transaction.png)

# Setup

1. Run Redis from a Docker Image.
2. Run Mongo from a Docker Image.
3. Run Postgres from a Docker Image.
4. Create .env file and add the following creds.

```text
REDIS_URI=redis://127.0.0.1:6379
MONGO_URI=mongodb://127.0.0.1:27017
POSTGRES_URI=postgresql://test_user:test@127.0.0.1:5432
```
4. Create A Virtual Env and Install Requirements
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
```bash
pip install -r requirements.txt
```
5. Start the FastAPI App
```bash
python3 app.py
```

