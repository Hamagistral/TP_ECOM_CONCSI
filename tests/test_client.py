import pytest
from unittest.mock import patch
from src.models.user import Client, Marchand
from src.models.product import Product
from src.models.store import Store

class TestClient:
    @pytest.fixture
    def marchand(self):
        return Marchand(
            email="marchand@example.com",
            password="password123",
            nom="Test",
            prenom="Marchand",
            telephone="0123456789",
            adresse="123 Marchand Street"
        )

    @pytest.fixture
    def client(self):
        return Client(
            email="client@example.com",
            password="password123",
            nom="Test",
            prenom="Client",
            telephone="0123456789",
            adresse="123 Client Street"
        )

    @pytest.fixture
    def product(self, marchand, store):
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        
        # Ajouter le marchand au store
        store.users[marchand.email] = marchand
        
        # Ajouter le produit au marchand
        marchand.products.append(product)
        
        return product
    
    @pytest.fixture
    def store(self):
        store = Store()
        return store

    def test_panier_validity(self, client, product):
        client.add_to_cart(product, 5)
        assert client.panier[product.id] > 0
        assert product.id in client.panier

    def test_panier_uniqueness(self, client, product):
        client.add_to_cart(product, 3)
        client.add_to_cart(product, 2)
        assert list(client.panier.keys()).count(product.id) == 1
        assert client.panier[product.id] == 5

    def test_commandes_validity(self, client, product, store):
        # S'assurer que le prix du produit est correct
        assert product.prix == 100.0
        
        # Préparer la commande
        client.balance = 1000.0
        client.add_to_cart(product, 2)  # Commander 2 produits à 100€
        
        # Passer la commande
        commande = client.passer_commande(store)
        
        # Vérifier que la commande est créée
        assert commande is not None
        # Vérifier que le total est correct (2 * 100€)
        assert commande['total'] == 200.0
        # Vérifier que toutes les commandes ont un total > 0
        assert all(cmd['total'] > 0 for cmd in client.commandes)

    def test_passer_commande_preconditions(self, client, product, store):
        # Test panier vide
        commande = client.passer_commande(store)
        assert commande is None, "Une commande avec panier vide ne devrait pas être possible"

        # Test balance insuffisante
        client.add_to_cart(product, 1)  # Produit à 100€
        client.balance = 50.0  # Balance insuffisante
        commande = client.passer_commande(store)
        assert commande is None, "Une commande avec balance insuffisante ne devrait pas être possible"

    def test_passer_commande_postconditions(self, client, product, store):
        # Préparer la commande
        client.balance = 1000.0
        initial_balance = client.balance
        client.add_to_cart(product, 1)
        
        # Mémoriser l'état initial
        commandes_count_before = len(client.commandes)
        
        # Passer la commande
        commande = client.passer_commande(store)
        
        # Vérifier les postconditions
        assert len(client.panier) == 0, "Le panier devrait être vide"
        assert len(client.commandes) == commandes_count_before + 1, "Une nouvelle commande devrait être créée"
        assert client.balance == initial_balance - product.prix, "La balance devrait être mise à jour"

    @patch('rich.prompt.Prompt.ask')
    def test_crediter_compte(self, mock_ask, client):
        # Test sans carte bancaire
        initial_balance = client.balance
        result = client.crediter_compte()
        assert result is False, "Le crédit sans carte bancaire devrait échouer"
        assert client.balance == initial_balance, "La balance ne devrait pas changer"

        # Simuler l'ajout d'une carte bancaire
        mock_ask.side_effect = ["4242424242424242", "12/25", "123"]
        client.add_carte_bancaire()
        assert client.carte_bancaire is not None, "La carte devrait être enregistrée"

        # Test crédit avec carte
        mock_ask.side_effect = ["100"]
        initial_balance = client.balance
        result = client.crediter_compte()
        assert result is True, "Le crédit devrait réussir"
        assert client.balance == initial_balance + 100, "La balance devrait être mise à jour"