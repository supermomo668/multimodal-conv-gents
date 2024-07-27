def generate_llm_config(tool):
    # Define the function schema based on the tool's args_schema
    """
    use as such:llm_config = {
        "functions": [
            generate_llm_config(YOUR_TOOL),
        ],
        "config_list": config_list,  # Assuming you have this defined elsewhere
        "timeout": 120,
    }
    """
    function_schema = {
        "name": tool.name.lower().replace(" ", "_"),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args
    return function_schema
  