from state.agent_state import AgentState 


def relevance_router(state: AgentState):
    if state["relevance"].lower() == "relevant":
        return "convert_to_sql"
    else:
        return "generate_funny_response"

def execute_sql_router(state: AgentState): 
    if state.get("sql_error", False): 
        return "regenerate_query"
    else: 
        return "generate_human_readable_answer"  

def check_attempts_router(state: AgentState): 
    if state.get("attempts", 0) >= state.get("max_iter", 3):
        return "end_max_iterations" 
    else: 
        return "convert_to_sql" 