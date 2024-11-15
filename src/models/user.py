from datetime import datetime
from typing import Dict, List, Optional
from rich.table import Table
from rich.prompt import Prompt

from ..utils.helpers import console
from .product import Product

class User:
    def __init__(self, email: str, password: str, nom: str, prenom: str, telephone: str, adresse: str):
        self.email = email
        self.password = password
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.adresse = adresse
        self.balance = 0.0
        self.carte_bancaire = None
        self.dateCreation = datetime.now()
        
    def add_carte_bancaire(self):
        console.print("[blue]Ajout d'une carte bancaire")
        numero = Prompt.ask("Numéro de carte")
        date_exp = Prompt.ask("Date d'expiration (MM/YY)")
        cvv = Prompt.ask("CVV", password=True)
        self.carte_bancaire = {
            "numero": numero[-4:],  # Garder uniquement les 4 derniers chiffres
            "date_exp": date_exp
        }
        console.print("[green]Carte bancaire ajoutée avec succès")

    def crediter_compte(self):
        if not self.carte_bancaire:
            console.print("[red]Veuillez d'abord ajouter une carte bancaire")
            return False
        
        montant = float(Prompt.ask("Montant à créditer"))
        if montant <= 0:
            console.print("[red]Le montant doit être positif")
            return False

        # Simulation de paiement
        console.print(f"[blue]Débit de {montant}€ sur la carte **** **** **** {self.carte_bancaire['numero']}")
        self.balance += montant
        console.print(f"[green]Compte crédité de {montant}€. Nouveau solde: {self.balance}€")
        return True

