from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import Marchand

class Product:
    def __init__(self, nom: str, description: str, prix: float, quantite: int, categorie: str, vendeur: 'Marchand'):
        self.nom = nom
        self.description = description
        self.prix = prix
        self.quantite = quantite
        self.categorie = categorie
        self.vendeur = vendeur
        self.id = self.generate_id()
        
    def generate_id(self) -> str:
        """Génère un ID unique basé sur le nom du produit, la catégorie et le vendeur"""
        nom_part = self.nom[:3].upper()
        categorie_part = self.categorie[:2].upper()
        vendeur_part = self.vendeur.nom[:2].upper()
        
        return f"{nom_part}{categorie_part}{vendeur_part}"