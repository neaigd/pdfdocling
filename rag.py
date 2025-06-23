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

def create_and_load_vector_db(file_path: str = None):
    """
    Cria um novo banco de dados se não existir, ou carrega um existente.
    """
    print("--- [DEBUG] Entrando em create_and_load_vector_db ---")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    if os.path.exists(DB_FAISS_PATH):
        print(f"--- [DEBUG] Caminho {DB_FAISS_PATH} existe. Tentando carregar...")
        try:
            vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
            print("--- [DEBUG] Banco de dados carregado com sucesso.")
            return vectorstore
        except Exception as e:
            print(f"--- [DEBUG] Erro ao carregar o banco de dados: {e}. Retornando None.")
            return None
    elif file_path and os.path.exists(file_path):
        print(f"--- [DEBUG] Criando novo banco de dados a partir de {file_path}...")
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()

        if not documents:
            print("--- [DEBUG] Aviso: Nenhum documento carregado do arquivo. Não é possível criar o banco de dados.")
            return None

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(DB_FAISS_PATH)
        print(f"--- [DEBUG] Banco de dados criado e salvo em {DB_FAISS_PATH}.")
        return vectorstore
    else:
        print("--- [DEBUG] Nenhuma condição atendida para carregar ou criar. Retornando None.")
        return None

def create_qa_chain(vectorstore):
    """
    Cria uma cadeia de Q&A padrão usando o banco de dados vetorial.
    """
    prompt_template = """Use os seguintes trechos de contexto para responder à pergunta no final. Se você não sabe a resposta, apenas diga que não sabe, não tente inventar uma resposta.

Contexto: {context}
Pergunta: {question}
Resposta:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    llm = ChatGroq(model_name="llama3-8b-8192", temperature=0.1)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), return_source_documents=True, chain_type_kwargs={"prompt": PROMPT})
    return qa_chain

def main():
    """Função principal para rodar o sistema de Q&A interativo."""
    print("--- [DEBUG] Iniciando a função main ---")
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("Erro: Por favor, configure sua GROQ_API_KEY no arquivo .env")
        return

    vectorstore = create_and_load_vector_db()
    
    if not vectorstore:
        print("\nBanco de dados vetorial não encontrado. Vamos criar o primeiro.")
        initial_file = input("Digite o caminho para o seu arquivo Markdown de origem (ex: output_markdown/jurisprudencia_with_html_links.md): ")
        if os.path.exists(initial_file):
            vectorstore = create_and_load_vector_db(initial_file)
        else:
            print(f"Arquivo '{initial_file}' não encontrado. Encerrando.")
            return
            
    if not vectorstore:
        print("Não foi possível criar ou carregar o banco de dados. Encerrando.")
        return

    print("\nInicializando o sistema de Q&A...")
    qa = create_qa_chain(vectorstore)
    print("\nSistema de Q&A pronto! Digite 'quit' para sair.")

    while True:
        question = input("\nFaça sua pergunta: ")
        if question.lower() == 'quit':
            break
        
        print("\nBuscando resposta...")
        response = qa.invoke({"query": question})
        
        print("\nResposta:", response['result'])
        print("\n--- Documentos de Origem Consultados ---")
        for i, doc in enumerate(response['source_documents']):
            clean_content = " ".join(doc.page_content.splitlines())
            print(f"  {i+1}. {clean_content[:200]}...")

if __name__ == "__main__":
    main()