from .config import vector_store, GRAPH_DECAY, INITIAL_K, FINAL_K, GRAPH_DB_LOCATION
from .graph_db import GraphDB
from .logger_config import logger


def graphRAGRetriever(query: str) -> dict:

    # Log the route
    logger.info('story route: graphRAGRetriever() called')

    graph = GraphDB(GRAPH_DB_LOCATION)

    # Step 1: Vector search
    results = vector_store.similarity_search_with_relevance_scores(query, k=INITIAL_K)
    docs_by_id = {}

    # Add original matches
    for doc, score in results:
        node_id = doc.metadata["id"]
        docs_by_id[node_id] = {"doc": doc, "score": score}
    logger.info(f'Documents added: {docs_by_id.keys()}')

    # Step 2: Expand graph neighbors
    for doc, score in results:

        node_id = doc.metadata["id"]
        neighbors = graph.fetchConnections(node_id)
        all_neighbours = []
        for neighbor_id in neighbors:

            # Ghost node
            try:
                neighbor_doc = vector_store.get_by_ids([neighbor_id])[0]
            except Exception:
                continue

            if not neighbor_id in docs_by_id.keys():
                docs_by_id[neighbor_id] = {"doc": neighbor_doc, "score": score * GRAPH_DECAY}
                all_neighbours.append(neighbor_id)
        logger.info(f'Neighbour nodes for {node_id} -> {all_neighbours}')

    # Step 3 & 4: rerank and filter with threshold
    ranked = sorted(docs_by_id.values(), key=lambda x: x["score"], reverse=True)
    ranked = ranked[: FINAL_K]
    logger.info(f'Reranked documents: {ranked}')

    # Step 5: context
    context = "\n\n".join(item["doc"].page_content for item in ranked)
    return {"context": context}

def sessionRetriever(arc_num: str, session_num: str) -> str:

    # Log the route
    logger.info(f'story route: sessionRetriever() called, arc: {arc_num}, session: {session_num}')

    # Get the content of the last session
    result = vector_store.get(where={"$and": [{"arc": arc_num}, {"session": session_num}]})

    # Sort the content by scene ID
    docs = list(zip(result["metadatas"], result["documents"]))
    docs.sort(key=lambda x: int(x[0].get("scene", 0)))
    logger.info(f'Documents fetched = {len(docs)}')

    # Convert the content into a single string
    response = "\n\n".join(content for _, content in docs)
    return {'context': response}

def arcRetriever(arc_num: str) -> str:
    
    # Log the route
    logger.info(f'story route: arcRetriever() called, arc: {arc_num}')

    # Get the content of the last session
    result = vector_store.get(where={"arc": arc_num})

    # Sort the content by scene ID
    docs = list(zip(result["metadatas"], result["documents"]))
    docs.sort(key=lambda x: (int(x[0].get("session", 0)), int(x[0].get("scene", 0))))
    logger.info(f'Documents fetched = {len(docs)}')

    # Convert the content into a single string
    response = "\n\n".join(content for _, content in docs)
    return {'context': response}
