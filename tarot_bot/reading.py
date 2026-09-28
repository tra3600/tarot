"""Tirage personnalisé : formules, positions par thème, interprétation et synthèse."""
from __future__ import annotations

import random
import secrets
from dataclasses import dataclass

from .cards import DECK, THEMES, Card

DISCLAIMER = (
    "Ce tirage est proposé à titre de divertissement et de réflexion personnelle. "
    "Il ne remplace en aucun cas un avis médical, juridique ou financier."
)

# Chaque thème a 5 positions ; la dernière est toujours le conseil.
POSITIONS: dict[str, tuple[str, ...]] = {
    "amour": ("Votre cœur en ce moment", "L'énergie de l'autre", "La dynamique du lien",
              "Le frein à dépasser", "Le conseil de l'oracle"),
    "travail": ("Votre situation professionnelle", "Votre atout principal", "Votre environnement",
                "L'obstacle à dépasser", "Le conseil de l'oracle"),
    "argent": ("Votre situation financière", "Ce qui vous soutient", "Ce qui vous échappe",
               "Le risque à éviter", "Le conseil de l'oracle"),
    "famille": ("L'ambiance du foyer", "Votre rôle", "Ce qui circule entre vous",
                "La tension à apaiser", "Le conseil de l'oracle"),
    "perso": ("Où vous en êtes", "Votre ressource intérieure", "Ce qui vous influence",
              "Ce qu'il faut lâcher", "Le conseil de l'oracle"),
    "futur": ("Le présent", "Le passé récent", "L'entourage",
              "Le défi à venir", "L'issue probable"),
}

# formule -> indices de POSITIONS utilisés
FORMULAS: dict[str, tuple[str, tuple[int, ...]]] = {
    "flash": ("Tirage Flash (1 carte)", (4,)),
    "trio": ("Tirage Trio (3 cartes)", (0, 3, 4)),
    "complet": ("Grand tirage (5 cartes)", (0, 1, 2, 3, 4)),
}

REVERSED_PROBABILITY = 0.3


@dataclass(frozen=True)
class DrawnCard:
    position: str
    card: Card
    reversed: bool

    @property
    def score(self) -> int:
        return -self.card.energy if self.reversed else self.card.energy

    def interpretation(self, theme: str) -> str:
        base = self.card.themes[theme]
        if not self.reversed:
            return base
        return f"Énergie freinée ou intériorisée ({self.card.shadow}). Sur le fond : {base[0].lower()}{base[1:]}"


@dataclass(frozen=True)
class Reading:
    theme: str
    formula: str
    name: str
    question: str
    cards: tuple[DrawnCard, ...]

    def summary(self) -> str:
        total = sum(c.score for c in self.cards)
        avg = total / len(self.cards)
        n_rev = sum(c.reversed for c in self.cards)
        if avg >= 0.5:
            tone = "Le tirage est globalement porteur : les énergies vous soutiennent, osez avancer."
        elif avg <= -0.3:
            tone = ("Le tirage est exigeant : il signale des épreuves ou des remises en question, "
                    "mais aussi une occasion de vous transformer. Avancez pas à pas.")
        else:
            tone = "Le tirage est nuancé : rien n'est joué, tout dépendra de vos choix et de votre attitude."
        if len(self.cards) > 1 and n_rev >= (len(self.cards) + 1) // 2:
            tone += " Beaucoup de cartes sont à l'envers : prenez le temps de mûrir avant d'agir."
        return tone


def draw(theme: str, formula: str, name: str = "", question: str = "",
         rng: random.Random | None = None) -> Reading:
    """Tire les cartes sans doublon. Par défaut, source aléatoire cryptographique."""
    if theme not in THEMES:
        raise ValueError(f"Thème inconnu : {theme!r} (choix : {', '.join(THEMES)})")
    if formula not in FORMULAS:
        raise ValueError(f"Formule inconnue : {formula!r} (choix : {', '.join(FORMULAS)})")
    rng = rng or secrets.SystemRandom()
    indices = FORMULAS[formula][1]
    picked = rng.sample(DECK, len(indices))
    drawn = tuple(
        DrawnCard(POSITIONS[theme][i], card, rng.random() < REVERSED_PROBABILITY)
        for i, card in zip(indices, picked)
    )
    return Reading(theme, formula, name.strip(), question.strip(), drawn)


def render(reading: Reading) -> str:
    """Texte brut du tirage, prêt à être envoyé."""
    lines = []
    greeting = f"{reading.name}, voici" if reading.name else "Voici"
    lines.append(f"🔮 {greeting} votre {FORMULAS[reading.formula][0]} — thème : {THEMES[reading.theme]}")
    if reading.question:
        lines.append(f"Votre question : « {reading.question} »")
    lines.append("")
    for d in reading.cards:
        orient = "à l'envers" if d.reversed else "à l'endroit"
        lines.append(f"▸ {d.position}")
        lines.append(f"  {d.card.name} ({orient}) — {d.card.keywords if not d.reversed else d.card.shadow}")
        lines.append(f"  {d.interpretation(reading.theme)}")
        lines.append("")
    lines.append("✨ Synthèse : " + reading.summary())
    lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)
