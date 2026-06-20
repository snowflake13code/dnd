from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableBranch

from .graphRAG_retriever import graphRAGRetriever, sessionRetriever, arcRetriever
from .models import QueryRoute
from .prompts import router_prompt, assistant_prompt, samael_prompt, lucifer_prompt, default_council_prompt, argue_council_prompt, funny_council_prompt

from .config import JSON_STATE_LOCATION
from dotenv import load_dotenv

import os
import json
import random

load_dotenv()


class chatBot():
    def __init__(self):
        
        # STATE
        def get_campaign_state():
            with open(JSON_STATE_LOCATION) as f:
                return json.load(f)

        # LLM
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
        )

        router_llm = llm.with_structured_output(QueryRoute)
         
        # ROUTER
        router_chain = router_prompt | router_llm

        # RETRIEVAL LAYER (normalized output)         
        retrieval_router = RunnableBranch(
            (lambda x: x["route"].route == "story", RunnableLambda(lambda x: graphRAGRetriever(x['question']))),
            (lambda x: x["route"].route == "session", RunnableLambda(lambda x: sessionRetriever(str(x['route'].arc), str(x['route'].session)))),
            (lambda x: x["route"].route == "arc", RunnableLambda(lambda x: arcRetriever(str(x['route'].arc)))),
            RunnableLambda(lambda x: graphRAGRetriever(x['question'])),
        )

        # COUNCIL PROMPT SELECTION (isolated logic)
        def pick_council_prompt():
            r = random.random()
            if r < 0.6:
                return default_council_prompt
            elif r < 0.85:
                return argue_council_prompt
            return funny_council_prompt

        # PROMPT BUILDER (single unified layer)
        # Ensures all personas receive same schema:
        # {
        #   question,
        #   context,
        #   route,
        #   latest_arc,
        #   latest_session
        # }
         
        def build_prompt(input_data):
            persona = input_data["persona"]

            if persona == "assistant":
                return assistant_prompt
            if persona == "samael":
                return samael_prompt
            if persona == "lucifer":
                return lucifer_prompt
            if persona == "council":
                return pick_council_prompt()

            return assistant_prompt
        prompt_router = RunnableLambda(build_prompt)

        # FINAL RESPONSE CHAIN
        self.chain = (
            RunnablePassthrough()
            .assign(
                latest_arc=lambda _: get_campaign_state()["latest_arc"],
                latest_session=lambda _: get_campaign_state()["latest_session"],
            )
            .assign(route=router_chain)
            .assign(context=retrieval_router)
            .assign(prompt=prompt_router)
            | RunnableLambda(
                lambda x: (llm | StrOutputParser()).invoke(x["prompt"])
            )
        )

    def ask(self, question: str, persona: str):

        response = self.chain.invoke({
            "question": question,
            "persona": persona,
        })
        print(response)

    def newChat(self):
        pass