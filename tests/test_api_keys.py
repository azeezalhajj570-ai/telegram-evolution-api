from app.security.api_keys import generate_api_key, hash_api_key, verify_api_key


def test_hash_and_verify():
    key = "test-api-key-12345"
    h = hash_api_key(key)
    assert verify_api_key(key, h)
    assert not verify_api_key("wrong-key", h)


def test_different_hashes():
    h1 = hash_api_key("key1")
    h2 = hash_api_key("key1")
    assert h1 != h2


def test_generate_api_key_format():
    key = generate_api_key()
    assert key.startswith("tev_")
    assert len(key) > 20
