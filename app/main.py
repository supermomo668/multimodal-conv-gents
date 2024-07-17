from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import subprocess
import json, os
from omegaconf import OmegaConf

app = FastAPI()

# Define a Pydantic model for input validation
class HydraConfig(BaseModel):
    param1: str
    param2: int
    # Add other parameters as needed

@app.get("/")
async def default():
    return {"message": "Hello, FiCast"}
@app.post("/run")
async def run_hydra_app(config: HydraConfig):
  try:
    # Convert Pydantic model to a dictionary
    config_dict = config.model_dump()
    
    # Convert dictionary to OmegaConf DictConfig
    hydra_conf = OmegaConf.create(config_dict)
    
    # Convert DictConfig to a JSON string
    config_json = OmegaConf.to_container(hydra_conf, resolve=True)
    config_json_str = json.dumps(config_json)
    
    # Save the configuration to a temporary file
    with open("temp_config.json", "w") as temp_config_file:
        temp_config_file.write(config_json_str)
    
    # Run the Hydra application with the temporary config file
    result = subprocess.run(
        ["python", "-m", "agents.dialogue.main", "hydra.run.dir=temp_config"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(result.stderr)
    
    return {"message": "Hydra application executed successfully", "output": result.stdout}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-script")
async def get_test_script():
    try:
        # Define the path to the JSON file
        json_file_path = "outputs/conversations/script_json_20240715_214605.json"
        
        # Check if the file exists
        if not os.path.exists(json_file_path):
            raise HTTPException(status_code=404, detail="JSON file not found")
        
        # Read the JSON file
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
        
        # Extract the "podcast" data
        podcast_data = data.get("podcast")
        
        # Check if the "podcast" data exists
        if podcast_data is None:
            raise HTTPException(status_code=404, detail="'podcast' data not found in the JSON file")
        
        return {"podcast": podcast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
