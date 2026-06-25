import re

UI_PATTERNS = [
    "associez un profil instagram",
    "en savoir plus",
    "plus tard associer",
    "boîte de réception",
    "liker notre page",
    "canalboxgabon",
    "facebook",
    "instagram"
]

def clean_message(text: str) -> str:
    if not text:
        return ""

    # normalisation
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()

    # suppression UI Facebook
    lower = text.lower()
    for p in UI_PATTERNS:
        if p in lower:
            return ""

    # suppression timestamps Facebook
    text = re.sub(r"Aujourd’hui\s*\d{1,2}:\d{2}", "", text)
    text = re.sub(r"\d{1,2}:\d{2}", "", text)

    return text.strip()