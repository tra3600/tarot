"""Version console (démo locale, paiement simulé) : python -m tarot_bot.cli"""
from __future__ import annotations

from . import config
from .cards import THEMES
from .reading import FORMULAS, draw, render


def _choose(title: str, options: dict[str, str]) -> str:
    keys = list(options)
    while True:
        print(title)
        for i, k in enumerate(keys, 1):
            print(f"  {i}. {options[k]}")
        raw = input("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            return keys[int(raw) - 1]
        print("Choix invalide.\n")


def main() -> None:
    mode = config.payment_mode()
    print("🔮 Tarot de Marseille — tirage personnalisé\n")
    name = input("Votre prénom : ").strip()
    theme = _choose("\nChoisissez un thème :", THEMES)
    formula = _choose("\nChoisissez une formule :", {
        k: f"{v[0]} — {config.format_price(k, mode)}" for k, v in FORMULAS.items()})
    question = input("\nVotre question (facultatif) : ").strip()
    if input(f"\n[Paiement simulé] Payer {config.format_price(formula, mode)} ? (oui/non) : ").strip().lower() not in ("oui", "o", "y", "yes"):
        print("Paiement non effectué. À bientôt !")
        return
    print("\n" + render(draw(theme, formula, name, question)))


if __name__ == "__main__":
    main()
