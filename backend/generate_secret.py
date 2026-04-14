#!/usr/bin/env python
"""
Generador de SECRET_KEY segura para Django.
Ejecutar: python generate_secret.py
"""
import secrets
import string

def generate_secret_key():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Remover caracteres problemáticos
    for char in ['\\', '\'', '"', '`']:
        alphabet = alphabet.replace(char, '')
    
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(50))
    return secret_key

if __name__ == '__main__':
    secret = generate_secret_key()
    print("=" * 60)
    print("SECRET_KEY generada para Django:")
    print("=" * 60)
    print(f"DJANGO_SECRET_KEY={secret}")
    print("=" * 60)
    print("\nCopia esta línea y pégala en tus variables de entorno.")
    print("Ejemplo para Railway: DJANGO_SECRET_KEY=" + secret)
    print("=" * 60)