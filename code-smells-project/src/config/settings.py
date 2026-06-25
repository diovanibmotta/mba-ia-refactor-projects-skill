import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
DB_PATH = os.environ.get("DB_PATH", "loja.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
PORT = int(os.environ.get("PORT", "5000"))
HOST = os.environ.get("HOST", "127.0.0.1")

VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
VALID_ORDER_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

DISCOUNT_TIER_HIGH_THRESHOLD = 10000
DISCOUNT_TIER_HIGH_RATE = 0.10
DISCOUNT_TIER_MID_THRESHOLD = 5000
DISCOUNT_TIER_MID_RATE = 0.05
DISCOUNT_TIER_LOW_THRESHOLD = 1000
DISCOUNT_TIER_LOW_RATE = 0.02
