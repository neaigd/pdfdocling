import os
from dotenv import load_dotenv

# Importações do LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# --- Configuração de Pastas ---
VECTOR_DB_DIR = "vector_db"
DB_FAISS_PATH = os.path.join(VECTOR_DB_DIR, "faiss_index")

# --- Modelo de Embedding (definido globalmente para reutilização) ---
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

def update_vector_db(vectorstore, file_path: str):
    """Adiciona um novo documento a um banco de dados vetorial existente."""
    print(f"\nAtualizando banco de dados com o arquivo: {file_path}")
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    if not docs:
        print("Aviso: Nenhum texto foi extraído do documento para adicionar.")
        return vectorstore
        
    print(f"Adicionando {len(docs)} novos trechos ao banco de dados...")
    vectorstore.add_documents(docs)
    vectorstore.save_local(DB_FAISS_PATH) # Salva as alterações
    print("Banco de dados atualizado e salvo com sucesso!")
    return vectorstore

def create_and_load_vector_db(file_path: str = None):
    """Cria um novo banco de dados ou carrega um existente."""
    if os.path.exists(DB_FAISS_PATH):
        print(f"Carregando banco de dados vetorial existente de '{DB_FAISS_PATH}'...")
        try:
            vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
            return vectorstore
        except Exception as e:
            print(f"Erro ao carregar o banco de dados: {e}. Considere apagar a pasta 'vector_db' e recomeçar.")
            return None
    elif file_path and os.path.exists(file_path):
        print(f"Criando novo banco de dados vetorial a partir de '{file_path}'...")
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(DB_FAISS_PATH)
        print(f"Banco de dados vetorial criado e salvo em '{DB_FAISS_PATH}'")
        return vectorstore
    else:
        return None

def create_analysis_chain(vectorstore):
    """Cria uma cadeia de Q&A otimizada para análise jurídica."""
    
    prompt_template = """Você é um assistente jurídico sênior, especializado em jurisprudência brasileira. Sua tarefa é analisar o caso de um cliente e compará-lo com as teses e julgados fornecidos no contexto. Seja preciso e direto.

**Caso do Cliente:**
{question}

**Contexto (Teses e Julgados Encontrados):**
{context}

**Sua Análise Estruturada:**
Com base estritamente no contexto fornecido, forneça a seguinte análise:
1.  **Teses Relevantes:** Liste, de forma concisa, as teses ou julgados do contexto que se aplicam diretamente ao caso do cliente.
2.  **Análise de Posição:** Classifique a jurisprudência encontrada como **FAVORÁVEL**, **CONTRÁRIA** ou **NEUTRA** à posição do cliente.
3.  **Justificativa:** Elabore uma explicação clara e objetiva do porquê. Conecte os pontos da jurisprudência com os fatos descritos no caso do cliente para fundamentar sua análise. Se o contexto não for suficiente, afirme isso.

**Resultado da Análise:**
"""

    PROMPT_ANALYSIS = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0.2)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT_ANALYSIS}
    )
    return qa_chain

def main():
    """Função principal com menu interativo para o assistente jurídico."""
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("Erro: Por favor, configure sua GROQ_API_KEY no arquivo .env")
        return

    vectorstore = create_and_load_vector_db()
    
    if not vectorstore:
        print("\nNenhum banco de dados encontrado. É necessário criar um com o primeiro documento.")
        initial_file = input("Digite o caminho para o seu primeiro arquivo Markdown (ex: output_markdown/jurisprudencia_with_html_links.md): ")
        if os.path.exists(initial_file):
            vectorstore = create_and_load_vector_db(initial_file)
        else:
            print(f"Arquivo '{initial_file}' não encontrado. Encerrando.")
            return

    if not vectorstore:
        print("Falha ao criar ou carregar o banco de dados. Encerrando.")
        return

    print("\nInicializando a cadeia de análise jurídica...")
    qa = create_analysis_chain(vectorstore)
    print("Sistema pronto.")

    while True:
        print("\n--- Assistente de Análise Jurídica ---")
        print("[1] Analisar um caso")
        print("[2] Adicionar nova jurisprudência ao banco de dados")
        print("[3] Sair")
        choice = input("Escolha uma opção: ")

        if choice == '1':
            case_description = input("\nDescreva a situação jurídica do seu cliente: ")
            if case_description:
                print("\nAnalisando... Isso pode levar alguns segundos.")
                response = qa.invoke({"query": case_description})
                print("\n--- Análise da IA ---")
                print(response['result'])
                print("\n--- Documentos de Origem Consultados ---")
                for i, doc in enumerate(response['source_documents']):
                    clean_content = " ".join(doc.page_content.splitlines())
                    print(f"  {i+1}. {clean_content[:250]}...")
        
        elif choice == '2':
            new_file_path = input("\nDigite o caminho para o novo arquivo Markdown a ser adicionado: ")
            if os.path.exists(new_file_path):
                vectorstore = update_vector_db(vectorstore, new_file_path)
                qa = create_analysis_chain(vectorstore)
                print("Cadeia de análise atualizada com o novo documento.")
            else:
                print(f"Erro: Arquivo '{new_file_path}' não encontrado.")

        elif choice == '3':
            print("Encerrando o sistema.")
            break
        
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()