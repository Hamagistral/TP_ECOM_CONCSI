import pytest
from unittest.mock import patch
from src.models.user import Marchand, Client
from src.models.product import Product
from src.models.store import Store

class TestMarchand:
    @pytest.fixture
    def store(self):
        return Store()

    @pytest.fixture
    def marchand(self, store):
        marchand = Marchand(
            email="marchand@example.com",
            password="password123",
            nom="Test",
            prenom="Marchand",
            telephone="0123456789",
            adresse="123 Marchand Street"
        )
        store.users[marchand.email] = marchand
        return marchand

    @pytest.fixture
    def client(self, store):
        client = Client(
            email="client@example.com",
            password="password123",
            nom="Test",
            prenom="Client",
            telephone="0123456789",
            adresse="123 Client Street"
        )
        store.users[client.email] = client
        return client

    def test_unique_products(self, marchand):
        """Test inv uniqueProducts: self.products->isUnique(id)"""
        # Ajouter un premier produit
        product1 = marchand.add_product(
            name="Test Product 1",
            description="Description 1",
            price=100.0,
            quantity=10,
            categorie="Headphones"
        )

        # Ajouter un deuxième produit similaire
        product2 = marchand.add_product(
            name="Test Product 2",
            description="Description 2",
            price=150.0,
            quantity=5,
            categorie="Laptop"
        )

        # Vérifier que les IDs sont uniques
        product_ids = [p.id for p in marchand.products]
        assert len(product_ids) == len(set(product_ids)), "Les IDs des produits doivent être uniques"

    def test_valid_products(self, marchand):
        """Test inv validProducts: self.products->forAll(p | p.prix > 0 and p.quantite >= 0)"""
        # Ajouter un produit valide
        product = marchand.add_product(
            name="Test Product",
            description="Description",
            price=100.0,
            quantity=10,
            categorie="Test"
        )

        # Vérifier les contraintes
        assert product.prix > 0, "Le prix doit être positif"
        assert product.quantite >= 0, "La quantité doit être positive ou nulle"

        # Vérifier pour tous les produits
        assert all(p.prix > 0 and p.quantite >= 0 for p in marchand.products), \
            "Tous les produits doivent avoir un prix positif et une quantité non négative"

    def test_add_product_preconditions(self, marchand):
        """Test les préconditions de add_product"""
        # Test nom non vide
        product = marchand.add_product(
            name="Test Product",
            description="Description",
            price=100.0,
            quantity=10,
            categorie="Test"
        )
        assert product.nom != "", "Le nom ne peut pas être vide"

        # Test prix positif
        assert product.prix > 0, "Le prix doit être positif"

        # Test quantité non négative
        assert product.quantite >= 0, "La quantité ne peut pas être négative"

        # Test catégorie non vide
        assert product.categorie != "", "La catégorie ne peut pas être vide"

    def test_add_product_postconditions(self, marchand):
        """Test les postconditions de add_product"""
        initial_count = len(marchand.products)
        
        product = marchand.add_product(
            name="Test Product",
            description="Description",
            price=100.0,
            quantity=10,
            categorie="Test"
        )

        # Vérifier que le produit a été ajouté
        assert len(marchand.products) == initial_count + 1, "Le nombre de produits doit augmenter de 1"
        
        # Vérifier que le produit existe avec les bonnes valeurs
        assert any(p.nom == "Test Product" and p.prix == 100.0 for p in marchand.products), \
            "Le produit doit exister avec les valeurs spécifiées"

    def test_modifier_status_commande_preconditions(self, marchand, client, store):
        """Test les préconditions de modifier_status_commande"""
        # Vérifier qu'on ne peut pas modifier sans commandes
        assert len(marchand.commandes_recues) == 0, "Il ne devrait pas y avoir de commandes au début"

        # Créer une commande
        product = marchand.add_product(
            name="Test Product",
            description="Description",
            price=100.0,
            quantity=10,
            categorie="Test"
        )
        
        client.balance = 1000.0
        client.add_to_cart(product, 1)
        client.passer_commande(store)

        # Vérifier que la commande existe maintenant
        assert len(marchand.commandes_recues) > 0, "Il devrait y avoir une commande"
        
        # Vérifier que le status est valide
        commande = marchand.commandes_recues[0]
        assert commande['status'] in ['en_attente', 'confirmé', 'livré', 'annulé'], \
            "Le status doit être valide"

    def test_annulation_commande(self, marchand, client, store):
        """Test l'annulation d'une commande"""
        # Créer et ajouter un produit
        product = marchand.add_product(
            name="Test Product",
            description="Description",
            price=100.0,
            quantity=10,
            categorie="Test"
        )
        
        # Client passe une commande
        client.balance = 1000.0
        client.add_to_cart(product, 1)
        client.passer_commande(store)

        # Vérifier les balances avant annulation
        marchand_balance_before = marchand.balance
        client_balance_before = client.balance

        # Simuler l'annulation de la commande
        commande = marchand.commandes_recues[0]
        assert marchand.balance >= commande['total'], \
            "Le marchand doit avoir assez d'argent pour rembourser"