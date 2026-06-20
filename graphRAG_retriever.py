from langchain_core.runnables import Runnable
from config import vector_store, GRAPH_DECAY, INITIAL_K, FINAL_K, GRAPH_DB_LOCATION
from graph_db import GraphDB


def graphRAGRetriever(query: str) -> str:

    graph = GraphDB(GRAPH_DB_LOCATION)

    # Step 1: Vector search
    results = vector_store.similarity_search_with_relevance_scores(query, k=INITIAL_K)
    docs_by_id = {}

    # Add original matches
    for doc, score in results:
        node_id = doc.metadata["id"]
        docs_by_id[node_id] = {"doc": doc, "score": score}

    # Step 2: Expand graph neighbors
    for doc, score in results:

        node_id = doc.metadata["id"]
        neighbors = graph.fetchConnections(node_id)
        for neighbor_id in neighbors:

            # Ghost node
            try:
                neighbor_doc = vector_store.get_by_ids([neighbor_id])[0]
            except Exception:
                continue

            if not neighbor_id in docs_by_id.keys():
                docs_by_id[neighbor_id] = {"doc": neighbor_doc, "score": score * GRAPH_DECAY}

    # Step 3 & 4: rerank and filter with threshold
    ranked = sorted(docs_by_id.values(), key=lambda x: x["score"], reverse=True)
    ranked = ranked[: FINAL_K]

    # Step 5: context
    context = "\n\n".join(item["doc"].page_content for item in ranked)
    return context
