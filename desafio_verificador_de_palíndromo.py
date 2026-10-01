import unicodedata

def eh_palindromo(texto):
    # Remove acentos
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    # Mantém apenas letras e números, além de converter para minúsculas
    texto = "".join(
        caractere.lower()
        for caractere in texto
        if caractere.isalnum()
    )

    # Compara com o texto invertido
    return texto == texto[::-1]


# Teste:
print(eh_palindromo("Ame o poema"))  # True
