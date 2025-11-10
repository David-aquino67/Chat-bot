class TextUtils:
    """Colección de utilidades agnósticas para el manejo de texto."""

    def is_valid(self, text: str) -> bool:
        """Verifica que el texto no sea nulo, vacío, o demasiado largo/corto."""
        return bool(text and len(text.strip()) > 1 and len(text) < 5000)

    def clean(self, text: str) -> str:
        """Limpia el texto (ej: eliminar espacios extra, normalizar)."""
        return text.strip()