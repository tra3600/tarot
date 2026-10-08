"""Stockage SQLite : commandes et tirages livrés (un tirage payé n'est livré qu'une fois)."""
from __future__ import annotations

import sqlite3
import time


class Storage:
    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, theme TEXT NOT NULL, formula TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '', question TEXT NOT NULL DEFAULT '',
            amount_cents INTEGER NOT NULL, currency TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            charge_id TEXT, result TEXT, created_at REAL NOT NULL,
            cgv_version TEXT, cgv_accepted_at REAL)""")
        cols = {r["name"] for r in self.db.execute("PRAGMA table_info(orders)")}
        for col, typ in (("cgv_version", "TEXT"), ("cgv_accepted_at", "REAL")):  # bases créées avant les CGV
            if col not in cols:
                self.db.execute(f"ALTER TABLE orders ADD COLUMN {col} {typ}")
        self.db.commit()

    def create_order(self, user_id, theme, formula, name, question, amount_cents, currency,
                     cgv_version=None) -> int:
        cur = self.db.execute(
            "INSERT INTO orders (user_id, theme, formula, name, question, amount_cents, currency, created_at,"
            " cgv_version, cgv_accepted_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (user_id, theme, formula, name, question, amount_cents, currency, time.time(),
             cgv_version, time.time() if cgv_version else None))
        self.db.commit()
        return cur.lastrowid

    def get_order(self, order_id: int):
        return self.db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

    def mark_paid(self, order_id: int, charge_id: str, result: str) -> bool:
        """Passe la commande en 'paid' une seule fois. Retourne False si déjà payée (idempotent)."""
        cur = self.db.execute(
            "UPDATE orders SET status='paid', charge_id=?, result=? WHERE id=? AND status='pending'",
            (charge_id, result, order_id))
        self.db.commit()
        return cur.rowcount == 1
