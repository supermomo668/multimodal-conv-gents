import os
import yaml
import hydra
from pathlib import Path
from omegaconf import DictConfig, OmegaConf
from dotenv import load_dotenv
from typing import Sequence
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from .tools import process_search_tool, internet_search_tool
from .agents import initialize_ads_agents, create_agent_nodes
from .ontology import AgentState, ModelConfig
from agents.utils.registry import workflow_registry

from agents.ontology import configs

def load_environment_variables():
    load_dotenv()
    assert os.environ["OPENAI_API_KEY"]
    assert os.environ["TAVILY_API_KEY"]

def create_workflow(cfg: configs.ConvesrationConfig):
    """
    ConversationConfig: workflow, members, llm, tools, system_prompt
    """
    options = ["FINISH"] + cfg.agents

    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {"next": {"title": "Next", "anyOf": [{"enum": options}]}},
            "required": ["next"]
        }
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system", cfg.system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system",
         "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}"),
    ]).partial(options=str(options), members=", ".join(cfg.agents))

    rag_chain = (
        prompt | llm.bind_functions(
            functions=[function_def], function_call="route"
        ) | JsonOutputFunctionsParser()
    )

    agents = initialize_ads_agents(llm, tools)
    nodes = create_agent_nodes(agents)

    return workflow_registry(workflow)(members, nodes, rag_chain)

@hydra.main(config_path="../../conf", config_name="config")
def main(cfg: DictConfig):
    load_environment_variables()
    print(f"Configuration:{cfg}")
    
    model_cfg = cfg.model
    if model_cfg.provider == "google":
        llm = ChatGoogleGenerativeAI(model=model_cfg.model)
    else:
        llm = ChatOpenAI(model=model_cfg.model)

    tools = [TavilySearchResults(max_results=1), process_search_tool]
    agents_config = cfg.conversation.agents
    agent_names = [agent["name"] for agent in agents_config]

    # Create workflow
    workflow = create_workflow(cfg.conversation)
    graph = workflow.compile()

    message_stream = []
    for s in graph.stream(
        {
            "messages": [
                HumanMessage(
                    content=cfg.conversation.conversation_input
                )
            ],
        },
        {"recursion_limit": 150}
    ):
        message_stream.append(s)
        if not "__end__" in s:
            print(s, end="\n\n-----------------\n\n")

    # Save the conversation output to a markdown file
    output_dir = Path(cfg.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / cfg.output.file_name

    with open(output_file, "w") as f:
        for message in message_stream:
            f.write(f"{message}\n\n")

    print(f"Conversation output saved to {output_file}")

if __name__ == "__main__":
    main()