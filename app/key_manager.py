"""
Key Generation
This program handles RSA key pair generation
"""

import datetime
from cryptography.hazmat.primitives.asymmetric import rsa

KEYS = {}


# Generate RSA key pair and store in KEYS
def generate_rsa_key_pair(kid, expiry_minutes=5):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    expiry_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=expiry_minutes
    )

    # Return dictionary of private key, public key and expiry.
    KEYS[kid] = {
        'private_key': private_key,
        'public_key': private_key.public_key(),
        'expiry': expiry_time
    }

    return KEYS[kid]


# Generate an expired key for tests
generate_rsa_key_pair('expired_key', expiry_minutes=-10)
