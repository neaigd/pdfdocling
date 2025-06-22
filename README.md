
# Docling: Análise Avançada de PDF e Sistema RAG com Preservação de Links

Este projeto demonstra como usar a biblioteca `docling` da IBM, combinada com `PyMuPDF`, para extrair dados estruturados e preservar hiperlinks embutidos de documentos PDF.

O objetivo é converter um PDF jurídico em um formato Markdown limpo e, em seguida, usar esse conteúdo para alimentar um sistema de Perguntas e Respostas (Q&A) construído com uma arquitetura RAG (Retrieval-Augmented Generation). O sistema final é capaz de responder a perguntas sobre o conteúdo do documento, mantendo os links de referência para as fontes originais.

## ✨ Funcionalidades

-   **Estrutura Organizada:** O projeto separa dados de entrada, saídas intermediárias e bancos de dados persistentes.
-   **Conversão com Preservação de Links**: Usa `docling` para a análise de layout e `PyMuPDF` para a extração de hiperlinks, combinando os resultados em um arquivo Markdown rico.
-   **Extração de Tabelas e Layout**: Mantém a formatação de tabelas e a estrutura visual do documento original.
-   **Banco de Dados Vetorial Persistente**: Cria um banco de dados FAISS local para inicializações rápidas em usos futuros.
-   **Pipeline RAG Completo**: Sistema de Q&A construído com LangChain, Groq (Llama 3 70B) e projetado para rodar inteiramente em CPU.

## 📂 Estrutura do Projeto

```
/
├── input_pdfs/                 # Coloque seus PDFs de entrada aqui
│   └── jurisprudencia.pdf
├── output_markdown/            # Arquivos Markdown gerados (ignorado pelo .gitignore)
├── vector_db/                  # Banco de dados vetorial FAISS (ignorado pelo .gitignore)
├── .venv/                      # Ambiente virtual Python
├── .env                        # Arquivo para a chave de API do Groq
├── .gitignore                  # Arquivos a serem ignorados pelo Git
├── requirements.txt            # Dependências do projeto
├── doc_advanced.py             # Script para converter PDF -> Markdown com links
└── rag.py                      # Script para rodar o sistema de Q&A (RAG)
```

## ⚙️ Configuração e Instalação

1.  **Clone o Repositório e Crie as Pastas**:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    mkdir input_pdfs
    ```
    Coloque seu arquivo `jurisprudencia.pdf` dentro da pasta `input_pdfs`.

2.  **Crie e Ative um Ambiente Virtual**:
    -   Windows: `python -m venv .venv` e `.\.venv\Scripts\activate`
    -   macOS/Linux: `python3 -m venv .venv` e `source .venv/bin/activate`

3.  **Instale as Dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure sua Chave de API do Groq**:
    -   Obtenha uma chave em [https://console.groq.com/keys](https://console.groq.com/keys).
    -   Crie um arquivo `.env` e adicione a linha: `GROQ_API_KEY="SUA_CHAVE_API_AQUI"`.

## 🚀 Como Executar

### Etapa 1: Converter o PDF (com Links)
Execute o script `doc_advanced.py`. Ele irá processar o PDF da pasta `input_pdfs` e salvará um novo arquivo Markdown com os links preservados na pasta `output_markdown`.
```bash
python doc_advanced.py
```

### Etapa 2: Iniciar o Sistema de Perguntas e Respostas (RAG)
Execute o script `rag.py`.
```bash
python rag.py
```
-   **Na primeira execução**, o script não encontrará um banco de dados vetorial. Ele pedirá o caminho para o arquivo Markdown. Digite:
    ```
    output_markdown/jurisprudencia_with_links.md
    ```
    Ele criará o banco de dados vetorial na pasta `vector_db/`.

-   **Em execuções futuras**, ele carregará automaticamente o banco de dados existente, agilizando a inicialização.

Após a inicialização, você poderá interagir com o chatbot. Para sair, digite `quit`.