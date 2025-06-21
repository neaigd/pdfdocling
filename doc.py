import os

from docling.document_converter import DocumentConverter

# --- Configuração de Pastas ---
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_markdown"
PDF_FILENAME = "docling.pdf"

# --- Garante que o diretório de saída exista ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Caminhos dos arquivos ---
source_path = os.path.join(INPUT_DIR, PDF_FILENAME)
output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(PDF_FILENAME)[0]}_converted.md")

# --- Verificação do arquivo de entrada ---
if not os.path.exists(source_path):
    print(f"Erro: Arquivo de entrada não encontrado em '{source_path}'")
else:
    print(f"Processando o arquivo: {source_path}")
    
    # --- Conversão do Documento ---
    converter = DocumentConverter()
    result = converter.convert(source_path)

    # Salva os resultados em formato Markdown no diretório de saída
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.document.export_to_markdown())

    print(f"Conversão concluída! O resultado foi salvo em: {output_path}")