"""Configuration par variables d'environnement."""
import os

# Prix en centimes, par formule.
PRICES_CENTS = {
    "flash": int(os.getenv("PRICE_FLASH_CENTS", "299")),
    "trio": int(os.getenv("PRICE_TRIO_CENTS", "599")),
    "complet": int(os.getenv("PRICE_COMPLET_CENTS", "999")),
}
# Prix en Étoiles Telegram (Stars, devise XTR), utilisés quand PAYMENT_MODE=stars.
PRICES_STARS = {
    "flash": int(os.getenv("PRICE_FLASH_STARS", "75")),
    "trio": int(os.getenv("PRICE_TRIO_STARS", "180")),
    "complet": int(os.getenv("PRICE_COMPLET_STARS", "330")),
}
CURRENCY = os.getenv("CURRENCY", "EUR")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Jeton fourni par BotFather (Stripe, etc.). Vide = mode démo sans vrai paiement.
PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
PAYMENT_MODE = os.getenv("PAYMENT_MODE", "")  # demo | stars | provider ; vide = déduit du jeton de paiement
SEND_IMAGES = os.getenv("SEND_IMAGES", "1") != "0"  # image des cartes tirées (nécessite Pillow)
DB_PATH = os.getenv("TAROT_DB", "tarot.db")

# Identité du vendeur, affichée dans les CGV (à renseigner avant la mise en ligne).
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "[NOM DU VENDEUR]")
BUSINESS_SIRET = os.getenv("BUSINESS_SIRET", "[SIRET]")
BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS", "[ADRESSE]")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "[EMAIL DE CONTACT]")
MEDIATOR = os.getenv("MEDIATOR", "[NOM ET COORDONNÉES DU MÉDIATEUR DE LA CONSOMMATION]")


MODES = ("demo", "stars", "provider")


def payment_mode() -> str:
    """stars : Étoiles Telegram (services numériques) ; provider : fournisseur BotFather ; demo : paiement simulé."""
    mode = PAYMENT_MODE.strip().lower() or ("provider" if PROVIDER_TOKEN else "demo")
    if mode not in MODES:
        raise SystemExit(f"PAYMENT_MODE invalide : {mode!r} (choix : {', '.join(MODES)})")
    return mode


def amount(formula: str, mode: str) -> int:
    """Montant facturé : Étoiles en mode stars, sinon centimes. Stocké dans orders.amount_cents."""
    return PRICES_STARS[formula] if mode == "stars" else PRICES_CENTS[formula]


def currency(mode: str) -> str:
    return "XTR" if mode == "stars" else CURRENCY


def format_price(formula: str, mode: str) -> str:
    if mode == "stars":
        return f"{PRICES_STARS[formula]} ⭐ Étoiles Telegram"
    return f"{PRICES_CENTS[formula] / 100:.2f} {CURRENCY} TTC"
