from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

class Fewshottext:
    def __init__(self, model="llama3.1", tempreture=0.0, language="Türkçe", textfile="None",message="Sen kimsin?"):
        self.model = model
        self.tempreture = tempreture
        #self.textfile = "/home/bot/Projects/qa/fewshot_learning/"+textfile+".txt"
        self.language = language
        self.message=message
        self.chain=self.process_all("/home/bot/Projects/telegram_chatbot/document_files/"+textfile+".txt")
    
    
    def parse_text_file(self,textfile):
        examples = [{"input": "Sen kimsin?", "output": "Ben hizmet etmek için tasarlanmış bir yapay zekayım."}]
        with open(textfile, 'r', encoding='UTF-8') as file:
            while line := file.readline():
                linen=line.rstrip()
                if "~" in linen:
                    input_str=linen.strip().split('~')[0]
                    output_str=linen.strip().split('~')[1]
                    examples.append({'input': input_str, 'output': output_str})
        return examples
    

    def process_all(self,textfile):
        examples = self.parse_text_file(textfile)
        to_vectorize = [" ".join(example.values()) for example in examples]
        #embeddings = HuggingFaceEmbeddings()
        embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local")
        vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=examples)

        example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore,
        k=2,
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            # The input variables select the values to pass to the example_selector
            input_variables=["input"],
            example_selector=example_selector,
            # Define how each example will be formatted.
            # In this case, each example will become 2 messages:
            # 1 human, and 1 AI
            example_prompt=ChatPromptTemplate.from_messages(
                [("human", "{input}"), ("ai", "{output}")]
            ),
        )
        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "2024 yılındayız sorumu {language} cevaplarmısın."),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )

        llm = Ollama(
            model=self.model,
            temperature=self.tempreture,
        )
        
        chain = final_prompt | llm

        return chain
    

    def answerquery(self,language="None",message="None"):
        if message not in "None":
            self.message=message
        if language not in "None":
            self.language=language
        
        result=self.chain.invoke({"input": self.message,"language": self.language})
        return result