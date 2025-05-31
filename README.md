# Digital Wallet System 

This is a digital wallet system implemented in Flask.

I chose Flask because it's a lightweight, flexible, and modular Python web framework that allows for rapid development. It also integrates seamlessly with extensions like JWT for secure authentication, making it a great fit for building RESTful APIs in this wallet system.

I used Flask-SQLAlchemy because it allows defining database models as Python classes, making the code cleaner and more maintainable. Additionally, it integrates well with Flask's app context and helps in performing secure, efficient CRUD operations, which are essential for managing user accounts, wallets, and transaction records.

## Major Features
- User registration and login using JWT authentication
- Password hashing using bcrypt for enhanced security
- Multi-currency wallet support (INR, USD, YEN, EURO)
- Deposit, withdraw, and transfer operations with validations
- Full transaction history for each user
- Basic fraud detection based on thresholds
- Admin routes for monitoring flagged transactions, total balances, and top users
- Clean and modular Flask project structure
- 
## Two Major Database Models

### User

- Stores credentials, profile, balances (INR, USD, YEN, EURO)
- Handles JWT and password hashing

### Transaction

- Logs all wallet actions
- Tracks type, amount, currency, time
- Flags suspicious activity

## Basic Fraud Detection

A rule-based fraud detection system is implemented by defining specific thresholds:

- Withdrawals over ₹10,000
- Deposits over ₹50,000
- More than 5 transfers within 5 minutes

These actions are flagged as suspicious.


## Routes Overview

### Authentication Routes

These manage user registration and login.

| Method | Endpoint         | Description                          |
|--------|------------------|--------------------------------------|
| POST   | /auth/register   | Register a new user                  |
| POST   | /auth/login      | Login with credentials to get JWT    |

### Wallet Operations (JWT Required)

| Method | Endpoint              | Description                                    |
|--------|-----------------------|------------------------------------------------|
| GET    | /wallet/balance       | Get balances in all supported currencies       |
| POST   | /wallet/deposit       | Deposit money to your wallet                   |
| POST   | /wallet/withdraw      | Withdraw funds from a specific currency        |
| POST   | /wallet/transfer      | Transfer funds to another registered user      |
| GET    | /wallet/transactions  | View your complete transaction history         |

### Admin Operations (Admin JWT Required)

| Method | Endpoint                     | Description                                      |
|--------|------------------------------|--------------------------------------------------|
| GET    | /admin/flagged-transactions  | See all transactions flagged as suspicious       |
| GET    | /admin/total-balances        | View total balances system-wide                 |
| GET    | /admin/top-users             | See top users based on balance/activity          |
