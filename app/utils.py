import unicodedata
import re

def clean_and_normalize_label(name: str) -> str:
    # 1. Verifica se está vazio antes de tentar manipular
    if not name or not name.strip():
        return ""
    
    # 2. Transforma em minúsculas e colapsa espaços múltiplos
    name = " ".join(name.lower().split())
    
    # 3. Remove os acentos (Padrão Ouro)
    name = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("utf-8")
    
    # 4. Substitui underlines por espaços e remove caracteres especiais (corrigido \w e \s)
    name = name.replace("_", " ")
    name = re.sub(r"[^\w\s-]", "", name)
    
    return name
    