class Client(User):
    def __init__(self, email: str, password: str, nom: str, prenom: str, telephone: str, adresse: str):
        super().__init__(email, password, nom, prenom, telephone, adresse)
        self.panier = {}  # product_id: quantity
        self.commandes = [] # Liste des commandes

    def add_to_cart(self, product, quantity):
        if product.quantite >= quantity:
            if product.id in self.panier:
                self.panier[product.id] += quantity
            else:
                self.panier[product.id] = quantity
            console.print(f"[green]Ajouté au panier: {quantity} x {product.nom}")
        else:
            console.print("[red]Stock insuffisant")

    def remove_from_cart(self, product_id):
        if product_id in self.panier:
            del self.panier[product_id]
            console.print("[green]Produit retiré du panier")

    def view_cart(self, store):
        if not self.panier:
            console.print("[yellow]Votre panier est vide")
            return
        
        table = Table(title="Votre Panier")
        table.add_column("ID")
        table.add_column("Produit")
        table.add_column("Quantité")
        table.add_column("Prix unitaire")
        table.add_column("Total")
        
        total = 0
        for prod_id, quantity in self.panier.items():
            product = store.get_product(prod_id)
            if product:
                subtotal = product.prix * quantity
                total += subtotal
                table.add_row(
                    str(product.id),
                    product.nom,
                    str(quantity),
                    f"{product.prix}€",
                    f"{subtotal}€"
                )
        
        console.print(table)
        console.print(f"[blue]Total: {total}€")

    def passer_commande(self, store):
        if not self.panier:
            console.print("[yellow]Votre panier est vide")
            return

        # Calculer le total et organiser par marchand
        total = 0
        commande_details = []
        montants_par_marchand = {}  # Pour tracker les montants par marchand

        for prod_id, quantity in self.panier.items():
            product = store.get_product(prod_id)
            if product:
                subtotal = product.prix * quantity
                total += subtotal
                commande_details.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                # Calculer le montant pour chaque marchand
                if product.vendeur.email not in montants_par_marchand:
                    montants_par_marchand[product.vendeur.email] = 0
                montants_par_marchand[product.vendeur.email] += subtotal

        if total > self.balance:
            console.print(f"[red]Solde insuffisant. Total: {total}€, Balance: {self.balance}€")
            return

        # Créer la commande
        commande = {
            'id': f"CMD{len(self.commandes) + 1}",
            'date': datetime.now(),
            'details': commande_details,
            'total': total,
            'status': 'en_attente',
            'client_email': self.email,
            'client_nom': f"{self.prenom} {self.nom}",
            'montants_par_marchand': montants_par_marchand  # Ajouter les montants par marchand
        }

        # Vérifier les stocks et mettre à jour
        for detail in commande_details:
            product = detail['product']
            quantity = detail['quantity']
            if product.quantite >= quantity:
                product.quantite -= quantity
            else:
                console.print(f"[red]Stock insuffisant pour {product.nom}")
                return

        # Débiter le client
        self.balance -= total
        console.print(f"[yellow]Votre compte a été débité de {total}€")
        console.print(f"[blue]Nouvelle balance: {self.balance}€")

        # Créditer chaque marchand immédiatement
        for marchand_email, montant in montants_par_marchand.items():
            marchand = store.get_user_by_email(marchand_email)
            if marchand:
                marchand.balance += montant
                console.print(f"[green]Marchand {marchand.nom} crédité de {montant}€")

        # Ajouter la commande aux commandes du client
        self.commandes.append(commande)
        
        # Ajouter la commande aux commandes reçues des marchands
        for detail in commande_details:
            marchand = detail['product'].vendeur
            if not hasattr(marchand, 'commandes_recues'):
                marchand.commandes_recues = []
            marchand.commandes_recues.append(commande)

        self.panier.clear()
        console.print("[green]Commande passée avec succès!")
        console.print(f"[blue]Commande N°{commande['id']} - Total: {total}€")
        return commande

    def voir_commandes(self):
        if not self.commandes:
            console.print("[yellow]Vous n'avez pas de commandes")
            return

        table = Table(title="Vos Commandes")
        table.add_column("ID")
        table.add_column("Date")
        table.add_column("Total")
        table.add_column("Status")
        
        for cmd in self.commandes:
            table.add_row(
                cmd['id'],
                datetime.strptime(cmd['date'], '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M"),
                f"{cmd['total']}€",
                cmd['status']
            )
        
        console.print(table)

class Marchand(User):
    def __init__(self, email: str, password: str, nom: str, prenom: str, telephone: str, adresse: str):
        super().__init__(email, password, nom, prenom, telephone, adresse)
        self.products = []
        self.commandes_recues = []  

    def add_product(self, name: str, description: str, price: float, quantity: int, categorie: str):
        product = Product(
            nom=name,
            description=description,
            prix=price,
            quantite=quantity,
            categorie=categorie,
            vendeur=self
        )
        self.products.append(product)
        console.print(f"[green]Produit ajouté: {product.nom}")
        return product

    def view_products(self):
        if not self.products:
            console.print("[yellow]Vous n'avez pas de produits")
            return

        table = Table(title="Vos Produits")
        table.add_column("ID")
        table.add_column("Nom")
        table.add_column("Description")
        table.add_column("Prix")
        table.add_column("Quantité")
        table.add_column("Catégorie")
        
        for product in self.products:
            table.add_row(
                str(product.id),
                product.nom,
                product.description,
                f"{product.prix}€",
                str(product.quantite),
                product.categorie
            )
        
        console.print(table)
        
    def voir_commandes_recues(self):
        if not self.commandes_recues:
            console.print("[yellow]Vous n'avez pas de commandes reçues")
            return

        table = Table(title="Commandes Reçues")
        table.add_column("ID")
        table.add_column("Client")
        table.add_column("Date")
        table.add_column("Produits")
        table.add_column("Total")
        table.add_column("Status")
        
        for cmd in self.commandes_recues:
            produits = []
            total_marchand = 0
            for detail in cmd['details']:
                if detail['product'].vendeur.email == self.email:
                    produits.append(f"{detail['quantity']}x {detail['product'].nom}")
                    total_marchand += detail['subtotal']
            
            if produits:  # N'afficher que si le marchand a des produits dans la commande
                table.add_row(
                    cmd['id'],
                    cmd['client_nom'],  # Utilisation du nom complet du client
                    cmd['date'].strftime("%Y-%m-%d %H:%M:%S"),
                    "\n".join(produits),
                    f"{total_marchand}€",
                    cmd['status']
                )
        
        console.print(table)
        console.print(f"[blue]Balance actuelle: {self.balance}€")
        
    def modifier_status_commande(self, store):
        self.voir_commandes_recues()
        if not self.commandes_recues:
            return

        cmd_id = Prompt.ask("ID de la commande à modifier")
        commande = next((cmd for cmd in self.commandes_recues if cmd['id'] == cmd_id), None)
        if not commande:
            console.print("[red]Commande non trouvée")
            return

        status_options = {
            "1": "confirmé",
            "2": "livré",
            "3": "annulé"
        }
        
        console.print("\nChoisir le nouveau status:")
        for key, value in status_options.items():
            console.print(f"{key}. {value}")

        choice = Prompt.ask("Choix", choices=list(status_options.keys()))
        nouveau_status = status_options[choice]
        ancien_status = commande['status']
        
        # Si on annule la commande
        if nouveau_status == "annulé" and ancien_status != "annulé":
            # Récupérer le montant spécifique à ce marchand
            montant_marchand = commande['montants_par_marchand'].get(self.email, 0)
            
            # Vérifier si le marchand a assez d'argent pour le remboursement
            if self.balance < montant_marchand:
                console.print(f"[red]Balance insuffisante pour effectuer le remboursement ({montant_marchand}€)")
                return
            
            # Rembourser le client
            client = store.get_user_by_email(commande['client_email'])
            if client:
                # Débiter le marchand
                self.balance -= montant_marchand
                # Créditer le client
                client.balance += montant_marchand
                
                console.print(f"[yellow]Remboursement effectué:")
                console.print(f"[red]Votre compte a été débité de {montant_marchand}€")
                console.print(f"[green]Client {client.nom} remboursé de {montant_marchand}€")
                console.print(f"[blue]Votre nouvelle balance: {self.balance}€")
                
                # Restaurer les stocks
                for detail in commande['details']:
                    if detail['product'].vendeur.email == self.email:
                        detail['product'].quantite += detail['quantity']
                        console.print(f"[blue]Stock restauré pour {detail['product'].nom}: +{detail['quantity']}")

        commande['status'] = nouveau_status
        console.print(f"[green]Status modifié: {nouveau_status}")
        
    def manage_stock(self):
        if not self.products:
            console.print("[yellow]Vous n'avez pas de produits")
            return

        # Afficher les produits actuels
        table = Table(title="Vos Produits")
        table.add_column("ID")
        table.add_column("Nom")
        table.add_column("Prix")
        table.add_column("Stock Actuel")
        table.add_column("Catégorie")
        
        for product in self.products:
            table.add_row(
                str(product.id),
                product.nom,
                f"{product.prix}€",
                str(product.quantite),
                product.categorie
            )
        
        console.print(table)

        # Sélectionner le produit à modifier
        prod_id = Prompt.ask("ID du produit à modifier")
        product = next((p for p in self.products if p.id == prod_id), None)
        
        if not product:
            console.print("[red]Produit non trouvé")
            return

        console.print(f"\n[blue]Gestion du stock pour : {product.nom}")
        console.print(f"Stock actuel : {product.quantite}")
        console.print("\n1. Ajouter du stock")
        console.print("2. Réduire le stock")
        
        choice = Prompt.ask("Choix", choices=["1", "2"])
        
        try:
            if choice == "1":
                quantite = int(Prompt.ask("Quantité à ajouter"))
                if quantite > 0:
                    product.quantite += quantite
                    console.print(f"[green]Stock ajouté avec succès. Nouveau stock: {product.quantite}")
                else:
                    console.print("[red]La quantité doit être positive")
            else:
                quantite = int(Prompt.ask("Quantité à retirer"))
                if quantite > 0:
                    if quantite <= product.quantite:
                        product.quantite -= quantite
                        console.print(f"[green]Stock retiré avec succès. Nouveau stock: {product.quantite}")
                    else:
                        console.print("[red]Stock insuffisant pour cette opération")
                else:
                    console.print("[red]La quantité doit être positive")
        except ValueError:
            console.print("[red]Veuillez entrer un nombre valide")

class Admin(User):
    def __init__(self, email: str, password: str, nom: str, prenom: str, telephone: str, adresse: str):
        super().__init__(email, password, nom, prenom, telephone, adresse)

    def view_all_users(self, store):
        """Afficher tous les utilisateurs"""
        table = Table(title="Liste des Utilisateurs")
        table.add_column("Type")
        table.add_column("Email")
        table.add_column("Nom")
        table.add_column("Prénom")
        table.add_column("Téléphone")
        table.add_column("Balance")
        table.add_column("Date Création")
        
        for user in store.users.values():
            if not isinstance(user, Admin):  # Ne pas afficher les admins
                user_type = "Client" if isinstance(user, Client) else "Marchand"
                table.add_row(
                    user_type,
                    user.email,
                    user.nom,
                    user.prenom,
                    user.telephone,
                    f"{user.balance}€",
                    user.dateCreation.strftime("%Y-%m-%d %H:%M")
                )
        
        console.print(table)

    def view_all_products(self, store):
        """Afficher tous les produits de tous les marchands"""
        table = Table(title="Liste des Produits")
        table.add_column("ID")
        table.add_column("Nom")
        table.add_column("Prix")
        table.add_column("Stock")
        table.add_column("Catégorie")
        table.add_column("Vendeur")
        
        for user in store.users.values():
            if isinstance(user, Marchand):
                for product in user.products:
                    table.add_row(
                        str(product.id),
                        product.nom,
                        f"{product.prix}€",
                        str(product.quantite),
                        product.categorie,
                        user.nom
                    )
        
        console.print(table)

    def delete_user(self, store):
        """Supprimer un compte utilisateur"""
        self.view_all_users(store)
        email = Prompt.ask("Email de l'utilisateur à supprimer")
        
        if email in store.users:
            user = store.users[email]
            if isinstance(user, Admin):
                console.print("[red]Impossible de supprimer un compte administrateur")
                return
            
            confirmation = Prompt.ask(
                f"[red]Êtes-vous sûr de vouloir supprimer le compte de {user.nom} ({email})? (oui/non)"
            )
            
            if confirmation.lower() == "oui":
                del store.users[email]
                store.save_data()
                console.print("[green]Compte supprimé avec succès")
        else:
            console.print("[red]Utilisateur non trouvé")

    def delete_product(self, store):
        """Supprimer un produit"""
        self.view_all_products()
        prod_id = Prompt.ask("ID du produit à supprimer")
        
        for user in store.users.values():
            if isinstance(user, Marchand):
                for product in user.products[:]:  # Copie de la liste pour éviter les problèmes de modification pendant l'itération
                    if product.id == prod_id:
                        confirmation = Prompt.ask(
                            f"[red]Êtes-vous sûr de vouloir supprimer le produit {product.nom}? (oui/non)"
                        )
                        if confirmation.lower() == "oui":
                            user.products.remove(product)
                            store.save_data()
                            console.print("[green]Produit supprimé avec succès")
                            return
        
        console.print("[red]Produit non trouvé")

    def view_all_transactions(self, store):
        """Voir toutes les transactions (commandes)"""
        table = Table(title="Historique des Transactions")
        table.add_column("ID Commande")
        table.add_column("Client")
        table.add_column("Date")
        table.add_column("Montant")
        table.add_column("Status")
        table.add_column("Marchand(s)")
        
        for user in store.users.values():
            if isinstance(user, Client):
                for cmd in user.commandes:
                    marchands = ", ".join([
                        store.users[email].nom 
                        for email in cmd['montants_par_marchand'].keys()
                    ])
                    table.add_row(
                        cmd['id'],
                        user.nom,
                        cmd['date'].strftime("%Y-%m-%d %H:%M"),
                        f"{cmd['total']}€",
                        cmd['status'],
                        marchands
                    )
        
        console.print(table)

    def generate_stats(self, store):
        """Générer des statistiques"""
        # Statistiques générales
        nb_clients = sum(1 for u in store.users.values() if isinstance(u, Client))
        nb_marchands = sum(1 for u in store.users.values() if isinstance(u, Marchand))
        nb_produits = sum(
            len(u.products) 
            for u in store.users.values() 
            if isinstance(u, Marchand)
        )
        
        # Statistiques des commandes
        total_ventes = 0
        commandes_par_status = {}
        for user in store.users.values():
            if isinstance(user, Client):
                for cmd in user.commandes:
                    total_ventes += cmd['total']
                    status = cmd['status']
                    commandes_par_status[status] = commandes_par_status.get(status, 0) + 1

        console.print("\n[blue]=== Statistiques Générales ===")
        console.print(f"Nombre de clients: {nb_clients}")
        console.print(f"Nombre de marchands: {nb_marchands}")
        console.print(f"Nombre total de produits: {nb_produits}")
        console.print(f"Total des ventes: {total_ventes}€")
        
        console.print("\n[blue]=== Status des Commandes ===")
        for status, count in commandes_par_status.items():
            console.print(f"{status}: {count}")