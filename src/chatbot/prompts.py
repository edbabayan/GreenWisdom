class MultiAgentPrompts:
    contextualization_prompt = """
    Given the chat history and the latest user query, translate the query to English if needed and then formulate a 
    standalone question that can be understood without the chat history. Do NOT answer the question, just reformulate
    it if needed and otherwise return it as is.
    """