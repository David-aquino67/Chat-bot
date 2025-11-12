class TextUtils:
    def is_valid(self, text: str) -> bool:
        return bool(text and len(text.strip()) > 1 and len(text) < 5000)

    def clean(self, text: str) -> str:
        return text.strip()