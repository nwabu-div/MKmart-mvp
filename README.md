# MokoMarket MVP
Diowire development project DDP/MVP/2025/000000001: mkmart

## Description
Electronics marketplace backend with seller auth, product management, order recording, and AI restock alerts.

## Setup
1. pip install -r requirements.txt
2. Create .env with secrets (see guide.md)
3. uvicorn main:app --reload
4. Docs: /docs

## Features
- Email + Password auth with OTP verification
- Add/List products
- Record sales (orders)
- AI alerts on top selling categories

## Deployment
Live on Render: https://mkmart-mvp.onrender.com
