## TP: Projet Conception SI Site E-commerce

### 🎯 Description du Projet

Application de e-commerce en ligne de commande permettant la gestion de comptes clients, marchands, administrateurs, ainsi que les commandes et produits, inspirée du modèle Amazon.

![app](https://alpha-gamer.com/cdn/shop/files/gaming_setup.png?v=1718151964&width=1840)

### 📝 Structure du Projet

```
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py         # Classes User, Client, Marchand, Admin
│   │   ├── store.py        # Classe Store (gestion des données)
│   │   └── product.py      # Classe Product
│   └── utils/
│       ├── __init__.py
│       └── helpers.py      # Fonctions utilitaires
├── data/
│   └── data.json           # Stockage des données
├── tests/
│   ├── __init__.py
│   ├── test_user.py
│   ├── test_client.py
│   ├── test_marchand.py
│   ├── test_product.py
│   └── test_store.py
├── main.py                 # Point d'entrée de l'application
└── requirements.txt        # Dépendances du projet
```

### 🛠️ Technologies

- **Python**
- **Rich Console**
- **Pytest**
- **UML et OCL**
- **JSON pour les données**

```python
rich==13.9.4      # Interface console améliorée
pytest==8.3.3     # Tests unitaires
```

### Installation et Exécution

1. Créer un environnement virtuel : 

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Exécuter l'application :

```bash
python main.py
```

4. Exécuter les tests :

```bash
pytest              # Tous les tests
pytest tests/test_client.py  # Tests spécifiques
pytest -v          # Mode verbeux
```

### 🕵️ Description des Classes

**User**: Classe de base pour tous les utilisateurs

- **Attributs :** email, password, nom, prenom, telephone, adresse, balance, carte_bancaire  
- **Méthodes :** credit_account(), add_bank_card()

**Client (hérite de User)**: Gestion des clients

- **Attributs supplémentaires :** panier, commandes  
- **Méthodes :** add_to_cart(), remove_from_cart(), place_order(), see_orders()

**Marchand (hérite de User)**: Gestion des marchands

- **Attributs supplémentaires :** products, commandes_recues
- **Méthodes :** add_product(), view_products(), modify_command_status(), manage_stock()

**Admin (hérite de User)**: Gestion des administrateurs

- **Méthodes :** view_all_users(), view_all_products(), delete_user(), delete_product(), generate_stats()

**Product**: Gestion des produits

- **Attributs :** id, nom, description, prix, quantite, categorie, vendeur
- **Méthodes :** generate_id()

**Store**: Gestion centrale de l'application

- **Attributs :** users, current_user
- **Méthodes :** register_user(), login(), save_data(), load_data()

### 🔬 Structure des Données (data.json)

```json
{
    "users": [
        {
            "email": "client@example.com",
            "password": "hashed_password",
            "nom": "Nom",
            "prenom": "Prenom",
            "telephone": "0123456789",
            "adresse": "Adresse",
            "balance": 0.0,
            "carte_bancaire": null,
            "type": "client",
            "panier": {},
            "commandes": []
        },
        {
            "email": "marchand@example.com",
            "type": "marchand",
            "products": [],
            "commandes_recues": []
        }
    ]
}
```

### 🧪 Tests

Les tests sont organisés par classe et couvrent :

- Validation des données
- Gestion des utilisateurs
- Processus de commande
- Gestion des produits
- Persistance des données

### ⚙️ Fonctionnalités Principales

- Client
    - Création de compte
    - Gestion du panier
    - Passage de commandes
    - Suivi des commandes
    - Gestion des retours

- Marchand

    - Gestion des produits
    - Gestion des stocks
    - Suivi des commandes
    - Traitement des retours

- Admin

    - Gestion des utilisateurs
    - Supervision du système
    - Statistiques et rapports

- Sécurité

    - Mots de passe hashés (SHA-256)
    - Validation des données
    - Gestion des permissions
