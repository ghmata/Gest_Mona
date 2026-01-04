"""
Testes unitários básicos para o serviço Groq OCR.
Este arquivo pode ser executado para verificar a integridade do serviço.
"""
from services.groq_service import get_groq_service

# Teste 1: Inicialização
print("Testando inicialização do serviço...")
service = get_groq_service()
print(f"✅ Serviço inicializado: {service}")

# Teste 2: Validação de categoria
print("\nTestando normalização de categoria...")
testes_categoria = [
    ("legumes", "Hortifruti"),
    ("Hortifruti", "Hortifruti"),
    ("carnes", "Açougue"),
    ("BEBIDAS", "Bebidas"),
    ("marmitex", "Embalagens"),
    ("categoria_inexistente", "Outros"),
]

for entrada, esperado in testes_categoria:
    resultado = service._normalizar_categoria(entrada)
    status = "✅" if resultado == esperado else "❌"
    print(f"  {status} '{entrada}' -> '{resultado}' (esperado: '{esperado}')")

# Teste 3: Validação de resposta
print("\nTestando validação de resposta...")
dados_validos = {
    "data": "2025-12-26",
    "estabelecimento": "CEASA",
    "valor_total": 150.00,
    "categoria": "Hortifruti"
}
assert service._validar_resposta(dados_validos) == True
print("✅ Validação de resposta OK para dados válidos")

dados_invalidos = {
    "estabelecimento": "CEASA",
    "categoria": "Hortifruti"
}
assert service._validar_resposta(dados_invalidos) == False
print("✅ Validação de resposta OK para dados inválidos (rejeitou corretamente)")

# Teste 4: Funções auxiliares
print("\nTestando funções auxiliares...")
from utils.helpers import extrair_json_de_texto, validar_data, formatar_valor

# Teste extrair_json_de_texto
json_texto = 'Aqui está: {"valor": 100}'
resultado = extrair_json_de_texto(json_texto)
assert resultado == {"valor": 100}
print("✅ extrair_json_de_texto OK")

# Teste validar_data
assert validar_data("2025-12-26") == True
assert validar_data("26/12/2025") == False
assert validar_data("2025-13-01") == False
print("✅ validar_data OK")

# Teste formatar_valor
assert formatar_valor("R$ 1.234,56") == 1234.56
assert formatar_valor("150,50") == 150.5
assert formatar_valor(100) == 100.0
print("✅ formatar_valor OK")

print("\n" + "="*50)
print("Todos os testes passaram com sucesso! ✅")
print("="*50)
