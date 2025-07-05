import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature


def generate_keys(private_key_path='private_key.pem', public_key_path='public_key.pem'):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    with open(private_key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    public_key = private_key.public_key()
    with open(public_key_path, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))


def sign_manifest(manifest_path, private_key_path='private_key.pem', signature_path='manifest.sig'):
    with open(manifest_path, 'rb') as f:
        data = f.read()

    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    with open(signature_path, 'wb') as f:
        f.write(signature)


def verify_manifest(manifest_path, signature_path='manifest.sig', public_key_path='public_key.pem'):
    with open(manifest_path, 'rb') as f:
        data = f.read()

    with open(signature_path, 'rb') as f:
        signature = f.read()

    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())

    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        print("Signature is valid.")
    except InvalidSignature:
        print("Invalid signature.")