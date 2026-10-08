# Tarot de Marseille — bot de tirage payant

Bot qui tire les 78 lames du Tarot de Marseille (22 arcanes majeurs + 56 mineurs) et livre une interprétation **personnalisée** selon le thème
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

### Docker
```bash
cp .env.example .env     # puis remplir le fichier (ne jamais le committer)
docker build -t tarot-bot .
docker run -d --name tarot --restart unless-stopped --env-file .env -v tarot-data:/data tarot-bot
docker logs -f tarot
```
La base `tarot.db` est dans le volume `tarot-data` : sauvegardez-le.

### CGV et consentement
Avant chaque paiement, le bot affiche un récapitulatif et exige un clic sur « J'accepte les CGV et je paie »
(âge, CGV, livraison immédiate, renonciation au droit de rétractation). La facture n'est créée qu'après ce clic, et la
version des CGV et l'horodatage sont enregistrés dans la commande. `/cgv` affiche le texte complet (`tarot_bot/legal.py`).
Avec des paiements réels, le bot refuse de démarrer tant que `BUSINESS_NAME`, `BUSINESS_SIRET`, `BUSINESS_ADDRESS`,
`BUSINESS_EMAIL` et `MEDIATOR` ne sont pas renseignés. **Le texte est un modèle : faites-le relire par un juriste.**

### Suppression des données
`/supprimer` (avec confirmation) efface le prénom, les questions et les tirages de l'utilisateur et supprime ses commandes non
payées. Les commandes payées restent, anonymisées (identifiant Telegram remplacé par 0) : montant, date, référence de paiement et
preuve d'acceptation des CGV sont conservés pour la comptabilité. Ce comportement est annoncé dans les CGV (§7).

Prix (centimes) réglables : `PRICE_FLASH_CENTS`, `PRICE_TRIO_CENTS`, `PRICE_COMPLET_CENTS`, `CURRENCY`, `TAROT_DB`.

## À faire avant la mise en ligne
- Faire valider les CGV, publier une politique de confidentialité, RGPD (les questions des clients sont stockées dans SQLite).
- Le contenu est fourni à titre de divertissement (avertissement ajouté à chaque tirage).
- Enrichir les textes (les mineurs combinent une phrase par rang et une par couleur).

`legacy/` : ancienne version C++ (non fonctionnelle, conservée pour mémoire).
