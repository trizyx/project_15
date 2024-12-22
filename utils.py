def detect_language(input_text: str) -> str:
    if all("а" <= char <= "я" or char == "ё" for char in input_text.lower() if char.isalpha()):
        return "ru-ru"
    return "en-us"


print(detect_language('Landon'))
