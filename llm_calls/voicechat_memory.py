from typing import Optional
from operator import itemgetter
from typing import List
from .voice_to_text import start_speech_to_text

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser

import torch
#from langchain.llms import HuggingFaceHub
from subprocess import call


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []
    

class Voicechat:
    def __init__(self, model="llama3.1", tempreture=0, language="Turkish",message="hi",chatid="None"):
        self.model = model
        self.tempreture = tempreture
        self.language = language
        self.message=message
        self.chatid=chatid

    def answerquery(self,model="None",tempreture="None",language="None",message="None",chatid="123",store = {},soundfileinput="None",soundfileoutput="None"):

        if soundfileinput not in "None":
            #message=start_speech_to_text(input='calis.ogg',output="calis.wav")
            pwd='145314-k'
            cmd_stop='systemctl stop ollama'
            cmd_start='systemctl start ollama'
            #ekran kartının hafızası yeterli olmadığı için ses tanıma yapılırken ollama server durdurulmak zorundadır.
            call('echo {} | sudo -S {}'.format(pwd, cmd_stop), shell=True)
            message=start_speech_to_text(input=soundfileinput,output=soundfileoutput)
            call('echo {} | sudo -S {}'.format(pwd, cmd_start), shell=True)
        if message not in "None":
            self.message=message
        if language not in "None":
            self.language=language
        if model not in "None":
            self.model=model
        if tempreture not in "None":
            self.tempreture=float(tempreture)
        if chatid not in "123":
            self.chatid=chatid
        
        llm = ChatOllama(
            model=self.model,
            #model="llama3.1",
            temperature=self.tempreture,
        )

        def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
            if session_id not in store:
                store[session_id] = InMemoryHistory()
            return store[session_id]
        
        prompt = ChatPromptTemplate.from_messages([
        ("system", "You're an assistant and answer questions only with {language} language"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
        ])

        parser = StrOutputParser()

        chain = prompt | llm | parser

        chain_with_history = RunnableWithMessageHistory(
        chain,
        # Uses the get_by_session_id function defined in the example
        # above.
        get_by_session_id,
        input_messages_key="question",
        history_messages_key="history",
        )

        result=chain_with_history.invoke(  {"language": self.language, "question": self.message},config={"configurable": {"session_id": self.chatid}})

        
        if len(store[self.chatid].messages) >= 6:
            #Eğer 6 mesaj olmuşsa geçmişi temizler
            #store.clear()
            #biz sadece belli indisleri silmek istiyoruz(0. ve 1. mesajı böylece hep 4 mesaj kayıtta kalacak
            del store[self.chatid].messages[0]
            del store[self.chatid].messages[0]
        
        del llm
        torch.cuda.empty_cache()
        return result, store
    
