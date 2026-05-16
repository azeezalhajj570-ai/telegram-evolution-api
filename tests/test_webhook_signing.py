from app.security.webhook_signing import sign_payload, verify_signature


def test_sign_and_verify():
    payload = b'{"event": "message", "data": "hello"}'
    secret = "test-secret-123"
    signature = sign_payload(payload, secret)
    assert verify_signature(payload, secret, signature)


def test_wrong_secret():
    payload = b'{"event": "message"}'
    signature = sign_payload(payload, "secret-1")
    assert not verify_signature(payload, "secret-2", signature)


def test_tampered_payload():
    payload = b'{"event": "message"}'
    secret = "my-secret"
    signature = sign_payload(payload, secret)
    assert not verify_signature(b'{"event": "modified"}', secret, signature)
