import os
import fitz  # PyMuPDF
from docling.document_converter import DocumentConverter

# --- Configuração de Pastas ---
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_markdown"
PDF_FILENAME = "jurisprudencia.pdf"  # Renomeei para um nome mais descritivo

def process_pdf_with_links(pdf_filename: str):
    """
    Converte um PDF para Markdown usando Docling e, em seguida,
    re-injeta os hiperlinks extraídos com PyMuPDF.
    """
    # --- Garante que os diretórios existam ---
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Caminhos dos arquivos ---
    source_path = os.path.join(INPUT_DIR, pdf_filename)
    output_filename = f"{os.path.splitext(pdf_filename)[0]}_with_links.md"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(source_path):
        print(f"Erro: Arquivo de entrada não encontrado em '{source_path}'")
        return

    # --- Etapa 1: Converter com Docling para obter a estrutura ---
    print(f"Processando com Docling para obter o layout: {source_path}")
    converter = DocumentConverter()
    result = converter.convert(source_path)
    markdown_content = result.document.export_to_markdown()
    print("Layout e texto extraídos com sucesso.")

    # --- Etapa 2: Extrair hiperlinks com PyMuPDF ---
    print("Extraindo hiperlinks com PyMuPDF...")
    link_map = {}
    try:
        doc = fitz.open(source_path)
        for page in doc:
            links = page.get_links()
            for link in links:
                if link['kind'] == fitz.LINK_URI:
                    # A 'from_rect' é a caixa delimitadora do texto do link
                    rect = link['from_rect']
                    # Extrai o texto dentro da caixa delimitadora
                    anchor_text = page.get_textbox(rect).strip()
                    # Limpa o texto, pois pode conter quebras de linha
                    cleaned_text = " ".join(anchor_text.split())
                    if cleaned_text:
                        link_map[cleaned_text] = link['uri']
        doc.close()
        print(f"Encontrados {len(link_map)} links únicos.")
    except Exception as e:
        print(f"Ocorreu um erro ao extrair links: {e}")
        # Prossegue sem os links se houver erro
        link_map = {}

    # --- Etapa 3: Combinar os resultados ---
    print("Combinando layout com hiperlinks...")
    # Itera sobre os links extraídos e substitui no conteúdo do Markdown
    for anchor_text, url in link_map.items():
        # Cria o link em formato Markdown
        markdown_link = f"[{anchor_text}]({url})"
        # Substitui o texto simples pelo link formatado
        markdown_content = markdown_content.replace(anchor_text, markdown_link)
    
    # --- Etapa 4: Salvar o arquivo final ---
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"\nConversão avançada concluída!")
    print(f"O resultado com links foi salvo em: {output_path}")


if __name__ == "__main__":
    # Renomeie o seu arquivo PDF para "jurisprudencia.pdf" e coloque-o na pasta "input_pdfs"
    process_pdf_with_links(PDF_FILENAME)