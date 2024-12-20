
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional

class Person(BaseModel):
    """Information about a person."""

    # ^ Doc-string for the entity Person.
    # This doc-string is sent to the LLM as the description of the schema Person,
    # and it can help to improve extraction results.

    # Note that:
    # 1. Each field is an `optional` -- this allows the model to decline to extract it!
    # 2. Each field has a `description` -- this description is used by the LLM.
    # Having a good description can help improve extraction results.
    name: Optional[str] = Field(default=None, description="The name of the person")
    hair_color: Optional[str] = Field(
        default=None, description="The color of the person's hair if known"
    )
    height_in_meters: Optional[str] = Field(
        default=None, description="Height measured in meters"
    )

class Extract_text:
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
        ).with_structured_output(schema=Person)


        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert extraction algorithm. "
                    "Only extract relevant information from the text. "
                    "If you do not know the value of an attribute asked to extract, "
                    "return null for the attribute's value.",
                ),
                # Please see the how-to about improving performance with
                # reference examples.
                # MessagesPlaceholder('examples'),
                ("human", "{text}"),
            ]
        )

        runnable = prompt | llm 

        result=runnable.invoke({"text": self.message})

        # sentiment = result.sentiment
        # aggressiveness = result.aggressiveness
        # language = result.language

        # print(sentiment, aggressiveness, language)

        return result
    
