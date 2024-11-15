import os
import json
from pathlib import Path
from datetime import datetime
from rich.prompt import Prompt
from typing import Optional, Dict

from ..utils.helpers import console, hash_password
from ..models.user import User, Client, Marchand, Admin
from ..models.product import Product

from rich.table import Table
from rich.prompt import Prompt

class Store:
    DATA_DIR = Path(__file__).parent.parent.parent / "data"
    DATA_FILE = DATA_DIR / "data.json"

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        # Créer le dossier data s'il n'existe pas
        self.DATA_DIR.mkdir(exist_ok=True)
        self.load_data()

    def load_data(self):
        if self.DATA_FILE.exists():
            try:
                with open(self.DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # Premier passage : créer tous les utilisateurs
                    for user_data in data.get("users", []):
                        if user_data["type"] == "admin":
                            user = Admin(
                                email=user_data["email"],
                                password=user_data["password"],
                                nom=user_data["nom"],
                                prenom=user_data["prenom"],
                                telephone=user_data["telephone"],
                                adresse=user_data["adresse"]
                            )
                            user.balance = user_data.get("balance", 0.0)
                            user.carte_bancaire = user_data.get("carte_bancaire")
                        elif user_data["type"] == "client":
                            user = Client(
                                email=user_data["email"],
                                password=user_data["password"],
                                nom=user_data["nom"],
                                prenom=user_data["prenom"],
                                telephone=user_data["telephone"],
                                adresse=user_data["adresse"]
                            )
                            user.balance = user_data.get("balance", 0.0)
                            user.carte_bancaire = user_data.get("carte_bancaire")
                            user.panier = user_data.get("panier", {})
                        else:  # Marchand
                            user = Marchand(
                                email=user_data["email"],
                                password=user_data["password"],
                                nom=user_data["nom"],
                                prenom=user_data["prenom"],
                                telephone=user_data["telephone"],
                                adresse=user_data["adresse"]
                            )
                            user.balance = user_data.get("balance", 0.0)
                            user.carte_bancaire = user_data.get("carte_bancaire")
                            
                            # Créer les produits
                            if "products" in user_data:
                                for prod_data in user_data["products"]:
                                    product = Product(
                                        nom=prod_data["nom"],
                                        description=prod_data["description"],
                                        prix=prod_data["prix"],
                                        quantite=prod_data["quantite"],
                                        categorie=prod_data["categorie"],
                                        vendeur=user
                                    )
                                    user.products.append(product)
                        
                        self.users[user_data["email"]] = user

                    # Deuxième passage : restaurer les commandes avec les références correctes
                    for user_data in data.get("users", []):
                        user = self.users[user_data["email"]]
                        
                        if isinstance(user, Client) and "commandes" in user_data:
                            user.commandes = []
                            for cmd_data in user_data["commandes"]:
                                # Recréer les détails de la commande avec les références aux produits
                                details = []
                                for detail_data in cmd_data["details"]:
                                    vendeur = self.users[detail_data["vendeur_email"]]
                                    product = next(
                                        (p for p in vendeur.products if p.id == detail_data["product_id"]),
                                        None
                                    )
                                    if product:
                                        details.append({
                                            'product': product,
                                            'quantity': detail_data["quantity"],
                                            'subtotal': detail_data["subtotal"]
                                        })

                                commande = {
                                    'id': cmd_data['id'],
                                    'date': datetime.strptime(cmd_data['date'], "%Y-%m-%d %H:%M:%S"),
                                    'total': cmd_data['total'],
                                    'status': cmd_data['status'],
                                    'client_email': cmd_data['client_email'],
                                    'client_nom': cmd_data['client_nom'],
                                    'montants_par_marchand': cmd_data['montants_par_marchand'],
                                    'details': details
                                }
                                user.commandes.append(commande)

                        if isinstance(user, Marchand) and "commandes_recues" in user_data:
                            user.commandes_recues = []
                            for cmd_data in user_data["commandes_recues"]:
                                details = []
                                for detail_data in cmd_data["details"]:
                                    vendeur = self.users[detail_data["vendeur_email"]]
                                    product = next(
                                        (p for p in vendeur.products if p.id == detail_data["product_id"]),
                                        None
                                    )
                                    if product:
                                        details.append({
                                            'product': product,
                                            'quantity': detail_data["quantity"],
                                            'subtotal': detail_data["subtotal"]
                                        })

                                commande = {
                                    'id': cmd_data['id'],
                                    'date': datetime.strptime(cmd_data['date'], "%Y-%m-%d %H:%M:%S"),
                                    'total': cmd_data['total'],
                                    'status': cmd_data['status'],
                                    'client_email': cmd_data['client_email'],
                                    'client_nom': cmd_data['client_nom'],
                                    'montants_par_marchand': cmd_data['montants_par_marchand'],
                                    'details': details
                                }
                                user.commandes_recues.append(commande)

                    console.print("[green]Données chargées avec succès")
            except Exception as e:
                console.print(f"[red]Erreur lors du chargement des données: {e}")
                self.users = {}

    def save_data(self):
        try:
            data = {"users": []}
            for user in self.users.values():
                # Déterminer le type d'utilisateur
                if isinstance(user, Admin):
                    user_type = "admin"
                elif isinstance(user, Client):
                    user_type = "client"
                else:
                    user_type = "marchand"
                    
                user_data = {
                    "email": user.email,
                    "password": user.password, 
                    "nom": user.nom,
                    "prenom": user.prenom,
                    "telephone": user.telephone,
                    "adresse": user.adresse,
                    "balance": user.balance,
                    "carte_bancaire": user.carte_bancaire,
                    "type": user_type
                }

                if isinstance(user, Client):
                    # Sauvegarder le panier
                    user_data["panier"] = user.panier
                    
                    # Sauvegarder les commandes avec tous les détails
                    user_data["commandes"] = [{
                        'id': cmd['id'],
                        'date': cmd['date'].strftime("%Y-%m-%d %H:%M:%S"),
                        'total': cmd['total'],
                        'status': cmd['status'],
                        'client_email': cmd['client_email'],
                        'client_nom': cmd['client_nom'],
                        'montants_par_marchand': cmd['montants_par_marchand'],
                        'details': [{
                            'product_id': detail['product'].id,
                            'product_nom': detail['product'].nom,
                            'product_prix': detail['product'].prix,
                            'quantity': detail['quantity'],
                            'subtotal': detail['subtotal'],
                            'vendeur_email': detail['product'].vendeur.email
                        } for detail in cmd['details']]
                    } for cmd in user.commandes]

                elif isinstance(user, Marchand):  # Marchand
                    # Sauvegarder les produits
                    user_data["products"] = [{
                        "nom": p.nom,
                        "description": p.description,
                        "prix": p.prix,
                        "quantite": p.quantite,
                        "categorie": p.categorie,
                    } for p in user.products]
                    
                    # Sauvegarder les commandes reçues
                    user_data["commandes_recues"] = [{
                        'id': cmd['id'],
                        'date': cmd['date'].strftime("%Y-%m-%d %H:%M:%S"),
                        'total': cmd['total'],
                        'status': cmd['status'],
                        'client_email': cmd['client_email'],
                        'client_nom': cmd['client_nom'],
                        'montants_par_marchand': cmd['montants_par_marchand'],
                        'details': [{
                            'product_id': detail['product'].id,
                            'product_nom': detail['product'].nom,
                            'product_prix': detail['product'].prix,
                            'quantity': detail['quantity'],
                            'subtotal': detail['subtotal'],
                            'vendeur_email': detail['product'].vendeur.email
                        } for detail in cmd['details']]
                    } for cmd in getattr(user, 'commandes_recues', [])]

                data["users"].append(user_data)
            
            with open(self.DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4, default=str)
            console.print("[green]Données sauvegardées avec succès")
        except Exception as e:
            console.print(f"[red]Erreur lors de la sauvegarde des données: {e}")
            
        def register_user(self, type_user="client"):
            console.print("[blue]Création de compte")
            email = Prompt.ask("Email")
            if email in self.users:
                console.print("[red]Email déjà utilisé")
                return None
            
            password = Prompt.ask("Mot de passe", password=True)
            hashed_password = hash_password(password)  # Hash le mot de passe
            nom = Prompt.ask("Nom")
            prenom = Prompt.ask("Prénom")
            telephone = Prompt.ask("Téléphone")
            adresse = Prompt.ask("Adresse")

            if type_user == "client":
                user = Client(email, hashed_password, nom, prenom, telephone, adresse)
            elif type_user == "admin":
                user = Admin(email, hashed_password, nom, prenom, telephone, adresse)
            else:
                user = Marchand(email, hashed_password, nom, prenom, telephone, adresse)
            
            self.users[email] = user
            self.save_data()  # Sauvegarder immédiatement après création
            console.print("[green]Compte créé avec succès!")
            return user

    def login(self):
        email = Prompt.ask("Email")
        password = Prompt.ask("Mot de passe", password=True)
        hashed_password = hash_password(password)
        
        if not os.path.exists('data.json'):
            console.print("[red]Aucun utilisateur enregistré")
            return None

        try:
            with open('data.json', 'r') as f:
                data = json.load(f)
                users = data.get("users", [])
                for user_data in users:
                    if user_data["email"] == email and user_data["password"] == hashed_password:
                        # Récupérer l'utilisateur depuis self.users (déjà chargé dans load_data)
                        user = self.users.get(email)
                        if user:
                            self.current_user = user
                            console.print(f"[green]Bienvenue {user.nom}!")
                            return user
        except Exception as e:
            console.print(f"[red]Erreur lors de la connexion: {e}")
        
        console.print("[red]Email ou mot de passe incorrect")
        return None

    def delete_account(self):
        """Supprime le compte de l'utilisateur courant"""
        if not self.current_user:
            console.print("[red]Aucun utilisateur connecté")
            return False
        
        confirmation = Prompt.ask(
            "[red]Êtes-vous sûr de vouloir supprimer votre compte? (oui/non)"
        )
        
        if confirmation.lower() == "oui":
            email = self.current_user.email
            # Demander le mot de passe pour confirmation
            password = Prompt.ask("Entrez votre mot de passe pour confirmer", password=True)
            hashed_password = hash_password(password)
            
            if self.current_user.password == hashed_password:
                # Supprimer l'utilisateur du dictionnaire
                del self.users[email]
                # Sauvegarder les changements
                self.save_data()
                self.current_user = None
                console.print("[green]Compte supprimé avec succès")
                return True
            else:
                console.print("[red]Mot de passe incorrect")
                return False
        
        console.print("[yellow]Suppression annulée")
        return False
    
    def get_product(self, product_id):
        for user in self.users.values():
            if isinstance(user, Marchand):
                for product in user.products:
                    if product.id == product_id:
                        return product
        return None

    def display_products(self):
        table = Table(title="Produits disponibles")
        table.add_column("ID")
        table.add_column("Nom")
        table.add_column("Description")
        table.add_column("Prix")
        table.add_column("Quantité")
        table.add_column("Catégorie")
        table.add_column("Vendeur")

        for user in self.users.values():
            if isinstance(user, Marchand):
                for product in user.products:
                    table.add_row(
                        str(product.id),
                        product.nom,
                        product.description,
                        f"{product.prix}€",
                        str(product.quantite),
                        product.categorie,
                        product.vendeur.nom
                    )
        
        console.print(table)