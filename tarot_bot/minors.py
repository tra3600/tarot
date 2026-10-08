"""Les 56 arcanes mineurs (Bâtons, Coupes, Épées, Deniers).

Le sens par thème d'une carte = phrase du rang (As, 2, ... Roi) + phrase de la famille (couleur).
"""
from __future__ import annotations

from .cards import Card

RANKS = ("As", "Deux", "Trois", "Quatre", "Cinq", "Six", "Sept", "Huit", "Neuf", "Dix",
         "Valet", "Cavalier", "Reine", "Roi")
SUITS = {"Bâtons": "de Bâtons", "Coupes": "de Coupes", "Épées": "d'Épées", "Deniers": "de Deniers"}

KEYWORDS = {
    "Bâtons": ("élan, création, énergie neuve", "choix d'orientation, ambition, vision",
               "expansion, attente de résultats, horizons", "célébration, stabilité, cadre",
               "rivalité, agitation, compétition", "victoire, reconnaissance, cortège",
               "défense, courage, position à tenir", "rapidité, messages, mouvement",
               "persévérance, vigilance, dernier effort", "fardeau, responsabilités, surcharge",
               "curiosité, enthousiasme, message", "fougue, aventure, impulsion",
               "charisme, chaleur, confiance", "leadership, vision, autorité inspirante"),
    "Coupes": ("amour naissant, don du cœur, ouverture", "union, réciprocité, attirance",
               "fête, amitié, joie partagée", "lassitude, introspection, offre ignorée",
               "déception, regrets, ce qui reste", "nostalgie, enfance, générosité",
               "rêves, illusions, choix multiples", "départ, abandon d'un acquis, quête",
               "vœu exaucé, satisfaction, plaisir", "bonheur familial, harmonie, épanouissement",
               "sensibilité, message du cœur, tendresse", "romantisme, proposition, charme",
               "empathie, intuition, douceur", "maîtrise émotionnelle, bienveillance, sagesse du cœur"),
    "Épées": ("clarté, vérité, victoire de l'esprit", "indécision, équilibre précaire, trêve",
              "chagrin, rupture, douleur nécessaire", "repos, retraite, récupération",
              "conflit, victoire amère, défaite", "passage, transition, apaisement",
              "stratégie, ruse, esquive", "entrave, blocage mental, impuissance",
              "angoisse, insomnie, culpabilité", "fin pénible, épuisement, dernier coup",
              "vigilance, esprit vif, curiosité critique", "action rapide, franchise, brusquerie",
              "lucidité, indépendance, franchise", "jugement, expertise, justice intellectuelle"),
    "Deniers": ("opportunité matérielle, graine de prospérité", "équilibre budgétaire, adaptation, jonglage",
                "savoir-faire, collaboration, travail reconnu", "sécurité, épargne, possessivité",
                "précarité, manque, solitude matérielle", "partage, générosité, donner et recevoir",
                "patience, investissement, bilan à mi-parcours", "apprentissage, application, artisanat",
                "autonomie, aisance, fruits du travail", "héritage, patrimoine, stabilité durable",
                "projet concret, occasion d'apprendre", "constance, fiabilité, lenteur sûre",
                "prospérité, sens pratique, générosité", "réussite matérielle, sécurité, gestion solide"),
}

RANK_SHADOW = ("occasion manquée, départ raté", "hésitation, déséquilibre", "retard, dispersion",
               "stagnation, repli excessif", "tension qui s'apaise, conflit larvé",
               "progrès lent, reconnaissance différée", "doute, défense épuisée",
               "lenteur ou précipitation", "épuisement, fausse sécurité",
               "surcharge, fin difficile à accepter", "immaturité, message retardé",
               "impétuosité, inconstance", "dépendance, humeur instable", "rigidité, abus d'autorité")

# énergie par rang (+1 porteur, 0 neutre, -1 exigeant), puis exceptions par couleur
RANK_ENERGY = (1, 0, 1, 0, -1, 1, 0, 0, 1, 1, 0, 0, 1, 1)
ENERGY_OVERRIDES = {
    "Bâtons": {9: 0, 10: 0},
    "Coupes": {4: 0},
    "Épées": {2: 0, 3: -1, 5: -1, 7: -1, 8: -1, 9: -1, 10: -1},
    "Deniers": {},
}

