import pytest

from app.security.encryption import decrypt, encrypt


def test_encrypt_decrypt_roundtrip():
    key = b"test-key-32-bytes-for-testing!!!!"
    plaintext = "hello-world-123"
    ciphertext = encrypt(plaintext, key)
    decrypted = decrypt(ciphertext, key)
    assert decrypted == plaintext


def test_decrypt_with_wrong_key():
    key = b"test-key-32-bytes-for-testing!!!!"
    wrong_key = b"wrong-key-32-bytes-for-testing!!!"
    ciphertext = encrypt("secret", key)
    with pytest.raises(Exception):
        decrypt(ciphertext, wrong_key)


def test_decrypt_tampered():
    key = b"test-key-32-bytes-for-testing!!!!"
    ciphertext = encrypt("data", key)
    tampered = ciphertext[:-4] + "xxxx"
    with pytest.raises(Exception):
        decrypt(tampered, key)


def test_empty_string():
    key = b"test-key-32-bytes-for-testing!!!!"
    ciphertext = encrypt("", key)
    decrypted = decrypt(ciphertext, key)
    assert decrypted == ""
