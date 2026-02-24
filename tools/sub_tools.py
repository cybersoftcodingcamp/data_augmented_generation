from state.agent_state import AgentState 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser 
from models.llm_gpt import llm 


def generate_funny_response(state: AgentState):
    print("Generating a funny response for an unrelated question.")
    system = """You are a charming and funny assistant who responds in a playful manner.
    """
    human_message = "I can not help with that, but doesn't asking questions make you come closer to the problem? You can always revise the data."
    funny_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", human_message),
        ]
    )
    # llm = ChatOpenAI(temperature=0.7)
    funny_response = funny_prompt | llm | StrOutputParser()
    message = funny_response.invoke({})
    state["query_result"] = message
    print("Generated funny response.")
    return state


def end_max_iterations(state: AgentState): 
    state["query_result"] = "Please try again" 
    return state 