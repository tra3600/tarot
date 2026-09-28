"""Configuration par variables d'environnement."""
import os

# Prix en centimes, par formule.
PRICES_CENTS = {
    "flash": int(os.getenv("PRICE_FLASH_CENTS", "299")),
    "trio": int(os.getenv("PRICE_TRIO_CENTS", "599")),
    "complet": int(os.getenv("PRICE_COMPLET_CENTS", "999")),
}
CURRENCY = os.getenv("CURRENCY", "EUR")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Jeton fourni par BotFather (Stripe, etc.). Vide = mode démo sans vrai paiement.
PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
DB_PATH = os.getenv("TAROT_DB", "tarot.db")
