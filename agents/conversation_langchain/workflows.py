
from langgraph.graph import StateGraph, END


from .ontology import AgentState


from utils.registry import workflow_registry

@workflow_registry.reegister("ads")  
def ads_workflow(members, nodes, rag_chain):
  workflow = StateGraph(AgentState)
  workflow.add_node("supervisor", action=rag_chain)
  for name, node in nodes.items():
      workflow.add_node(name, action=node)

  for member in members:
      workflow.add_edge(start_key=member, end_key="supervisor")

  conditional_map = {k: k for k in members}
  conditional_map['FINISH'] = END

  workflow.add_conditional_edges(
      "supervisor", lambda x: x["next"], conditional_map)
  workflow.set_entry_point("supervisor")

  