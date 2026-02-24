from typing_extensions import TypedDict 

class AgentState(TypedDict):
    question: str
    sql_query: str
    query_result: str
    query_rows: str
    attempts: int
    relevance: str
    sql_error: bool
    max_iter: int 