"""
JWT Key Pair Generator

This script generates RSA key pairs (private/public) for JWT token signing and verification.
The keys are generated in PEM format which is commonly used for JWT algorithms like RS256.

Generated keys should be:
1. Stored securely (private key should never be exposed)
2. Used as environment variables in your application
3. Regenerated periodically for security best practices

Usage:
- Run this script to generate new key pairs
- Copy the output to your environment configuration
- Never commit these keys to version control

Output Format:
- Private key in PKCS#8 PEM format (unencrypted)
- Public key in SubjectPublicKeyInfo PEM format
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate RSA key pair with recommended parameters
private_key = rsa.generate_private_key(
    public_exponent=65537,  # Standard RSA public exponent
    key_size=2048,          # Recommended key size for JWT
)

# Derive public key from private key
public_key = private_key.public_key()

# Serialize private key to PEM format (PKCS#8)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()  # Key is unencrypted
)

# Serialize public key to PEM format (SubjectPublicKeyInfo)
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Output the generated keys with visual separator
print('PRIVATE KEY (JWT_PRIVATE_KEY):')
print(private_pem.decode('utf-8').replace('\n', ''))  # Convert bytes to string for clean output

print('-' * 50)  # Visual separator

print('PUBLIC KEY (JWT_PUBLIC_KEY):')
print(public_pem.decode('utf-8').replace('\n', ''))  # Convert bytes to string for clean output
