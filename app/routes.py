"""
This Program handles JWKS endpoint and authentication endpoint.
"""

from flask import jsonify, request, make_response
import jwt
import datetime
import uuid
import base64
from app.key_manager import generate_rsa_key_pair, KEYS


# Convert an integer to base64url format without padding.
def base64url_uint(value):
    byte_length = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(
        value.to_bytes(byte_length, 'big')
    ).rstrip(b'=').decode('utf-8')


def register_routes(app):
    """Register routes for JWKS and endpoints.
    Args:
        app(Flask): Flask app instance
    """
    @app.route('/.well-known/jwks.json', methods=['GET'])
    def jwks():
        """
        JWKS Endpoint:
        Return unexpired public keys in JWKS format.
        """
        keys = []
        for kid, key_data in KEYS.items():
            now = datetime.datetime.now(datetime.UTC)
            if key_data['expiry'] > now:
                public_numbers = key_data['public_key'].public_numbers()
                jwk = {
                    'kid': kid,
                    'kty': 'RSA',
                    'alg': 'RS256',
                    'use': 'sig',
                    'n': base64url_uint(public_numbers.n),
                    'e': base64url_uint(public_numbers.e),
                }
                keys.append(jwk)
        return jsonify({'keys': keys})

    @app.route(
        '/.well-known/jwks.json',
        methods=['POST', 'PUT', 'DELETE', 'PATCH']
    )
    def jwks_invalid():
        """Handles invalid methods for JWKS endpoint."""
        return make_response(
            jsonify({'message': 'Method Not Allowed'}), 405
        )

    @app.route('/auth', methods=['POST'])
    def auth():
        """
        Return a signed JWT using an unexpired key and expired key
        """
        username = 'mock_user'  # Always mock the username, no input needed

        expired = request.args.get('expired') is not None
        now = datetime.datetime.now(datetime.UTC)

        if expired:
            expired_kid = next(
                (k for k, v in KEYS.items() if v['expiry'] < now),
                None
            )

            if not expired_kid:
                return make_response(
                    jsonify({'message': 'No expired keys available'}),
                    400
                )

            kid = expired_kid
        else:
            kid = next(
                (k for k, v in KEYS.items() if v['expiry'] > now),
                None
            )

            if not kid:
                kid = str(uuid.uuid4())
                generate_rsa_key_pair(kid)

        key_data = KEYS[kid]

        payload = {
            'sub': username,
            'iat': now,
            'exp': now + datetime.timedelta(
                minutes=30 if not expired else -30
            ),
        }

        token = jwt.encode(
            payload,
            key_data['private_key'],
            algorithm='RS256',
            headers={'kid': kid},
        )

        return jsonify({'token': token})

    # Handle invalid method for auth endpoint
    @app.route('/auth', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
    def auth_invalid():
        return make_response(
            jsonify({'message': 'Method Not Allowed'}), 405
        )
