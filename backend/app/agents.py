from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict, total=False):
    question: str
    tenant_id: str
    source_count: int
    answer: str
    status: str
    trace: list[str]

def catalog(state: State):
    return {"trace": ["catalog"]}

def clarify(state: State):
    message = ("Conecte e sincronize uma fonte antes de consultar os dados."
               if state.get("source_count", 0) == 0 else
               "Sua fonte foi cadastrada. A execução analítica depende da sincronização, "
               "do catálogo semântico e do provedor de IA, previstos no roadmap.")
    return {"answer": message, "status": "needs_setup", "trace": state["trace"] + ["clarify"]}

def build_graph():
    graph = StateGraph(State)
    graph.add_node("catalog", catalog)
    graph.add_node("clarify", clarify)
    graph.add_edge(START, "catalog")
    graph.add_edge("catalog", "clarify")
    graph.add_edge("clarify", END)
    return graph.compile()

graph = build_graph()
