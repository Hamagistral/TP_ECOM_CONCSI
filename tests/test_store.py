import pytest
from pathlib import Path
from unittest.mock import patch
from src.models.user import Client, Marchand, Admin
from src.models.store import Store

class TestStore:
    @pytest.fixture
    def store(self):
        # S'assurer que le dossier data existe
        store = Store()
        store.DATA_DIR.mkdir(exist_ok=True)
        return store

    @pytest.fixture
    def mock_input_values(self):
        return {
            "email": "test@example.com",
            "password": "password123",
            "nom": "Test",
            "prenom": "User",
            "telephone": "0123456789",
            "adresse": "123 Test Street"
        }

    def test_store_initialization(self, store):
        """Test l'initialisation du Store"""
        assert store.current_user is None
        assert store.DATA_DIR.exists()

    def test_duplicate_email(self, store):
        """Test la tentative d'enregistrement avec un email existant"""
        # Premier enregistrement
        store.register_user(
            type_user="client",
            email="test@test.com",
            password="password123",
            nom="Test",
            prenom="User",
            telephone="0123456789",
            adresse="123 Test Street"
        )
        
        # Deuxième tentative avec le même email
        result = store.register_user(
            type_user="client",
            email="test@test.com",
            password="password123",
            nom="Test2",
            prenom="User2",
            telephone="9876543210",
            adresse="456 Test Street"
        )
        
        assert result is None

    @patch('rich.prompt.Prompt.ask')
    def test_duplicate_email(self, mock_ask, store, mock_input_values):
        """Test la tentative d'enregistrement avec un email existant"""
        # Premier enregistrement
        mock_ask.side_effect = list(mock_input_values.values())
        store.register_user(type_user="client")
        
        # Deuxième tentative avec le même email
        mock_ask.side_effect = list(mock_input_values.values())
        result = store.register_user(type_user="client")
        
        assert result is None

    @patch('rich.prompt.Prompt.ask')
    def test_login_success(self, mock_ask, store, mock_input_values):
        """Test la connexion réussie"""
        # Créer un utilisateur
        mock_ask.side_effect = list(mock_input_values.values())
        store.register_user(type_user="client")
        
        # Tentative de connexion
        mock_ask.side_effect = [mock_input_values["email"], mock_input_values["password"]]
        user = store.login()
        
        assert user is not None
        assert store.current_user is not None
        assert store.current_user.email == mock_input_values["email"]

    @patch('rich.prompt.Prompt.ask')
    def test_login_failure(self, mock_ask, store, mock_input_values):
        """Test la connexion échouée"""
        # Créer un utilisateur
        mock_ask.side_effect = list(mock_input_values.values())
        store.register_user(type_user="client")
        
        # Tentative de connexion avec mauvais mot de passe
        mock_ask.side_effect = [mock_input_values["email"], "wrongpassword"]
        user = store.login()
        
        assert user is None
        assert store.current_user is None

    @patch('rich.prompt.Prompt.ask')
    def test_delete_account(self, mock_ask, store, mock_input_values):
        """Test la suppression de compte"""
        # Créer et connecter un utilisateur
        mock_ask.side_effect = list(mock_input_values.values())
        store.register_user(type_user="client")
        mock_ask.side_effect = [mock_input_values["email"], mock_input_values["password"]]
        store.login()
        
        # Supprimer le compte
        mock_ask.side_effect = ["oui", mock_input_values["password"]]
        result = store.delete_account()
        
        assert result is True
        assert mock_input_values["email"] not in store.users
        assert store.current_user is None

    def test_get_user_by_email(self, store, mock_input_values):
        """Test la récupération d'un utilisateur par email"""
        with patch('rich.prompt.Prompt.ask') as mock_ask:
            mock_ask.side_effect = list(mock_input_values.values())
            user = store.register_user(type_user="client")
            
            retrieved_user = store.get_user_by_email(mock_input_values["email"])
            assert retrieved_user == user

    def test_data_persistence(self, store, mock_input_values):
        """Test la persistance des données"""
        # Créer un utilisateur
        with patch('rich.prompt.Prompt.ask') as mock_ask:
            mock_ask.side_effect = list(mock_input_values.values())
            store.register_user(type_user="client")
        
        # Créer un nouveau store pour recharger les données
        new_store = Store()
        assert mock_input_values["email"] in new_store.users
        loaded_user = new_store.users[mock_input_values["email"]]
        assert loaded_user.nom == mock_input_values["nom"]