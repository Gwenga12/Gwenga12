# Discord Bot Manager (Avancé)

Application de bureau simple en Python (Tkinter) pour gérer les commandes, les prix, les statuts et les fonctions d'un bot Discord avec choix du forfait (simple, modération, économie, RP/Gaming, avancé sur mesure).

## Fonctionnalités
- Écran d'accueil avec 4 boutons : Ajouter, À finir, À livrer, Statistiques, et une liste des commandes avec mise à jour de statut.
- Ajouter une commande avec forfait, statut, prix et fonctions.
- Forfaits pré-remplis (fonctions + prix) sauf pour l'avancé (100% personnalisable).
- Statistiques de ventes avec total gagné et graphique par forfait.
- Sauvegarde automatique à la fermeture + sauvegarde locale en JSON.

## Prérequis
- Python 3.9+

## Lancer l'application
```bash
python app.py
```

Le fichier de données est stocké par défaut dans `data/advanced_plan.json`.
