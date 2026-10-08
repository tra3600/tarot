"""Bot Telegram payant (sans dépendance externe : API HTTP + paiements Telegram).

Flux : /start -> thème -> formule -> question -> facture -> paiement -> tirage livré.
Modes de paiement (PAYMENT_MODE) :
  stars    : Étoiles Telegram (devise XTR, aucun jeton de paiement) - requis pour les services numériques ;
  provider : fournisseur BotFather (PAYMENT_PROVIDER_TOKEN) ;
  demo     : paiement simulé, à ne pas utiliser en production (mode par défaut sans jeton de paiement).
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
import uuid

from . import config, images, legal
from .cards import THEMES
from .reading import DISCLAIMER, FORMULAS, draw, render
from .storage import Storage

log = logging.getLogger("tarot")
MAX_QUESTION = 300
MAX_MSG = 4000  # limite Telegram : 4096


class Api:
    def __init__(self, token: str):
        self.base = f"https://api.telegram.org/bot{token}/"

    def call(self, method: str, **params):
        req = urllib.request.Request(
            self.base + method, data=json.dumps(params).encode(),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=70) as r:
                return json.load(r)["result"]
        except urllib.error.HTTPError as e:
            log.error("API %s: %s %s", method, e.code, e.read()[:200])
            raise

    def send_photo(self, chat_id, jpeg: bytes):
        """Envoie une image JPEG (multipart/form-data)."""
        boundary = uuid.uuid4().hex
        parts = [(f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n').encode(),
                 (f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="tirage.jpg"\r\n'
                  'Content-Type: image/jpeg\r\n\r\n').encode(), jpeg,
                 f'\r\n--{boundary}--\r\n'.encode()]
        req = urllib.request.Request(self.base + "sendPhoto", data=b"".join(parts),
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        try:
            with urllib.request.urlopen(req, timeout=70) as r:
                return json.load(r)["result"]
        except urllib.error.HTTPError as e:
            log.error("API sendPhoto: %s %s", e.code, e.read()[:200])
            raise


def _keyboard(rows):
    return {"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in row] for row in rows]}


class Bot:
    def __init__(self, api, storage: Storage, mode: str = "demo"):
        self.api, self.db, self.mode = api, storage, mode
        self.sessions: dict[int, dict] = {}  # user_id -> {step, theme, formula, name}

    # -- envoi ---------------------------------------------------------
    def send(self, chat_id, text, **kw):
        for i in range(0, len(text), MAX_MSG):
            self.api.call("sendMessage", chat_id=chat_id, text=text[i:i + MAX_MSG], **kw)

    def show_themes(self, chat_id, user_id):
        self.sessions[user_id] = {"step": "theme"}
        rows = [[(label, f"t:{key}")] for key, label in THEMES.items()]
        self.send(chat_id, "🔮 Bienvenue au Tarot de Marseille.\nSur quel thème souhaitez-vous un éclairage ?",
                  reply_markup=_keyboard(rows))

    # -- traitement des mises à jour -------------------------------------
    def handle(self, update: dict):
        if "message" in update:
            self.on_message(update["message"])
        elif "callback_query" in update:
            self.on_callback(update["callback_query"])
        elif "pre_checkout_query" in update:
            self.on_pre_checkout(update["pre_checkout_query"])

    def on_message(self, m):
        chat_id, user_id = m["chat"]["id"], m["from"]["id"]
        if "successful_payment" in m:
            return self.on_paid(chat_id, user_id, m["successful_payment"])
        text = (m.get("text") or "").strip()
        if text.startswith(("/start", "/tirage")):
            return self.show_themes(chat_id, user_id)
        if text.startswith("/cgv"):
            return self.send(chat_id, legal.cgv_text(self.mode))
        if text.startswith("/supprimer"):
            return self.send(chat_id, "Cela efface votre prénom, vos questions et vos tirages de nos données. "
                             "Seules les informations de paiement (montant, date, référence) sont conservées "
                             "sans votre nom, comme l'exige la comptabilité. Confirmer ?",
                             reply_markup=_keyboard([[("🗑 Oui, tout supprimer", "del:ok")],
                                                     [("Annuler", "del:no")]]))
        if text.startswith("/aide"):
            return self.send(chat_id, "Tapez /start pour un nouveau tirage, /cgv pour les conditions de vente, /supprimer pour effacer vos données.\n\n"
                             + DISCLAIMER)
        s = self.sessions.get(user_id)
        if s and s.get("step") == "question":
            question = "" if text.lower() in ("non", "-", "aucune") else text[:MAX_QUESTION]
            name = (m["from"].get("first_name") or "")[:40]
            s.update(step="cgv", name=name, question=question)
            return self.send(chat_id, legal.consent_prompt(s["formula"], self.mode),
                             reply_markup=_keyboard([[("✅ J'accepte les CGV et je paie", "cgv:ok")],
                                                     [("📄 Lire les CGV", "cgv:read")],
                                                     [("❌ Annuler", "cgv:no")]]))
        self.send(chat_id, "Tapez /start pour commencer un tirage.")

    def on_callback(self, q):
        chat_id, user_id, data = q["message"]["chat"]["id"], q["from"]["id"], q.get("data", "")
        try:  # simple accusé de réception : il échoue si le clic est trop ancien et ne doit rien bloquer
            self.api.call("answerCallbackQuery", callback_query_id=q["id"])
        except urllib.error.HTTPError:
            pass
        if data.startswith("t:") and data[2:] in THEMES:
            self.sessions[user_id] = {"step": "formula", "theme": data[2:]}
            rows = [[(f"{lbl} — {config.format_price(k, self.mode)}", f"f:{k}")]
                    for k, (lbl, _) in FORMULAS.items()]
            self.send(chat_id, f"Thème : {THEMES[data[2:]]}. Choisissez votre formule :",
                      reply_markup=_keyboard(rows))
        elif data in ("del:ok", "del:no"):
            if data == "del:ok":
                self.sessions.pop(user_id, None)
                n = self.db.erase_user(user_id)
                self.send(chat_id, f"✅ Vos données ont été effacées ({n} commande(s) concernée(s)).")
            else:
                self.send(chat_id, "Suppression annulée.")
        elif data.startswith("cgv:"):
            s = self.sessions.get(user_id)
            if data == "cgv:read":
                self.send(chat_id, legal.cgv_text(self.mode))
            elif not s or s.get("step") != "cgv":
                self.show_themes(chat_id, user_id)
            elif data == "cgv:ok":
                self.checkout(chat_id, user_id, s["theme"], s["formula"], s["name"], s["question"])
            else:
                self.sessions.pop(user_id, None)
                self.send(chat_id, "Commande annulée, rien n'a été débité. Tapez /start pour recommencer.")
        elif data.startswith("f:") and data[2:] in FORMULAS:
            s = self.sessions.get(user_id)
            if not s or "theme" not in s:
                return self.show_themes(chat_id, user_id)
            s.update(step="question", formula=data[2:])
            self.send(chat_id, "Posez votre question en une phrase (ou écrivez « non »).")

    # -- paiement ---------------------------------------------------------
    def checkout(self, chat_id, user_id, theme, formula, name, question):
        amount, currency = config.amount(formula, self.mode), config.currency(self.mode)
        order_id = self.db.create_order(user_id, theme, formula, name, question, amount, currency,
                                        cgv_version=legal.CGV_VERSION)
        self.sessions.pop(user_id, None)
        if self.mode == "demo":
            self.send(chat_id, "⚠️ Mode démo : paiement simulé.")
            return self.deliver(chat_id, order_id, "demo")
        label = f"{FORMULAS[formula][0]} — {THEMES[theme]}"
        invoice = dict(chat_id=chat_id, title="Tirage de Tarot de Marseille", description=label,
                       payload=str(order_id), currency=currency, prices=[{"label": label, "amount": amount}])
        if self.mode == "provider":  # en Étoiles (XTR), pas de jeton de paiement
            invoice["provider_token"] = config.PROVIDER_TOKEN
        self.api.call("sendInvoice", **invoice)

    def on_pre_checkout(self, q):
        order = self.db.get_order(int(q["invoice_payload"])) if q["invoice_payload"].isdigit() else None
        ok = bool(order and order["status"] == "pending" and order["cgv_version"] and order["user_id"] == q["from"]["id"]
                  and order["amount_cents"] == q["total_amount"] and order["currency"] == q["currency"])
        self.api.call("answerPreCheckoutQuery", pre_checkout_query_id=q["id"], ok=ok,
                      **({} if ok else {"error_message": "Commande invalide ou déjà payée."}))

    def on_paid(self, chat_id, user_id, pay):
        payload = pay.get("invoice_payload", "")
        order = self.db.get_order(int(payload)) if payload.isdigit() else None
        if not order or order["user_id"] != user_id or order["amount_cents"] != pay["total_amount"] \
                or order["currency"] != pay.get("currency", order["currency"]):
            log.error("Paiement non rapproché: %s", pay)
            return self.send(chat_id, "Paiement reçu mais commande introuvable : contactez le support.")
        self.deliver(chat_id, order["id"], pay.get("telegram_payment_charge_id", ""))

    def deliver(self, chat_id, order_id, charge_id):
        order = self.db.get_order(order_id)
        reading = draw(order["theme"], order["formula"], order["name"], order["question"])
        text = render(reading)
        if not self.db.mark_paid(order_id, charge_id, text):
            return  # déjà livrée : pas de double tirage
        photo = images.render_spread(reading) if config.SEND_IMAGES else None
        if photo:
            try:
                self.api.send_photo(chat_id, photo)
            except Exception:  # l'image est un plus : le tirage (texte) est livré quoi qu'il arrive
                log.exception("Envoi de l'image du tirage impossible")
        self.send(chat_id, text)
        self.send(chat_id, "Merci ! Tapez /start pour un nouveau tirage.")

    # -- boucle ----------------------------------------------------------
    def run(self):
        offset = None
        log.info("Bot démarré (%s)", {"demo": "mode démo", "stars": "paiements en Étoiles", "provider": "paiements via fournisseur"}[self.mode])
        while True:
            try:
                params = {"timeout": 50, "allowed_updates": ["message", "callback_query", "pre_checkout_query"]}
                if offset is not None:
                    params["offset"] = offset
                for u in self.api.call("getUpdates", **params):
                    offset = u["update_id"] + 1
                    try:
                        self.handle(u)
                    except Exception:
                        log.exception("Erreur de traitement")
            except Exception:
                log.exception("Erreur réseau, nouvelle tentative")
                time.sleep(5)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not config.BOT_TOKEN:
        raise SystemExit("Définissez TELEGRAM_BOT_TOKEN (voir README).")
    mode = config.payment_mode()
    if mode == "provider" and not config.PROVIDER_TOKEN:
        raise SystemExit("PAYMENT_MODE=provider demande PAYMENT_PROVIDER_TOKEN (BotFather > Payments).")
    if mode != "demo" and not legal.is_configured():
        raise SystemExit("Renseignez BUSINESS_NAME, BUSINESS_SIRET, BUSINESS_ADDRESS, BUSINESS_EMAIL et MEDIATOR "
                         "(mentions obligatoires des CGV) avant d'activer les paiements réels.")
    Bot(Api(config.BOT_TOKEN), Storage(config.DB_PATH), mode).run()


if __name__ == "__main__":
    main()
