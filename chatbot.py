from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from graphRAG_retriever import graphRAGRetriever

from dotenv import load_dotenv
import os

load_dotenv()

# -----------------------------
# LLM
# -----------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
)

# -----------------------------
# Retriever
# -----------------------------

retriever = RunnableLambda(lambda x: graphRAGRetriever(x['question']))

# -----------------------------
# Prompt
# -----------------------------

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a Dungeons & Dragons campaign assistant.
            Use the campaign notes to answer questions.
            If the answer is not contained in the notes, say so instead of inventing lore.

            Campaign Notes:
            {context}
            """,
        ),
        ("human", "{question}"),
    ]
)

# -----------------------------
# Retrieval Chain
# -----------------------------

retrieval_chain = RunnableParallel(
    {
        "question": RunnablePassthrough(),
        "context": retriever,
    }
)

chain = retrieval_chain | prompt | llm | StrOutputParser()

# -----------------------------
# Chat Loop
# -----------------------------

while (question := input("\nAsk your question (q to quit): ")) != "q":
    print("\nAssistant:")
    print(chain.invoke({"question": question}))