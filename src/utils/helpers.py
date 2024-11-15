from rich.console import Console
import hashlib

console = Console()

def hash_password(password: str) -> str:
    """Hash le mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()