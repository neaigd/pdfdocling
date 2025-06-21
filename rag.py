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

def create_qa_system(file_path: str):
    """Cria e retorna um sistema de Q&A a partir de um arquivo de texto."""
    # 1. Carregar o documento
    loader = TextLoader(file_path)
    documents = loader.load()

    # 2. Dividir o texto em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(documents)

    # 3. Criar embeddings usando um modelo que roda em CPU
    print("Criando embeddings... Isso pode levar um momento.")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    # 4. Criar o vector store (banco de dados de vetores) com FAISS
    vectorstore = FAISS.from_documents(docs, embeddings)

    # 5. Criar um template de prompt customizado
    prompt_template = """Use os seguintes trechos de contexto para responder à pergunta no final.
Se você não sabe a resposta, apenas diga que não sabe, não tente inventar uma resposta.

Contexto: {context}

Pergunta: {question}

Resposta:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # 6. Criar a instância do LLM com Groq (usando Llama 3 70B)
    llm = ChatGroq(
        model_name="llama3-70b-8192",
        temperature=0
    )

    # 7. Criar a cadeia de Q&A (RetrievalQA)
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
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    # Checar se a chave de API do Groq está configurada
    if not os.getenv("GROQ_API_KEY"):
        print("Por favor, configure sua GROQ_API_KEY no arquivo .env")
        return

    # Obter o caminho do arquivo do usuário
    file_path = input("Digite o caminho para o seu arquivo de texto (ex: conversion_results.txt): ")

    try:
        print("\nInicializando o sistema de Q&A... Isso pode levar um momento.")
        qa = create_qa_system(file_path)
        print("\nQA system ready! Digite 'quit' para sair.")

        # Loop interativo
        while True:
            question = input("\nDigite sua pergunta: ")
            if question.lower() == 'quit':
                break
            
            # Obter a resposta
            response = qa.invoke({"query": question})
            
            print("\nResposta:", response['result'])
            print("\nDocumentos de origem usados:")
            for i, doc in enumerate(response['source_documents']):
                print(f"  {i+1}. {doc.page_content[:200]}...")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()