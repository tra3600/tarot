"""Conditions générales de vente (CGV) et consentement avant paiement.

MODÈLE À FAIRE VALIDER par un juriste avant toute vente : il suit les obligations usuelles du droit français de
la consommation (identité du vendeur, prix TTC, contenu numérique livré immédiatement, renonciation expresse au
droit de rétractation - art. L221-28 13° C. conso., médiation - art. L612-1 C. conso.).
"""
from __future__ import annotations

from . import config
from .reading import FORMULAS

CGV_VERSION = "2026-10-08-2"  # à changer à chaque modification du texte


def is_configured() -> bool:
    """Faux tant que les mentions du vendeur sont encore des [PLACEHOLDERS]."""
    fields = (config.BUSINESS_NAME, config.BUSINESS_SIRET, config.BUSINESS_ADDRESS,
              config.BUSINESS_EMAIL, config.MEDIATOR)
    return not any(f.startswith("[") for f in fields)


def _prices() -> str:
    return "\n".join(f"  • {lbl} : {config.PRICES_CENTS[k] / 100:.2f} {config.CURRENCY} TTC"
                     for k, (lbl, _) in FORMULAS.items())


def cgv_text() -> str:
    return f"""CONDITIONS GÉNÉRALES DE VENTE (version {CGV_VERSION})

1. Vendeur
{config.BUSINESS_NAME} — SIRET {config.BUSINESS_SIRET} — {config.BUSINESS_ADDRESS} — {config.BUSINESS_EMAIL}

2. Service
Tirage de Tarot de Marseille personnalisé, livré sous forme de texte dans cette conversation Telegram. Il est fourni \
à titre de divertissement et de réflexion personnelle. Il ne constitue ni un avis médical, juridique, financier ou \
psychologique, ni une promesse de résultat. Le service est réservé aux personnes majeures.

3. Prix
{_prices()}
Le prix est payable en une fois, avant la livraison, par le moyen de paiement proposé par Telegram.

4. Livraison
Le tirage est livré immédiatement après confirmation du paiement.

5. Droit de rétractation
Le service est un contenu numérique fourni sans support matériel. En demandant sa livraison immédiate, vous acceptez \
que son exécution commence avant la fin du délai de rétractation de 14 jours et vous renoncez expressément à \
votre droit de rétractation (art. L221-28, 13° du Code de la consommation).

6. Problème de livraison
Si vous avez payé et n'avez pas reçu votre tirage, ou si une erreur technique s'est produite, écrivez à \
{config.BUSINESS_EMAIL} : nous livrons à nouveau le tirage ou nous remboursons.

7. Données personnelles
Votre identifiant Telegram, votre prénom et votre question sont conservés pour fournir le service et prouver la vente. \
Vous pouvez les effacer à tout moment avec la commande /supprimer (ou en écrivant à {config.BUSINESS_EMAIL}). \
Seules les informations de la transaction (montant, date, référence de paiement, preuve d'acceptation des CGV) \
sont conservées, sans votre prénom ni votre question, pour les obligations comptables et la preuve de la vente. Aucune donnée de carte bancaire n'est vue ni \
conservée par le service : le paiement est traité par le prestataire de paiement.

8. Médiation et droit applicable
En cas de litige, vous pouvez recourir gratuitement au médiateur de la consommation : {config.MEDIATOR}. \
Les présentes CGV sont soumises au droit français."""


def consent_prompt(price_cents: int) -> str:
    return (f"Avant de payer ({price_cents / 100:.2f} {config.CURRENCY} TTC), merci de lire les CGV (/cgv).\n\n"
            "En cliquant sur « J'accepte », vous confirmez : avoir 18 ans ou plus, accepter les CGV, "
            "demander la livraison immédiate du tirage et renoncer à votre droit de rétractation.")
