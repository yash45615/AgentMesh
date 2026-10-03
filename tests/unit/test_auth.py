def test_password_hashing():

    from app.core.security import (
        hash_password,
        verify_password,
    )

    password = "AgentMesh123!"

    hashed = hash_password(password)

    assert hashed != password

    assert verify_password(
        password,
        hashed,
    )

    assert not verify_password(
        "wrong-password",
        hashed,
    )
def test_jwt_token():

    from app.core.security import (
        create_access_token,
        decode_access_token,
    )

    token = create_access_token(
        {
            "sub": "123",
            "role": "developer",
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "123"

    assert payload["role"] == "developer"