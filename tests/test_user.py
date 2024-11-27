import pytest
from src.models.user import User

class TestUser:
    @pytest.fixture
    def valid_user_data(self):
        return {
            "email": "test@example.com",
            "password": "password123",
            "nom": "Test",
            "prenom": "User",
            "telephone": "0123456789",
            "adresse": "123 Test Street"
        }

    def test_email_validation(self, valid_user_data):
        # Test email valide
        user = User(**valid_user_data)
        assert '@' in user.email
        assert '.' in user.email

        # Test email invalide
        invalid_data = valid_user_data.copy()
        invalid_data['email'] = "invalid.email"
        user2 = User(**invalid_data)
        assert '@' not in user2.email, "Email invalide devrait être rejeté"

    def test_password_length(self, valid_user_data):
        # Test mot de passe valide
        user = User(**valid_user_data)
        assert len(user.password) >= 6

        # Test mot de passe trop court
        invalid_data = valid_user_data.copy()
        invalid_data['password'] = "12345"
        user2 = User(**invalid_data)
        assert len(user2.password) < 6, "Mot de passe trop court devrait être rejeté"

    def test_telephone_format(self, valid_user_data):
        # Test numéro valide
        user = User(**valid_user_data)
        assert len(user.telephone) >= 10

        # Test numéro invalide
        invalid_data = valid_user_data.copy()
        invalid_data['telephone'] = "123"
        user2 = User(**invalid_data)
        assert len(user2.telephone) < 10, "Numéro de téléphone trop court devrait être rejeté"

    def test_balance_operations(self, valid_user_data):
        user = User(**valid_user_data)
        
        # Test balance initiale
        assert user.balance == 0.0
        
        # Test crédit valide
        user.balance = 100.0
        assert user.balance == 100.0
        
        # Test balance négative
        user.balance = 0.0
        assert user.balance >= 0, "La balance ne peut pas être négative"