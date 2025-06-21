
# Docling: Análise Avançada de PDF e Sistema RAG

Este projeto demonstra como usar a biblioteca `docling` da IBM para extrair dados estruturados de PDFs e construir um sistema de Perguntas e Respostas (Q&A) com uma arquitetura RAG (Retrieval-Augmented Generation).

O projeto é projetado para rodar inteiramente em CPU, utilizando LangChain, FAISS para armazenamento local de vetores e a API do Groq para inferência ultrarrápida com o modelo Llama 3.

## ✨ Funcionalidades

-   **Estrutura Organizada:** O projeto separa dados de entrada, saídas intermediárias e bancos de dados persistentes.
-   **Conversão de PDF para Markdown:** Utiliza `docling` para analisar a estrutura, layout, tabelas e imagens de um PDF.
-   **Banco de Dados Vetorial Persistente:** Cria um banco de dados FAISS localmente, permitindo inicializações rápidas em usos futuros.
-   **Pipeline RAG Completo:** Implementa um sistema de Q&A de ponta a ponta.
-   **CPU-Only:** Todo o processo foi projetado para rodar em uma CPU comum.

## 📂 Estrutura do Projeto

```
/
├── input_pdfs/                 # Coloque seus PDFs de entrada aqui
│   └── docling.pdf
├── output_markdown/            # Arquivos Markdown gerados (ignorado pelo .gitignore)
├── vector_db/                  # Banco de dados vetorial FAISS (ignorado pelo .gitignore)
├── .venv/                      # Ambiente virtual Python
├── .env                        # Arquivo para a chave de API do Groq
├── .gitignore                  # Arquivos a serem ignorados pelo Git
├── requirements.txt            # Dependências do projeto
├── doc.py                      # Script para converter PDF -> Markdown
└── rag.py                      # Script para rodar o sistema de Q&A (RAG)
```

## ⚙️ Configuração e Instalação

### 1. Pré-requisitos
- Python 3.9 ou superior.

### 2. Clone o Repositório e Crie as Pastas
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
mkdir input_pdfs output_markdown vector_db
# Mova seu arquivo PDF para a pasta input_pdfs
mv seu_arquivo.pdf input_pdfs/
```

### 3. Crie e Ative um Ambiente Virtual
- **Windows:**
  ```bash
  python -m venv .venv
  .\.venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 4. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 5. Configure sua Chave de API
1.  Obtenha uma chave de API gratuita em [https://console.groq.com/keys](https://console.groq.com/keys).
2.  Crie um arquivo chamado `.env` na raiz do projeto.
3.  Adicione sua chave ao arquivo da seguinte forma:
    ```
    GROQ_API_KEY="SUA_CHAVE_API_AQUI"
    ```

## 🚀 Como Executar

O fluxo de trabalho agora é mais robusto.

### Etapa 1: Converter o PDF para Markdown
Execute o script `doc.py`. Ele irá procurar por `docling.pdf` na pasta `input_pdfs` e salvar o resultado em `output_markdown`.
```bash
python doc.py
```
Isso criará o arquivo `output_markdown/docling_converted.md`.

### Etapa 2: Iniciar o Sistema de Perguntas e Respostas (RAG)
Execute o script `rag.py`.
```bash
python rag.py
```

-   **Na primeira execução:** O script não encontrará um banco de dados vetorial. Ele pedirá o caminho para o arquivo Markdown gerado:
    ```
    Digite o caminho para o arquivo Markdown de origem (ex: output_markdown/docling_converted.md): output_markdown/docling_converted.md
    ```
    Ele então criará o banco de dados vetorial e o salvará na pasta `vector_db/`.

-   **Em execuções futuras:** O script detectará e carregará automaticamente o banco de dados vetorial da pasta `vector_db/`, tornando a inicialização muito mais rápida.

Após a inicialização, você pode começar a fazer perguntas ao chatbot. Para sair, digite `quit`.

### Exemplo de Interação

```
Digite sua pergunta: what is docling?

Resposta: Based on the provided context, Docling is a tool that converts PDF documents to JSON or Markdown format, and it can also extract metadata from the document, such as title, authors, and language. Additionally, it can understand detailed page layout, reading order, locate figures, and recover table structures. It can also optionally apply OCR (Optical Character Recognition) for scanned PDFs.
```