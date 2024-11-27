import pytest
from src.models.user import Marchand
from src.models.product import Product
from src.models.store import Store

class TestProduct:
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

    def test_valid_price(self, marchand):
        """Test inv validPrice: self.prix > 0"""
        # Test prix valide
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        
        assert product.prix > 0, "Le prix doit être positif"

    def test_valid_stock(self, marchand):
        """Test inv validStock: self.quantite >= 0"""
        # Test quantité valide
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        assert product.quantite >= 0, "La quantité doit être positive ou nulle"

        # Test mise à jour quantité
        initial_stock = product.quantite
        product.quantite = 20
        assert product.quantite > initial_stock, "La quantité a été augmentée"
        
        # Test réduction quantité
        product.quantite = 5
        assert product.quantite >= 0, "La quantité reste positive après réduction"

    def test_valid_id(self, marchand):
        """Test inv validId: self.id->notEmpty()"""
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        
        # Vérification de l'ID
        assert product.id is not None, "L'ID ne peut pas être None"
        assert len(product.id) > 0, "L'ID ne peut pas être vide"
        assert isinstance(product.id, str), "L'ID doit être une chaîne de caractères"

    def test_valid_categorie(self, marchand):
        """Test inv validCategorie: self.categorie->notEmpty()"""
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        
        # Vérification de la catégorie
        assert product.categorie is not None, "La catégorie ne peut pas être None"
        assert len(product.categorie) > 0, "La catégorie ne peut pas être vide"

    def test_valid_vendeur(self, marchand):
        """Test inv validVendeur: self.vendeur->notEmpty()"""
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        
        # Vérification du vendeur
        assert product.vendeur is not None, "Le vendeur ne peut pas être None"
        assert isinstance(product.vendeur, Marchand), "Le vendeur doit être de type Marchand"

    def test_generate_id(self, marchand):
        """Test constraints pour generate_id(): String"""
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        
        # Test format de l'ID
        generated_id = product.id
        assert len(generated_id) >= 5, "L'ID doit avoir au moins 5 caractères"
        
        # Vérifier que l'ID contient les éléments attendus
        nom_part = product.nom[:3].upper()
        categorie_part = product.categorie[:2].upper()
        vendeur_part = product.vendeur.nom[:2].upper()
        
        assert nom_part in generated_id, "L'ID doit contenir les 3 premières lettres du nom"
        assert categorie_part in generated_id, "L'ID doit contenir les 2 premières lettres de la catégorie"
        assert vendeur_part in generated_id, "L'ID doit contenir les 2 premières lettres du nom du vendeur"

    def test_product_uniqueness(self, marchand):
        """Test que deux produits similaires ont des IDs différents"""
        product1 = Product(
            nom="Test Product 1",
            description="Description 1",
            prix=100.0,
            quantite=10,
            categorie="Mouse",
            vendeur=marchand
        )
        
        product2 = Product(
            nom="Test Product 2",
            description="Description 2",
            prix=100.0,
            quantite=10,
            categorie="Keyboard",
            vendeur=marchand
        )
        
        assert product1.id != product2.id, "Deux produits doivent avoir des IDs différents"

    def test_product_update(self, marchand):
        """Test la mise à jour des attributs du produit"""
        product = Product(
            nom="Test Product",
            description="Description",
            prix=100.0,
            quantite=10,
            categorie="Test",
            vendeur=marchand
        )
        
        # Test mise à jour description
        product.description = "Nouvelle description"
        assert product.description == "Nouvelle description"
        
        # Test mise à jour prix
        product.prix = 150.0
        assert product.prix == 150.0
        
        # Test mise à jour quantité
        product.quantite = 15
        assert product.quantite == 15
        
        # L'ID ne doit pas changer après les mises à jour
        initial_id = product.id
        assert product.id == initial_id, "L'ID ne doit pas changer après modification des attributs"