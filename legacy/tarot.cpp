#include <iostream>
#include <vector>
#include <map>
#include <cstdlib>
#include <ctime>

// Structure pour stocker les informations des cartes
struct Card {
    std::string name;
    std::string interpretation;
};

// Cartes du tarot de Marseille
std::vector<Card> tarotDeck = {
    {"Le Bateleur", "Début, potentiel, opportunité"},
    {"La Papesse", "Sagesse, mystère, intuition"},
    {"L'Impératrice", "Créativité, abondance, croissance"},
    {"L'Empereur", "Autorité, structure, contrôle"},
    {"Le Pape", "Tradition, croyances, enseignement"},
    {"Les Amoureux", "Amour, choix, harmonie"},
    {"Le Chariot", "Volonté, succès, action"},
    {"La Justice", "Équité, vérité, équilibre"},
    {"L'Hermite", "Recherche, solitude, guidance"},
    {"La Roue de Fortune", "Changement, cycle, chance"},
    {"La Force", "Courage, patience, énergie"},
    {"Le Pendu", "Suspension, sacrifice, attente"},
    {"La Mort", "Fin, transformation, renouveau"},
    {"Tempérance", "Modération, équilibre, guérison"},
    {"Le Diable", "Tentations, attachements, addictions"},
    {"La Maison Dieu", "Choc, bouleversement, révélation"},
    {"L'Étoile", "Espoir, inspiration, sérénité"},
    {"La Lune", "Illusion, peur, intuition"},
    {"Le Soleil", "Bonheur, succès, vitalité"},
    {"Le Jugement", "Réflexion, réévaluation, éveil"},
    {"Le Monde", "Achèvement, accomplissement, intégration"}
};

// Fonction pour tirer une carte aléatoire
Card drawCard() {
    int index = rand() % tarotDeck.size();
    return tarotDeck[index];
}

// Fonction pour afficher les interprétations basées sur le thème choisi
void interpretCard(const Card& card, const std::string& theme) {
    std::cout << "Carte tirée: " << card.name << std::endl;
    std::cout << "Interprétation pour le thème " << theme << ": " << card.interpretation << std::endl;
}

// Fonction pour simuler un paiement
bool processPayment() {
    std::cout << "Le service coûte 50 euros. Souhaitez-vous continuer? (oui/non): ";
    std::string response;
    std::cin >> response;
    return response == "oui";
}

int main() {
    srand(static_cast<unsigned>(time(0)));

    std::cout << "Bienvenue dans le programme de tirage du Tarot de Marseille!" << std::endl;

    // Demander à l'utilisateur de choisir un thème
    std::cout << "Veuillez choisir un thème: Amour, Vie personnelle, Travail, Famille, Futur: ";
    std::string theme;
    std::cin >> theme;

    // Simuler un paiement
    if (!processPayment()) {
        std::cout << "Paiement non effectué. Fin du programme." << std::endl;
        return 0;
    }
}