RANK_TEXT = {
    "amour": (
        "Un commencement se dessine : une rencontre, un élan neuf ou un regain.",
        "Un équilibre à deux se cherche ; un choix ou un dialogue s'impose.",
        "Le lien s'ouvre et se déploie ; une fête, un tiers ou un projet commun s'invite.",
        "Le couple se pose, parfois trop ; entre confort et routine, réveillez le lien.",
        "Frictions et rivalités ; les désaccords demandent à être dits sans acharnement.",
        "Une phase d'harmonie et de reconnaissance ; le lien avance sereinement.",
        "Il faut défendre ou clarifier votre position ; ne cédez pas sur l'essentiel.",
        "Les événements s'accélèrent : nouvelles, déplacements, décisions rapides.",
        "L'épreuve est presque passée ; vous tenez bon ou avez appris à vous suffire.",
        "Un cycle affectif arrive à son terme ; il peut s'achever ou s'accomplir.",
        "Une nouvelle, une personne jeune ou un élan curieux ; approche timide mais sincère.",
        "Quelqu'un arrive avec fougue, ou repart ; une proposition, un mouvement du cœur.",
        "Une figure féminine, ou une qualité d'écoute et de maturité affective, entre en jeu.",
        "Une figure masculine, ou une posture stable et protectrice, entre en jeu."),
    "travail": (
        "Nouveau départ professionnel : projet, offre ou idée à saisir.",
        "Deux options ou deux priorités ; pesez avant de vous engager.",
        "Le projet prend de l'ampleur ; premiers résultats et collaborations.",
        "Phase de stabilité ou de pause ; consolidez sans vous endormir.",
        "Concurrence, désaccords d'équipe ; cadrez les rôles et restez professionnel.",
        "Reconnaissance et progrès ; votre travail est visible.",
        "Tenez votre position face aux pressions ; argumentez calmement.",
        "Rythme rapide : échéances, déplacements, réponses attendues.",
        "Vous approchez du but ; un dernier effort et de la vigilance.",
        "Charge lourde ou fin de cycle ; déléguez et bouclez ce qui doit l'être.",
        "Un apprenti, un message ou une mission à saisir avec curiosité.",
        "Un mouvement : mutation, mission ou collaborateur dynamique ; avancez avec méthode.",
        "Une personne compétente et bienveillante, ou un management à l'écoute.",
        "Un décideur, une autorité ou l'expertise d'un chef ; assumez vos responsabilités."),
    "argent": (
        "Une opportunité financière naît : revenu, cadeau ou investissement à étudier.",
        "Jonglage entre revenus et dépenses ; équilibrez et gardez de la souplesse.",
        "Les efforts commencent à porter ; un projet financé ou un partenariat.",
        "Tendance à la prudence ou à l'accumulation ; épargnez sans vous crisper.",
        "Tension de trésorerie ou manque ; tenez vos comptes précisément, demandez de l'aide.",
        "Échanges équilibrés : recevoir, rendre, partager avec équité.",
        "Évaluez vos placements et sachez patienter ; ne vous précipitez pas.",
        "Mouvement rapide de fonds ; décidez vite mais vérifiez tout.",
        "Aisance ou fin d'un effort financier ; méfiez-vous de l'excès de confiance.",
        "Un cycle financier se boucle ; poids des dettes ou solidité durable selon votre gestion.",
        "Une petite somme, une information ou une formation à investir.",
        "Un mouvement d'argent ou une démarche rapide à sécuriser.",
        "Une gestion attentive et généreuse ; la prudence protège vos ressources.",
        "Un conseiller ou une posture de gestionnaire solide ; pensez à long terme."),
    "famille": (
        "Un nouveau chapitre familial : naissance, projet ou réconciliation.",
        "Deux points de vue s'opposent au sein de la famille ; cherchez un terrain commun.",
        "La famille s'agrandit ou se réunit ; complicité et soutien.",
        "Le foyer se stabilise ; attention au repli ou à l'ennui.",
        "Disputes, jalousies ou rancœurs ; apaisez avant que cela ne s'installe.",
        "Transmission, entraide et harmonie entre générations.",
        "Défendez votre place ou vos limites face aux proches, sans agressivité.",
        "Événements rapides : déplacements, nouvelles, changements de rythme.",
        "Les épreuves passent ; le foyer résiste et se renforce.",
        "Une étape familiale se clôt ou s'accomplit pleinement.",
        "Un enfant, un jeune proche ou une nouvelle qui arrive.",
        "Une visite, un départ ou une initiative d'un proche.",
        "Une figure maternelle, ou un rôle de soin et d'écoute.",
        "Une figure paternelle, ou un pilier protecteur."),
    "perso": (
        "Un nouveau départ intérieur ; une envie ou une idée à faire naître.",
        "Vous êtes tiraillé(e) entre deux voies ; tranchez avec calme.",
        "Vos projets prennent forme ; entourez-vous de personnes qui vous portent.",
        "Besoin de pause ou de repli ; reposez-vous sans vous couper de tout.",
        "Conflit intérieur ou avec autrui ; ce qui vous heurte révèle un besoin.",
        "Progrès et apaisement ; vous avancez vers un mieux-être.",
        "Restez fidèle à vos convictions malgré doutes et pressions.",
        "La vie s'accélère ; choisissez vos priorités.",
        "Vous êtes près du but ; ne vous épuisez pas.",
        "Un cycle personnel se termine ; allégez-vous pour repartir.",
        "Une curiosité, un apprentissage ou un message qui vous éveille.",
        "Un élan de changement ; canalisez votre énergie.",
        "Cultivez douceur, intuition ou lucidité envers vous-même.",
        "Affirmez votre maturité et votre autorité intérieure."),
    "futur": (
        "Une nouvelle voie s'ouvre à vous.",
        "Une décision ou un choix d'orientation approche.",
        "Les premiers résultats se profilent ; élargissez vos horizons.",
        "Une période de stabilité ou de pause précède la suite.",
        "Des tensions ou obstacles sont à prévoir ; ils se franchissent.",
        "Une phase de progrès et de soutien s'annonce.",
        "Il faudra tenir bon et défendre vos choix.",
        "Les événements vont vite : soyez prêt(e) à réagir.",
        "L'aboutissement est proche ; ne relâchez pas l'effort.",
        "Un cycle se termine et en prépare un autre.",
        "Une nouvelle ou une rencontre importante arrive.",
        "Un événement rapide ou une personne active bouscule les plans.",
        "Un soutien bienveillant et mûr vous accompagnera.",
        "Une personne d'autorité, ou une maturité acquise, influencera le résultat."),
}

