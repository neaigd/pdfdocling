import os
from dotenv import load_dotenv

# Importações do LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# --- Configuração de Pastas ---
VECTOR_DB_DIR = "vector_db"
DB_FAISS_PATH = os.path.join(VECTOR_DB_DIR, "faiss_index")

def create_and_save_vector_db(file_path: str):
    """Cria e salva um banco de dados vetorial a partir de um arquivo de texto."""
    print(f"Criando novo banco de dados vetorial a partir de '{file_path}'...")
    
    # 1. Carregar o documento
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    # 2. Dividir o texto em chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # 3. Criar embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    # 4. Criar o vector store e salvar localmente
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(DB_FAISS_PATH)
    print(f"Banco de dados vetorial salvo em '{DB_FAISS_PATH}'")
    return vectorstore

def create_qa_chain(vectorstore):
    """Cria a cadeia de Q&A usando o banco de dados vetorial fornecido."""
    # Criar um template de prompt customizado
    prompt_template = """Use os seguintes trechos de contexto para responder à pergunta no final.
Se você não sabe a resposta, apenas diga que não sabe, não tente inventar uma resposta.

Contexto: {context}

Pergunta: {question}

Resposta:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Criar a instância do LLM com Groq
    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)

    # Criar a cadeia de Q&A
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain

def main():
    """Função principal para rodar o sistema de Q&A interativo."""
    load_dotenv()

    if not os.getenv("GROQ_API_KEY"):
        print("Erro: Por favor, configure sua GROQ_API_KEY no arquivo .env")
        return

    vectorstore = None
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})

    if os.path.exists(DB_FAISS_PATH):
        print(f"Carregando banco de dados vetorial existente de '{DB_FAISS_PATH}'...")
        vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        print("Banco de dados vetorial não encontrado.")
        markdown_file = input("Digite o caminho para o arquivo Markdown de origem (ex: output_markdown/docling_converted.md): ")
        if os.path.exists(markdown_file):
            vectorstore = create_and_save_vector_db(markdown_file)
        else:
            print(f"Erro: Arquivo '{markdown_file}' não encontrado. Execute doc.py primeiro.")
            return

    print("\nInicializando o sistema de Q&A...")
    qa = create_qa_chain(vectorstore)
    print("\nSistema de Q&A pronto! Digite 'quit' para sair.")

    while True:
        question = input("\nDigite sua pergunta: ")
        if question.lower() == 'quit':
            break
        
        response = qa.invoke({"query": question})
        
        print("\nResposta:", response['result'])
        print("\nDocumentos de origem usados:")
        for i, doc in enumerate(response['source_documents']):
            print(f"  {i+1}. {doc.page_content[:200].replace(os.linesep, ' ')}...")

if __name__ == "__main__":
    main()