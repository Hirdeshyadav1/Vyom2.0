class IntegrityViolationError(Exception):
    pass


class IntegrityMonitor:
    def __init__(self, *args, **kwargs):
        pass

    def verify_or_crash(self, *args, **kwargs):
        pass

    def create_baseline(self):
        return {"ok": True}


def load_or_create_secret_key(key_path):
    return b"disabled"
