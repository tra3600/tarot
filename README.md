# Tarot de Marseille — bot de tirage payant

Bot qui tire les 22 arcanes majeurs du Tarot de Marseille et livre une interprétation **personnalisée** selon le thème
(Amour, Travail, Argent, Famille, Vie personnelle, Futur), la formule choisie, le prénom et la question du client.

- Tirage sans doublon, aléatoire cryptographique, chaque carte pouvant sortir à l'envers.
- 3 formules payantes : Flash (1 carte), Trio (3), Grand tirage (5), avec positions propres à chaque thème et synthèse.
- Bot Telegram avec **paiements Telegram** (Stripe & co via BotFather) : le tirage n'est livré qu'après paiement vérifié
  (montant, utilisateur, commande), et une seule fois même si l'évènement est rejoué.
- Aucune dépendance externe (Python ≥ 3.9, SQLite).

## Utilisation

```bash
python -m tarot_bot.cli            # démo console, paiement simulé
python -m unittest discover -s tests

export TELEGRAM_BOT_TOKEN=...          # BotFather
export PAYMENT_PROVIDER_TOKEN=...      # BotFather > /mybots > Payments (vide = mode démo sans paiement réel)
python -m tarot_bot.telegram_bot
```

Prix (centimes) réglables : `PRICE_FLASH_CENTS`, `PRICE_TRIO_CENTS`, `PRICE_COMPLET_CENTS`, `CURRENCY`, `TAROT_DB`.

## À faire avant la mise en ligne
- Mentions légales / CGV / droit de rétractation, RGPD (les questions des clients sont stockées dans SQLite).
- Le contenu est fourni à titre de divertissement (avertissement ajouté à chaque tirage).
- Étendre le jeu aux 56 arcanes mineurs et enrichir les textes.

`legacy/` : ancienne version C++ (non fonctionnelle, conservée pour mémoire).
