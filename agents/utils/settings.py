"""
Configure settings
"""
def get_proxy_agent_settings():
  return {
    'human_input_mode': 'NEVER',
    'is_termination_msg' : lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    'code_execution_config': {
      "last_n_messages": 3,
      'work_dir': 'agent_output', 
      'use_docker': False
    }
    
  }
  
def get_state_transitionfunc():
  def state_transition(last_speaker, groupchat):
    messages = groupchat.messages

    if last_speaker is initializer:
        # init -> retrieve
        return coder
    elif last_speaker is coder:
        # retrieve: action 1 -> action 2
        return executor
    elif last_speaker is executor:
        if messages[-1]["content"] == "exitcode: 1":
            # retrieve --(execution failed)--> retrieve
            return coder
        else:
            # retrieve --(execution success)--> research
            return scientist
    elif last_speaker == "Scientist":
        # research -> end
        return None