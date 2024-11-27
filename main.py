from src.models.store import Store
from src.models.user import Client, Marchand, Admin
from src.utils.helpers import console
from rich.prompt import Prompt, Confirm

def main():
    store = Store()
    
    while True:
        if not store.current_user:
            console.print("[green]===== EpicLoot Store =====", style="bold")
            console.print("\n[blue]===== MENU PRINCIPAL =====")
            console.print("1. Se connecter")
            console.print("2. Créer un compte client")
            console.print("3. Créer un compte marchand")
            console.print("4. Quitter")
            
            choice = Prompt.ask("Choix", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                store.login()
            elif choice == "2":
                store.register_user("client")
            elif choice == "3":
                store.register_user("marchand")
            elif choice == "4":
                break
        
        else:
            if isinstance(store.current_user, Client):
                console.print("[green]===== EpicLoot Store =====", style="bold")
                console.print("\n[blue]===== MENU CLIENT =====")
                console.print("1. Voir les produits")
                console.print("2. Voir mon panier")
                console.print("3. Passer commande")
                console.print("4. Voir mes commandes")
                console.print("5. Voir ma balance")
                console.print("6. Ajouter une carte bancaire")
                console.print("7. Créditer mon compte")
                console.print("8. Voir les details d'une commande")
                console.print("9. Supprimer mon compte")
                console.print("10. Se déconnecter")
                
                choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
                
                if choice == "1":
                    store.display_products()
                    if Prompt.ask("Voulez-vous acheter un produit? (o/n)") == "o":
                        prod_id = str(Prompt.ask("ID du produit"))
                        quantity = int(Prompt.ask("Quantité"))
                        product = store.get_product(prod_id)
                        if product:
                            store.current_user.add_to_cart(product, quantity)
                elif choice == "2":
                    store.current_user.view_cart(store)
                    if store.current_user.panier and Prompt.ask("Voulez-vous retirer un produit? (o/n)") == "o":
                        prod_id = str(Prompt.ask("ID du produit à retirer"))
                        store.current_user.remove_from_cart(prod_id)
                elif choice == "3":
                    store.current_user.passer_commande(store)
                elif choice == "4":
                    store.current_user.voir_commandes()
                elif choice == "5":
                    console.print(f"[blue]Balance actuelle: {store.current_user.balance}€")
                elif choice == "6":
                    store.current_user.add_carte_bancaire()
                elif choice == "7":
                    store.current_user.crediter_compte()
                elif choice == "8":
                    store.current_user.voir_details_commande(
                        Prompt.ask("ID de la commande à consulter")
                    )
                elif choice == "9":
                    if store.delete_account():
                        console.print("[yellow]Retour au menu principal...")
                        continue
                elif choice == "10":
                    store.current_user = None

            elif isinstance(store.current_user, Marchand):
                console.print("[green]===== EpicLoot Store =====", style="bold")
                console.print("\n[blue]===== MENU MARCHAND =====")
                console.print("1. Ajouter un produit")
                console.print("2. Voir mes produits")
                console.print("3. Modifier un produit")
                console.print("4. Supprimer un produit")
                console.print("5. Voir les commandes reçues")
                console.print("6. Modifier status commande")
                console.print("7. Gérer les stocks")
                console.print("8. Voir ma balance")
                console.print("9. Ajouter coordonnées bancaires")
                console.print("10. Supprimer mon compte")
                console.print("11. Se déconnecter")
                
                choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])
                
                if choice == "1":
                    nom = Prompt.ask("Nom du produit")
                    description = Prompt.ask("Description")
                    prix = float(Prompt.ask("Prix"))
                    quantite = int(Prompt.ask("Quantité"))
                    categorie = Prompt.ask("Catégorie")
                    store.current_user.add_product(nom, description, prix, quantite, categorie)
                elif choice == "2":
                    store.current_user.view_products()
                elif choice == "3":
                    store.current_user.view_products()
                    product_id = Prompt.ask("ID du produit à modifier")
                    console.print("\nQue voulez-vous modifier?")
                    console.print("1. Nom")
                    console.print("2. Description")
                    console.print("3. Prix")
                    console.print("4. Quantité")
                    console.print("5. Catégorie")
                    
                    mod_choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5"])
                    field_map = {
                        "1": "nom",
                        "2": "description",
                        "3": "prix",
                        "4": "quantite",
                        "5": "categorie"
                    }
                    
                    field = field_map[mod_choice]
                    if field in ["prix", "quantite"]:
                        value = float(Prompt.ask(f"Nouvelle valeur pour {field}"))
                    else:
                        value = Prompt.ask(f"Nouvelle valeur pour {field}")
                        
                    if store.current_user.modify_product(product_id, **{field: value}):
                        store.save_data()
                        
                elif choice == "4":
                    store.current_user.view_products()
                    product_id = Prompt.ask("ID du produit à supprimer")
                    if Confirm.ask("Êtes-vous sûr de vouloir supprimer ce produit?"):
                        if store.current_user.delete_product(product_id):
                            store.save_data()
                elif choice == "5":
                    store.current_user.voir_commandes_recues()
                elif choice == "6":
                    store.current_user.modifier_status_commande(store)
                elif choice == "7":
                    store.current_user.manage_stock()
                elif choice == "8":
                    console.print(f"[blue]Balance actuelle: {store.current_user.balance}€")
                elif choice == "9":
                    store.current_user.add_carte_bancaire()
                elif choice == "10":
                    if store.delete_account():
                        console.print("[yellow]Retour au menu principal...")
                        continue
                elif choice == "11":
                    store.current_user = None
                    
            elif isinstance(store.current_user, Admin):
                console.print("[green]===== EpicLoot Store =====", style="bold")
                console.print("\n[blue]===== MENU ADMINISTRATEUR =====")
                console.print("1. Voir tous les utilisateurs")
                console.print("2. Voir tous les produits")
                console.print("3. Supprimer un utilisateur")
                console.print("4. Supprimer un produit")
                console.print("5. Voir l'historique des transactions")
                console.print("6. Générer des statistiques")
                console.print("7. Se déconnecter")
                
                choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
                
                if choice == "1":
                    store.current_user.view_all_users(store)
                elif choice == "2":
                    store.current_user.view_all_products(store)
                elif choice == "3":
                    store.current_user.delete_user(store)
                elif choice == "4":
                    store.current_user.delete_product(store)
                elif choice == "5":
                    store.current_user.view_all_transactions(store)
                elif choice == "6":
                    store.current_user.generate_stats(store)
                elif choice == "7":
                    store.current_user = None

    store.save_data()
    console.print("[green]Au revoir!")

if __name__ == "__main__":
    main()