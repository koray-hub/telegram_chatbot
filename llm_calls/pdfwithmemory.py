#from langchain.document_loaders import PyPDFLoader
#from langchain_community.document_loaders import OnlinePDFLoader
#from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain_nomic.embeddings import NomicEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
#from langchain_ollama import ChatOllama
#from langchain.vectorstores import FAISS
#from langchain_nomic.embeddings import NomicEmbeddings
#from langchain.embeddings import HuggingFaceEmbeddings
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

import os

class Pdfchat:
    def __init__(self, model="llama3.1", tempreture=0, language="Turkish",message="hi",chatid="12345",documentfileinput="None"):
        self.model = model
        self.tempreture = tempreture
        self.language = language
        self.message=message
        self.chatid=chatid
        self.documentfileinput=documentfileinput
        self.vectorstore=self.process_vectorstore(documentfileinput)
        self.conversations = {}

    def process_vectorstore(self,documentfileinput):
        # Load PDF
        #loader = OnlinePDFLoader("/home/bot/Projects/telegram_chatbot/document_files/robinson.pdf")
        loader = PyMuPDFLoader("/home/bot/Projects/telegram_chatbot/document_files/"+documentfileinput,extract_images=False)
        #loader = PyPDFLoader("/home/bot/Projects/telegram_chatbot/document_files/"+documentfileinput,extract_images=False)
        documents = loader.load()

        # Split text into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        # Create embeddings and vector store
        #embed_model = HuggingFaceEmbeddings(model_name="distiluse-base-multilingual-cased-v2", model_kwargs={'device': 'cuda'})
        #vectorstore = Chroma.from_documents(documents=texts, embedding=HuggingFaceEmbeddings(model_name="distiluse-base-multilingual-cased-v2", model_kwargs={'device': 'cuda'}))
        vectorstore = Chroma.from_documents(documents=texts, embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cuda'}))
        return vectorstore
    
    def get_memory(self, conversation_id):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationBufferWindowMemory(
                k=2, memory_key="chat_history", return_messages=True
            )
        #k=2 olduğu için 2 insan 2 ai mesajı saklar
        return self.conversations[conversation_id]
    

    def answerqueryfromdocument(self,model="None",tempreture="None",language="None",message="None",chatid="None"):

        if message not in "None":
            self.message=message
        if language not in "None":
            self.language=language
        if model not in "None":
            self.model=model
        if tempreture not in "None":
            self.tempreture=float(tempreture)
        if chatid not in "None":
            self.chatid=chatid
        

        # Create a conversation memory with a limited window
        #memory = ConversationBufferWindowMemory(k=2, memory_key=self.chatid, return_messages=True) #2 adet insan 2 adet ai mesajı saklar
        memory =self.get_memory(self.chatid) #eğer o chatid'de geçmiş konuşma yoksa yenisini oluşturur varsa eskisini yükler
        # Create a conversational retrieval chain with memory
        qa_chain = ConversationalRetrievalChain.from_llm(
            #llm = ChatOllama(model="gemma2",temperature=0,num_ctx=200),  # We use num_ctx to limit the context size, which is similar to max_tokens in function. 
            llm = Ollama(model=self.model,temperature=self.tempreture),
            #retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),  # Limit the number of retrieved documents
            retriever=self.vectorstore.as_retriever(),
            memory=memory,
        )

        result = qa_chain.invoke({"question": self.message})
        #print(result['answer'])
        #print(result['chat_history'])
        return result
    
