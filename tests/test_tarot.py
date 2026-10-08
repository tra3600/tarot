import random
import unittest

from tarot_bot import config, legal
from tarot_bot.cards import DECK, THEMES
from tarot_bot.minors import MINORS
from tarot_bot.reading import FORMULAS, FULL_DECK, POSITIONS, draw, render
from tarot_bot.storage import Storage
from tarot_bot.telegram_bot import Bot


class FakeApi:
    def __init__(self):
        self.calls = []

    def call(self, method, **params):
        self.calls.append((method, params))
        return True

    def sent(self):
        return [p["text"] for m, p in self.calls if m == "sendMessage"]


class DeckTests(unittest.TestCase):
    def test_deck_complete(self):
        self.assertEqual(len(DECK), 22)
        self.assertEqual(sorted(c.number for c in DECK), list(range(22)))
        for c in DECK:
            self.assertEqual(set(c.themes), set(THEMES), c.name)
            self.assertTrue(all(c.themes.values()) and c.shadow and c.keywords)


class MinorTests(unittest.TestCase):
    def test_56_minors(self):
        self.assertEqual(len(MINORS), 56)
        self.assertEqual(len(FULL_DECK), 78)
        self.assertEqual(len({c.name for c in FULL_DECK}), 78)
        self.assertEqual(len({c.number for c in FULL_DECK}), 78)
        for c in MINORS:
            self.assertEqual(set(c.themes), set(THEMES), c.name)
            self.assertTrue(all(c.themes.values()) and c.shadow and c.keywords and c.suit)
        self.assertEqual({c.suit for c in MINORS}, {"Bâtons", "Coupes", "Épées", "Deniers"})

    def test_minors_can_be_drawn(self):
        seen = set()
        for _ in range(200):
            seen |= {d.card.suit for d in draw("amour", "complet").cards}
        self.assertIn("Coupes", seen)
        self.assertTrue(all(not d.card.suit for d in draw("amour", "complet", full_deck=False).cards))


class DrawTests(unittest.TestCase):
    def test_all_themes_and_formulas(self):
        for theme in THEMES:
            self.assertEqual(len(POSITIONS[theme]), 5)
            for formula, (_, idx) in FORMULAS.items():
                r = draw(theme, formula, "Ana", "Que faire ?")
                self.assertEqual(len(r.cards), len(idx))
                self.assertEqual(len({d.card.name for d in r.cards}), len(idx))
                text = render(r)
                self.assertIn("Ana", text)
                self.assertIn("Synthèse", text)

    def test_seeded_reproducible_and_varied(self):
        a = draw("amour", "complet", rng=random.Random(1))
        b = draw("amour", "complet", rng=random.Random(1))
        self.assertEqual(a, b)
        seen = {tuple(d.card.name for d in draw("amour", "trio").cards) for _ in range(20)}
        self.assertGreater(len(seen), 1)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            draw("inconnu", "flash")
        with self.assertRaises(ValueError):
            draw("amour", "inconnue")


def msg(user, text=None, **extra):
    m = {"chat": {"id": user}, "from": {"id": user, "first_name": "Ana"}}
    if text is not None:
        m["text"] = text
    m.update(extra)
    return {"message": m}


def cb(user, data):
    return {"callback_query": {"id": "1", "data": data, "from": {"id": user},
                               "message": {"chat": {"id": user}}}}


