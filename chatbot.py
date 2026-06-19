from langchain_ollama.llms import OllamaLLM
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
from dotenv import load_dotenv
import os

load_dotenv()

model = OllamaLLM(model="llama3.2")
# model = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

template = """
You are a dungeons and dragons camapaign assistant.

Some notes from the campaign: {reviews}

User's question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    print("\n\n")
    if question == "q":
        break
    
    reviews = retriever.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)