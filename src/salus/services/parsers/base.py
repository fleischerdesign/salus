from salus.models.measurement import Measurement


class BaseParser:
    def can_handle(self, payload: dict | list) -> bool:
        if not isinstance(payload, dict):
            return False
        return self._can_handle_impl(payload)

    def parse(self, payload: dict | list) -> list[Measurement]:
        if not isinstance(payload, dict):
            return []
        return self._parse_impl(payload)

    def _can_handle_impl(self, payload: dict) -> bool:
        raise NotImplementedError

    def _parse_impl(self, payload: dict) -> list[Measurement]:
        raise NotImplementedError
