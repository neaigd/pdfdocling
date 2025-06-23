# Assistente Jurídico RAG: Da Jurisprudência em Teses à Análise de Casos

Este projeto é um pipeline completo de automação para pesquisa e análise jurídica, projetado para transformar as publicações "Jurisprudência em Teses" do STJ em uma base de conhecimento interativa e inteligente.

O fluxo de trabalho começa com o processamento de um PDF oficial, preservando seus links e estrutura, e culmina em um assistente de IA capaz de analisar casos específicos com base na jurisprudência catalogada.

## 🎯 O Desafio

Advogados e pesquisadores lidam com um volume massivo de publicações em PDF. O desafio é converter esses documentos estáticos em um formato dinâmico que permita:
1.  **Extração de Dados Estruturados:** Converter o texto e o layout do PDF para um formato limpo e legível.
2.  **Preservação de Fontes:** Manter os hiperlinks para os julgados e informativos originais, permitindo uma verificação rápida e o catalogamento em ferramentas como o Zotero.
3.  **Busca Semântica:** Ir além da busca por palavras-chave, permitindo consultar a base de conhecimento com descrições de casos em linguagem natural.
4.  **Análise Inteligente:** Obter uma análise preliminar sobre como a jurisprudência se aplica a um caso específico, classificando-a como favorável ou contrária.

## ✨ Solução e Funcionalidades

Este projeto aborda o desafio com um pipeline de duas etapas principais, utilizando ferramentas de IA de ponta:

-   **Processamento e Catalogação (`doc_advanced.py`)**:
    -   **Análise com `docling`:** Utiliza a biblioteca da IBM para uma análise profunda do layout do PDF, garantindo que a estrutura visual seja corretamente traduzida para Markdown.
    -   **Extração de Links com `PyMuPDF`:** Emprega um método geométrico para extrair todos os hiperlinks do documento.
    -   **Geração de Saída Rica:** Cria um arquivo Markdown onde os links são preservados como snippets HTML interativos, com ícones clicáveis, prontos para uso.

-   **Análise e Consulta com RAG (`rag_advanced.py`)**:
    -   **Base de Conhecimento Vetorial:** Constrói um banco de dados vetorial (FAISS) a partir dos arquivos Markdown gerados. Este banco de dados é **persistente e incremental**, permitindo que novas jurisprudências sejam adicionadas ao longo do tempo.
    -   **Busca Semântica com LangChain:** Utiliza `langchain-huggingface` para converter descrições de casos em vetores e encontrar os trechos de jurisprudência mais relevantes.
    -   **Análise com LLM via Groq:** Envia o caso do cliente e o contexto encontrado para o modelo Llama 3 70B através da API ultrarrápida do Groq.
    -   **Interface Interativa:** Um menu no terminal guia o usuário, permitindo escolher entre analisar um novo caso ou atualizar a base de conhecimento.
    -   **CPU-Only:** Todo o pipeline é otimizado para rodar eficientemente em uma CPU padrão.

## 📂 Estrutura do Projeto

```
/
├── input_pdfs/                 # Coloque seus PDFs de entrada aqui
│   └── jurisprudencia.pdf
├── output_markdown/            # Arquivos Markdown gerados (ignorado pelo .gitignore)
├── vector_db/                  # Banco de dados vetorial FAISS persistente (ignorado pelo .gitignore)
├── .venv/                      # Ambiente virtual Python
├── .env                        # Arquivo para a chave de API do Groq
├── .gitignore                  # Arquivos a serem ignorados pelo Git
├── requirements.txt            # Dependências do projeto
├── doc_advanced.py             # Script de processamento: PDF -> Markdown com HTML
└── rag_advanced.py             # Script principal: Assistente de análise jurídica
```

## ⚙️ Configuração e Instalação

1.  **Clone o Repositório**:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```
2.  **Crie as Pastas Necessárias**:
    ```bash
    mkdir input_pdfs
    ```
    Coloque seu arquivo PDF (ex: `jurisprudencia.pdf`) dentro da pasta `input_pdfs`.

3.  **Crie e Ative um Ambiente Virtual**:
    -   **Windows**: `python -m venv .venv` e `.\.venv\Scripts\activate`
    -   **macOS/Linux**: `python3 -m venv .venv` e `source .venv/bin/activate`

4.  **Instale as Dependências**:
    Todas as bibliotecas necessárias estão listadas no arquivo `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure sua Chave de API do Groq**:
    -   Obtenha uma chave gratuita em [https://console.groq.com/keys](https://console.groq.com/keys).
    -   Crie um arquivo chamado `.env` e adicione a linha: `GROQ_API_KEY="SUA_CHAVE_API_AQUI"`.

## 🚀 Fluxo de Trabalho Operacional

Este sistema foi projetado para um ciclo de uso contínuo.

### Etapa 1: Processar e Catalogar a Jurisprudência

Sempre que você tiver um novo PDF de "Jurisprudência em Teses":

1.  **Adicione o PDF** à pasta `input_pdfs/`.
2.  **Atualize o nome do arquivo** na variável `PDF_FILENAME` dentro do script `doc_advanced.py`.
3.  **Execute o script de processamento**:
    ```bash
    python doc_advanced.py
    ```
    -   **Resultado:** Um novo arquivo `.md` será criado em `output_markdown/`. Este arquivo é seu "artefato limpo": o texto está bem estruturado, e os links para as fontes originais são interativos. **Neste ponto, você pode abrir este arquivo, clicar nos links e catalogar as jurisprudências no seu Zotero ou outra ferramenta de gerenciamento.**

### Etapa 2: Ingerir o Conhecimento no Assistente de IA

Com o documento processado, alimente-o na base de conhecimento do seu assistente.

1.  **Execute o assistente jurídico**:
    ```bash
    python rag_advanced.py
    ```
2.  **Na primeira execução**, o sistema detectará que não há um banco de dados e solicitará o caminho do primeiro arquivo. Forneça o caminho gerado na Etapa 1 (ex: `output_markdown/jurisprudencia_with_html_links.md`).
3.  **Para adicionar documentos subsequentes**, escolha a opção **`[2] Adicionar nova jurisprudência...`** no menu principal e forneça o caminho do novo arquivo `.md`. O sistema atualizará a base de dados de forma incremental.

### Etapa 3: Realizar uma Análise de Casos

Com a base de conhecimento pronta e atualizada, use-a para análises práticas.

1.  **Execute o assistente jurídico**:
    ```bash
    python rag_advanced.py
    ```
2.  No menu, escolha a opção **`[1] Analisar um caso`**.
3.  **Descreva a situação do seu cliente** em linguagem natural. Por exemplo:
    > "Meu cliente é pai de uma criança com TEA e o plano de saúde se recusa a cobrir musicoterapia, além de limitar as sessões de outras terapias. Qual a posição da jurisprudência sobre isso?"
4.  **Receba a Análise:** O sistema irá consultar toda a sua base de dados, encontrar as teses mais relevantes e fornecer uma análise estruturada, indicando se a jurisprudência é **favorável**, **contrária** ou **neutra** à posição do seu cliente, com a devida fundamentação.

Para encerrar o programa a qualquer momento, escolha a opção **`[3] Sair`** no menu.