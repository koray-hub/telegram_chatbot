from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

class Voicechat:
    def __init__(self, model="llama3.1", tempreture=0, language="Turkish", soundfilename="None",message="hi",chatid="None"):
        self.model = model
        self.tempreture = tempreture
        self.soundfilename = soundfilename
        self.language = language
        self.message=message
        self.chatid=chatid

    def answerquery(self,model="None",tempreture="None",language="None",soundfilename="None",message="None"):
        if soundfilename not in "None":
            self.soundfilename=soundfilename
        if message not in "None":
            self.message=message
        if language not in "None":
            self.language=language
        if model not in "None":
            self.model=model
        if tempreture not in "None":
            self.tempreture=float(tempreture)
        
        model = ChatOllama(
            model=self.model,
            #model="llama3.1",
            temperature=self.tempreture,
        )

        # system_template = "Translate the following into {language} and answer only with translation."
        system_template = "Answer only with {language} language"
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text}")]
        )

        parser = StrOutputParser()
        chain = prompt_template | model | parser

        result=chain.invoke({"language": self.language, "text": self.message})
        return result