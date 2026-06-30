from salus.services.jwt import JwtService
from salus.services.password import hash_password, verify_password


class TestPasswordService:
    def test_hash_and_verify(self):
        h = hash_password("mysecret")
        assert verify_password("mysecret", h)
        assert not verify_password("wrong", h)

    def test_different_salts(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestJwtService:
    @staticmethod
    def _svc():
        return JwtService(secret="test-secret-key-for-jwt-testing")

    def test_create_and_verify(self):
        svc = self._svc()
        token = svc.create_token(1, "alice")
        payload = svc.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["username"] == "alice"

    def test_verify_invalid_token(self):
        svc = self._svc()
        payload = svc.verify_token("not.a.token")
        assert payload is None

    def test_verify_tampered_token(self):
        svc = self._svc()
        token = svc.create_token(1, "alice")
        payload = svc.verify_token(token + "tampered")
        assert payload is None