SUIT_TEXT = {
    "Bâtons": {
        "amour": "Côté Bâtons : la passion, le désir et l'élan mènent la danse.",
        "travail": "Côté Bâtons : initiative, énergie et ambition sont au premier plan.",
        "argent": "Côté Bâtons : l'argent vient de l'action et de l'entreprise.",
        "famille": "Côté Bâtons : dynamisme, projets et énergie partagée.",
        "perso": "Côté Bâtons : votre énergie vitale et votre volonté sont sollicitées.",
        "futur": "Côté Bâtons : cela viendra de l'action et de l'audace."},
    "Coupes": {
        "amour": "Côté Coupes : le cœur et les émotions sont directement concernés.",
        "travail": "Côté Coupes : ambiance, relations et motivation comptent plus que les chiffres.",
        "argent": "Côté Coupes : attention aux dépenses dictées par l'émotion.",
        "famille": "Côté Coupes : les liens affectifs sont au centre.",
        "perso": "Côté Coupes : vos émotions et votre sensibilité ont quelque chose à dire.",
        "futur": "Côté Coupes : les sentiments et les relations orienteront la suite."},
    "Épées": {
        "amour": "Côté Épées : les mots, la lucidité et parfois la douleur sont en jeu.",
        "travail": "Côté Épées : réflexion, communication et décisions tranchées.",
        "argent": "Côté Épées : contrats, calculs et choix rationnels ; restez lucide.",
        "famille": "Côté Épées : les mots peuvent blesser ; parlez avec clarté et mesure.",
        "perso": "Côté Épées : votre mental et vos pensées sont à l'œuvre.",
        "futur": "Côté Épées : la clarté d'esprit et des décisions nettes feront la différence."},
    "Deniers": {
        "amour": "Côté Deniers : le lien se prouve par le concret, le temps et la fiabilité.",
        "travail": "Côté Deniers : résultats concrets, méthode et travail de fond.",
        "argent": "Côté Deniers : le terrain matériel est directement concerné.",
        "famille": "Côté Deniers : foyer, logement, sécurité matérielle.",
        "perso": "Côté Deniers : corps, quotidien et ressources pratiques.",
        "futur": "Côté Deniers : la concrétisation passera par le travail et la patience."},
}


def _build() -> tuple[Card, ...]:
    cards = []
    n = 22
    for suit, de in SUITS.items():
        for i, rank in enumerate(RANKS):
            energy = ENERGY_OVERRIDES[suit].get(i + 1, RANK_ENERGY[i])
            themes = {t: f"{RANK_TEXT[t][i]} {SUIT_TEXT[suit][t]}" for t in RANK_TEXT}
            name = f"L'As {de}" if rank == "As" else (
                f"La {rank} {de}" if rank == "Reine" else
                f"Le {rank} {de}" if rank in ("Valet", "Cavalier", "Roi") else f"Le {rank} {de}")
            cards.append(Card(n, name, KEYWORDS[suit][i], RANK_SHADOW[i], energy, themes, suit))
            n += 1
    return tuple(cards)


MINORS: tuple[Card, ...] = _build()
