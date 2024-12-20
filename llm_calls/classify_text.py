
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

class Classification(BaseModel):
    sentiment: str = Field(..., enum=["happy", "neutral", "sad"])
    aggressiveness: int = Field(
        ...,
        description="describes how aggressive the statement is, the higher the number the more aggressive",
        enum=["1", "2", "3", "4", "5"],
    )
    language: str = Field(
        ..., enum=["spanish", "english", "french", "german", "italian","turkish"]
    )

class Classify_text:
    def __init__(self, model="llama3.1", tempreture=0,message="hi"):
        self.model = model
        self.tempreture = tempreture
        self.message=message

    def answerquery(self,model="None",tempreture="None",message="None"):

        if message not in "None":
            self.message=message
        if model not in "None":
            self.model=model
        if tempreture not in "None":
            self.tempreture=float(tempreture)

        
        llm = ChatOllama(
            model=self.model,
            #model="llama3.1",
            temperature=self.tempreture,
        ).with_structured_output(Classification)


        tagging_prompt = ChatPromptTemplate.from_template(
            """
        Extract the desired information from the following passage.

        Only extract the properties mentioned in the 'Classification' function.

        Passage:
        {input}
        """
        )

        tagging_chain = tagging_prompt | llm 

        result=tagging_chain.invoke({"input": self.message})

        # sentiment = result.sentiment
        # aggressiveness = result.aggressiveness
        # language = result.language

        # print(sentiment, aggressiveness, language)

        return result
    
