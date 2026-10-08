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
pip install -r requirements.txt    # Pillow : images des cartes (facultatif, sans lui le tirage reste en texte)
python -m tarot_bot.cli            # démo console, paiement simulé
python -m unittest discover -s tests

export TELEGRAM_BOT_TOKEN=...          # BotFather
export PAYMENT_PROVIDER_TOKEN=...      # BotFather > /mybots > Payments (vide = mode démo sans paiement réel)
python -m tarot_bot.telegram_bot
```

### Images des cartes
Chaque tirage livré est précédé d'une image des cartes tirées (cartes à l'envers retournées, légende numérotée dans l'ordre du texte).
- Scans du **tarot de Nicolas Conver (Marseille, 1760)**, Bibliothèque nationale de France, département des Estampes et de la photographie
  (jeu « dit tarot Conver », btv1b10520316w, via Wikimedia Commons), **domaine public**. 66 cartes sur 78 sont illustrées :
  les 22 arcanes majeurs, les bâtons, les coupes, 6 épées (As, 2 et figures) et 10 deniers. **Il manque** les épées 3 à 10 et les deniers
  3, 4, 6 et 7, absents de l'exemplaire numérisé : ces cartes apparaissent comme une carte « non illustrée » portant leur nom.
- Pour compléter un jeu, déposez une image `NN.jpg` dans `tarot_bot/assets/cards/` (`NN` = numéro de carte : 0-21 majeurs, puis
  22 + 14 × couleur + rang ; couleurs Bâtons, Coupes, Épées, Deniers ; rangs As…Dix, Valet, Cavalier, Reine, Roi). Format conseillé : 360 px de large.
- Police : DejaVu Serif (licence Bitstream Vera, `tarot_bot/assets/fonts/DejaVu-LICENSE.txt`).
- `SEND_IMAGES=0` désactive l'envoi des images.

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

### Paiement en Étoiles Telegram (Stars)
Telegram demande les Étoiles (devise `XTR`) pour les services numériques, et elles ne nécessitent ni fournisseur ni jeton de paiement :

```bash
export PAYMENT_MODE=stars
export BUSINESS_NAME=... BUSINESS_SIRET=... BUSINESS_ADDRESS=... BUSINESS_EMAIL=... MEDIATOR=...
python -m tarot_bot.telegram_bot
```
Prix par défaut : 150 / 300 / 500 Étoiles (`PRICE_FLASH_STARS`, `PRICE_TRIO_STARS`, `PRICE_COMPLET_STARS`). Les Étoiles reçues
se retirent via Fragment (TON) selon les conditions de Telegram ; vérifiez leur valeur en euros et les règles en vigueur.
Modes : `demo` (simulé), `stars`, `provider` (fournisseur BotFather + `PAYMENT_PROVIDER_TOKEN`).

Prix (centimes) réglables : `PRICE_FLASH_CENTS`, `PRICE_TRIO_CENTS`, `PRICE_COMPLET_CENTS`, `CURRENCY`, `TAROT_DB`.

## À faire avant la mise en ligne
- Faire valider les CGV, publier une politique de confidentialité, RGPD (les questions des clients sont stockées dans SQLite).
- Le contenu est fourni à titre de divertissement (avertissement ajouté à chaque tirage).
- Enrichir les textes (les mineurs combinent une phrase par rang et une par couleur).

`legacy/` : ancienne version C++ (non fonctionnelle, conservée pour mémoire).
