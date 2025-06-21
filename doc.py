from docling.document_converter import DocumentConverter

# Define o arquivo de origem (pode ser um caminho local ou uma URL)
source = "docling.pdf" 
converter = DocumentConverter()
result = converter.convert(source)

# Imprime o resultado convertido para Markdown no console
print("--- Conversão para Markdown ---")
print(result.document.export_to_markdown())

# Salva os resultados em um arquivo de texto para fácil visualização
with open('conversion_results.txt', 'w', encoding='utf-8') as f:
    f.write(result.document.export_to_markdown())

print("\n--- Conversão salva em 'conversion_results.txt' ---")

# Você também pode exportar para JSON (formato de dicionário Python)
# json_output = result.document.export_to_dict()
# print("\n--- Conversão para JSON (amostra) ---")
# print(str(json_output)[:500] + "...") # Imprime uma amostra do JSON