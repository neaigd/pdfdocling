import os
import fitz  # PyMuPDF
import re

from docling.document_converter import DocumentConverter

# --- Configuração de Pastas ---
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_markdown"
PDF_FILENAME = "jurisprudencia.pdf"

def process_pdf_with_html_links(pdf_filename: str):
    """
    Converte um PDF para Markdown e insere links como snippets HTML robustos,
    com um ícone SVG colorido para destaque visual.
    """
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    source_path = os.path.join(INPUT_DIR, pdf_filename)
    output_filename = f"{os.path.splitext(pdf_filename)[0]}_with_html_links.md"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(source_path):
        print(f"Erro: Arquivo de entrada não encontrado em '{source_path}'")
        return

    # --- Etapa 1: Converter com Docling ---
    print(f"Processando com Docling: {source_path}")
    converter = DocumentConverter()
    result = converter.convert(source_path)
    markdown_content = result.document.export_to_markdown()
    print("Layout e texto extraídos.")

    # --- Etapa 2: Extração de Hiperlinks Aprimorada com PyMuPDF ---
    print("Extraindo hiperlinks com método geométrico aprimorado...")
    links_to_process = []
    try:
        doc = fitz.open(source_path)
        for page in doc:
            words = page.get_text("words")
            
            for link in page.get_links():
                if link.get('kind') == fitz.LINK_URI and 'from' in link:
                    link_rect = fitz.Rect(link['from'])
                    anchor_words = [w[4] for w in words if fitz.Rect(w[:4]).intersects(link_rect)]
                    
                    if anchor_words:
                        anchor_text = " ".join(anchor_words)
                        if (anchor_text, link['uri']) not in links_to_process:
                            links_to_process.append((anchor_text, link['uri']))
        doc.close()
        print(f"Encontrados {len(links_to_process)} links únicos para processar.")
    except Exception as e:
        print(f"Ocorreu um erro ao extrair links: {e}")
        links_to_process = []

    # --- Etapa 3: Substituir texto por Snippets HTML (com Ícone Colorido) ---
    print("Substituindo texto por snippets HTML com ícones SVG coloridos...")

    # Ícone SVG "external-link" com cor azul (#3B82F6) para destaque.
    # O atributo 'stroke' foi alterado de "currentColor" para um código de cor fixo.
    html_icon_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" '
        'viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2.5" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; margin-left: 5px; display: inline-block;">'
        '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>'
        '<polyline points="15 3 21 3 21 9"></polyline>'
        '<line x1="10" y1="14" x2="21" y2="3"></line>'
        '</svg>'
    )
    
    for anchor_text, url in links_to_process:
        # Escapa as aspas na URL para um HTML válido
        safe_url = url.replace('"', '&quot;')
        
        # Cria o snippet HTML com a URL segura e o ícone colorido
        html_link_snippet = (
            f'{anchor_text}'
            f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer" title="Abrir no navegador">'
            f'{html_icon_svg}'
            f'</a>'
        )
        
        # Usa Regex para a substituição precisa
        pattern = re.escape(anchor_text)
        markdown_content, num_subs = re.subn(pattern, html_link_snippet, markdown_content, count=1)
        
        if num_subs == 0:
            print(f"Aviso: Não foi possível encontrar o texto âncora para substituir: '{anchor_text}'")

    # --- Etapa 4: Salvar o arquivo final ---
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"\nConversão final concluída!")
    print(f"O resultado foi salvo em: {output_path}")


if __name__ == "__main__":
    process_pdf_with_html_links(PDF_FILENAME)