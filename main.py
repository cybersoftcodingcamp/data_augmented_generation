import streamlit as st 
from dotenv import load_dotenv 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from tools.schema_tools import get_database_schema 
# from graph.main_workflow import app 
from tools.chart_tools import drawing_chart
from langgraph.graph import StateGraph, END 
from tools.agent_tools import * 
from tools.sub_tools import *
from routers.agent_routers import * 
from state.agent_state import AgentState


workflow = StateGraph(AgentState)

workflow.add_node("check_relevance", check_relevance)
workflow.add_node("convert_to_sql", convert_to_sql)
workflow.add_node("generate_funny_response", generate_funny_response)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_human_readable_answer", generate_human_readable_answer) 
workflow.add_node("regenerate_query", regenerate_query) 
workflow.add_node("end_max_iterations", end_max_iterations) 

workflow.add_conditional_edges(
    "check_relevance",
    relevance_router,
    {
        "convert_to_sql": "convert_to_sql",
        "generate_funny_response": "generate_funny_response"
    }
)

workflow.add_edge("convert_to_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql", 
    execute_sql_router, 
    {
        "regenerate_query": "regenerate_query",
        "generate_human_readable_answer": "generate_human_readable_answer"
    }
)

workflow.add_conditional_edges(
    "regenerate_query", 
    check_attempts_router, 
    {
        "convert_to_sql": "convert_to_sql", 
        "end_max_iterations": "end_max_iterations" 
    }
)

workflow.add_edge("generate_funny_response", END)
workflow.add_edge("end_max_iterations", END)
workflow.add_edge("generate_human_readable_answer", END)

workflow.set_entry_point("check_relevance")
app = workflow.compile()

st.set_page_config(page_title="Data Analysis Agent", page_icon=":robot_face:", layout="wide")
# Initialize session state 
if "schema" not in st.session_state: 
    st.session_state.schema = None 
if "engine" not in st.session_state: 
    st.session_state.engine = None 
if "SessionLocal" not in st.session_state: 
    st.session_state.SessionLocal = None 
    
    
# Sidebar for database connection
st.sidebar.header("Database Connection")
db_type = st.sidebar.selectbox("Database Type", ["postgresql", "mysql"])
host = st.sidebar.text_input("Host", value="localhost")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
port = st.sidebar.text_input("Port")
database = st.sidebar.text_input("Database Name")

# Button to connect to database
if st.sidebar.button("Connect to Database"):
    try:
        if db_type == "postgresql":
            db_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "mysql":
            db_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

        # Create engine and session
        st.session_state.engine = create_engine(db_url)
        st.session_state.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=st.session_state.engine)

        st.session_state.schema = get_database_schema(st.session_state.engine)
        st.sidebar.success("Connected to database and schema retrieved!")
    except Exception as e:
        st.sidebar.error(f"Failed to connect: {str(e)}")

# Main interface
st.title("🤖 Database Query Assistant")

# Query input
if st.session_state.schema:
    question = st.text_input("Enter your question:")
    if st.button("Submit Question") and question:
        with st.spinner("Processing your question..."):
            initial_state = {
                "question": question,
                "sql_query": "",
                "query_result": "",
                "query_rows": [],
                "attempts": 0,
                "relevance": "",
                "sql_error": False
            }
            result = app.invoke(initial_state)

            # Display results
            st.subheader("Results")
            st.write("*Query Result:*")
            st.write(result["query_result"])

            st.write("*Query Rows:*")
            if result["query_rows"]:
                st.json(result["query_rows"])
            else:
                st.write("No rows returned.")

            # Display chart
            st.subheader("Chart")
            
            try: 
                fig = drawing_chart(question, result)
                if fig:
                    st.pyplot(fig)
                else:
                    st.write("No chart generated (no data returned).")
            except:
                st.write("No chart generated for single-column result.")
            
else:
    st.warning("Please connect to a database first using the sidebar.")