class BotTests(unittest.TestCase):
    def flow(self, demo):
        api, db = FakeApi(), Storage()
        bot = Bot(api, db, "demo" if demo else "provider")
        for u in (msg(1, "/start"), cb(1, "t:amour"), cb(1, "f:trio"), msg(1, "Va-t-il revenir ?"),
                  cb(1, "cgv:ok")):
            bot.handle(u)
        return api, db, bot

    def test_demo_flow_delivers(self):
        api, db, _ = self.flow(demo=True)
        self.assertTrue(any("thème : Amour" in t for t in api.sent()))
        self.assertEqual(db.get_order(1)["status"], "paid")

    def test_real_flow_requires_payment_and_is_idempotent(self):
        api, db, bot = self.flow(demo=False)
        invoice = [p for m, p in api.calls if m == "sendInvoice"][0]
        self.assertEqual(invoice["prices"][0]["amount"], config.PRICES_CENTS["trio"])
        self.assertEqual(db.get_order(1)["status"], "pending")
        self.assertFalse(any("Synthèse" in t for t in api.sent()))
        pay = {"invoice_payload": "1", "total_amount": config.PRICES_CENTS["trio"],
               "telegram_payment_charge_id": "ch1"}
        bot.handle(msg(1, successful_payment=pay))
        bot.handle(msg(1, successful_payment=pay))  # rejeu
        self.assertEqual(sum("Synthèse" in t for t in api.sent()), 1)

    def test_cgv_required_before_payment(self):
        api, db = FakeApi(), Storage()
        bot = Bot(api, db, "provider")
        for u in (msg(1, "/start"), cb(1, "t:amour"), cb(1, "f:trio"), msg(1, "Question ?")):
            bot.handle(u)
        self.assertFalse(any(m == "sendInvoice" for m, _ in api.calls))
        self.assertIsNone(db.get_order(1))
        bot.handle(cb(1, "cgv:no"))  # refus : aucune commande
        bot.handle(cb(1, "cgv:ok"))  # session effacée : on repart du début, toujours pas de facture
        self.assertFalse(any(m == "sendInvoice" for m, _ in api.calls))
        self.assertIsNone(db.get_order(1))

    def test_cgv_consent_recorded_and_text(self):
        _, db, _ = self.flow(demo=False)
        order = db.get_order(1)
        self.assertEqual(order["cgv_version"], legal.CGV_VERSION)
        self.assertIsNotNone(order["cgv_accepted_at"])
        text = legal.cgv_text()
        self.assertIn("rétractation", text)
        self.assertIn("L221-28", text)

    def test_old_orders_without_consent_rejected(self):
        api, db = FakeApi(), Storage()
        oid = db.create_order(1, "amour", "flash", "A", "", config.PRICES_CENTS["flash"], config.CURRENCY)
        Bot(api, db, "provider").handle({"pre_checkout_query": {
            "id": "1", "invoice_payload": str(oid), "from": {"id": 1},
            "total_amount": config.PRICES_CENTS["flash"], "currency": config.CURRENCY}})
        self.assertFalse(api.calls[-1][1]["ok"])

    def test_erasure_command(self):
        api, db, bot = self.flow(demo=True)       # commande 1 payée (démo)
        db.create_order(1, "amour", "flash", "Ana", "Q2", 299, "EUR", cgv_version="v")  # commande en attente
        db.create_order(2, "amour", "flash", "Bob", "Q3", 299, "EUR", cgv_version="v")  # autre utilisateur
        bot.handle(msg(1, "/supprimer"))
        self.assertTrue(any(m == "sendMessage" and "Confirmer" in p["text"] for m, p in api.calls))
        self.assertIsNotNone(db.get_order(1)["result"])  # rien n'est effacé avant confirmation
        bot.handle(cb(1, "del:ok"))
        paid = db.get_order(1)
        self.assertEqual((paid["name"], paid["question"], paid["result"], paid["user_id"]), ("", "", None, 0))
        self.assertEqual(paid["status"], "paid")
        self.assertEqual(paid["amount_cents"], config.PRICES_CENTS["trio"])
        self.assertIsNone(db.get_order(2))        # non payée : supprimée
        self.assertEqual(db.get_order(3)["name"], "Bob")  # autre utilisateur intact

    def test_erasure_cancel_keeps_data(self):
        api, db, bot = self.flow(demo=True)
        bot.handle(cb(1, "del:no"))
        self.assertEqual(db.get_order(1)["name"], "Ana")

    def test_stale_callback_ack_does_not_block(self):
        import urllib.error

        class StaleAckApi(FakeApi):
            def call(self, method, **params):
                if method == "answerCallbackQuery":
                    raise urllib.error.HTTPError("u", 400, "query is too old", {}, None)
                return super().call(method, **params)

        api = StaleAckApi()
        bot = Bot(api, Storage(), "demo")
        bot.handle(cb(1, "t:amour"))
        self.assertTrue(any("Choisissez votre formule" in t for t in api.sent()))

    def stars_flow(self):
        api, db = FakeApi(), Storage()
        bot = Bot(api, db, "stars")
        for u in (msg(1, "/start"), cb(1, "t:travail"), cb(1, "f:flash"), msg(1, "Promotion ?"), cb(1, "cgv:ok")):
            bot.handle(u)
        return api, db, bot

    def test_stars_invoice_has_no_provider_token(self):
        api, db, bot = self.stars_flow()
        invoice = [p for m, p in api.calls if m == "sendInvoice"][0]
        self.assertEqual(invoice["currency"], "XTR")
        self.assertNotIn("provider_token", invoice)
        self.assertEqual(invoice["prices"][0]["amount"], config.PRICES_STARS["flash"])
        order = db.get_order(1)
        self.assertEqual((order["currency"], order["amount_cents"], order["status"]),
                         ("XTR", config.PRICES_STARS["flash"], "pending"))

    def test_stars_payment_delivers_once_and_checks_amount(self):
        api, db, bot = self.stars_flow()
        ok = {"id": "9", "invoice_payload": "1", "from": {"id": 1}, "currency": "XTR",
              "total_amount": config.PRICES_STARS["flash"]}
        bot.handle({"pre_checkout_query": ok})
        self.assertTrue(api.calls[-1][1]["ok"])
        bot.handle({"pre_checkout_query": dict(ok, total_amount=1)})  # mauvais montant
        self.assertFalse(api.calls[-1][1]["ok"])
        bot.handle({"pre_checkout_query": dict(ok, currency="EUR")})  # mauvaise devise
        self.assertFalse(api.calls[-1][1]["ok"])
        pay = {"invoice_payload": "1", "total_amount": config.PRICES_STARS["flash"], "currency": "XTR",
               "telegram_payment_charge_id": "stars-1"}
        bot.handle(msg(1, successful_payment=dict(pay, currency="EUR")))  # devise incohérente : refusé
        self.assertFalse(any("Synthèse" in t for t in api.sent()))
        bot.handle(msg(1, successful_payment=pay))
        bot.handle(msg(1, successful_payment=pay))
        self.assertEqual(sum("Synthèse" in t for t in api.sent()), 1)
        self.assertEqual(db.get_order(1)["charge_id"], "stars-1")

    def test_stars_prices_shown_in_cgv_and_buttons(self):
        self.assertIn("Étoiles Telegram", legal.cgv_text("stars"))
        self.assertIn(str(config.PRICES_STARS["trio"]), config.format_price("trio", "stars"))
        self.assertIn("EUR", config.format_price("trio", "provider"))

    def test_wrong_amount_or_user_refused(self):
        api, db, bot = self.flow(demo=False)
        bot.handle({"pre_checkout_query": {"id": "9", "invoice_payload": "1", "from": {"id": 2},
                                           "total_amount": config.PRICES_CENTS["trio"],
                                           "currency": config.CURRENCY}})
        self.assertFalse(api.calls[-1][1]["ok"])
        bot.handle(msg(2, successful_payment={"invoice_payload": "1", "total_amount": 1}))
        self.assertFalse(any("Synthèse" in t for t in api.sent()))


if __name__ == "__main__":
    unittest.main()
