import warnings
from typing import List, Any, Optional
import asyncio
from omegaconf import DictConfig

from evaluate.evaluation_harness.utils.url import is_screenshot_url_accessible
from .gptv import GPTV
import pandas as pd
from typing import *
from tqdm.auto import tqdm

from evaluate.evaluation_harness.ontology import gptv_config
from .prompts import GPTV_EVAL_QUERY_PROMPTS, GPTV_DEFAULT_EVAL_PROMPTER, EVALUATOR_SYSTEM_PROMPT
from .chains import gptv_chain_evaluator

from evaluate.evaluation_harness.helper_functions.multion import (
  action_prefix,
  clean_extracted_text,
  extract_commands,
  extract_thought,
  extract_action,
  extract_explanation,
  ParseChatCompletion,
  extract_first
)

from evaluate.evaluation_harness.evaluators.registry import metric_registry
from evaluate.evaluation_harness.evaluators.metrics.base import DFTableScorer
from evaluate.evaluation_harness.evaluators.metrics.trajectory import BaseTrajectoryMetric

from common.evaluate.ontology import Trajectory, Observation
from evaluate.evaluation_harness.evaluators.metrics.constants import DEFAULT_INVALID_SCORE

from evaluate.evaluation_harness.ontology.gptv import gptv_chain_metric_config, GPTVDFScorerInput

@metric_registry.register('gpt-v-chain')
class GPTVChainScorer(BaseTrajectoryMetric):
    def __init__(self, config: gptv_chain_metric_config, *args, **kwargs):
        """
        Initialize the GPTVChainScorer with a configuration.

        Args:
            config (gptv_chain_metric_config): Configuration for the scoring chain.
        """
        super().__init__(config, *args, **kwargs)
        self.chain = gptv_chain_evaluator(config)

    async def _process(self, trajectory: Trajectory):
        """
        Prepare the evaluation prompt for a given trajectory.

        Args:
            trajectory (Trajectory): The trajectory data for evaluation.
        """
        self.prompt = GPTV_DEFAULT_EVAL_PROMPTER(trajectory=trajectory).create_prompt(
            GPTV_EVAL_QUERY_PROMPTS.get(self.config.prompt_version)
        )

    async def _is_valid(self, trajectory: Trajectory) -> bool:
        """
        Validate the trajectory data to ensure it contains necessary elements for processing.

        Args:
            trajectory (Trajectory): The trajectory to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        self.last_obs = trajectory.observations[-1]
        self.last_obs.__class__ = Observation
        if not trajectory.observations:
            warnings.warn("Trajectory has no observation.")
            return False
        if not is_screenshot_url_accessible(self.last_obs.screenshot):
            warnings.warn(f"Trajectory last observation screenshot: `{self.last_obs.screenshot}` is not accessible.")
        return True

    async def __call__(self, trajectory: Trajectory, *args: Any, **kwds: Any) -> GPTV:
        """
        Evaluate a single trajectory using the configured scoring chain.

        Args:
            trajectory (Trajectory): The trajectory to evaluate.

        Returns:
            Any: The result of the scoring chain invocation.
        """
        if not await self._is_valid(trajectory):
            warnings.warn("Trajectory is invalid. Continuing without all neccessary information")
        await self._process(trajectory)
        try:
          return self.chain.invoke({
              "query": self.prompt, 
              "image": self.last_obs.screenshot
          })
        except Exception as e:
          return {"error": f"error from evaluation agent: {str(e)}"}

    async def evaluate_trajectories(self, trajectories: List[Trajectory]) -> List[Optional[Any]]:
        """
        Evaluate a list of trajectories asynchronously.

        Args:
            trajectories (List[Trajectory]): A list of trajectories to evaluate.

        Returns:
            List[Optional[Any]]: A list of results for each trajectory, corresponding to the order in the input list.
        """
        # Create a tqdm progress bar
        pbar = tqdm(total=len(trajectories), desc="Evaluating Trajectories")
        async def process_with_progress(trajectory):
          result = await self(trajectory)
          pbar.update(1)  
          # Update the progress bar for each completed task
          return result
        # Create tasks using the wrapped function
        tasks = [process_with_progress(trajectory) for trajectory in trajectories]
        result = await asyncio.gather(*tasks)
        pbar.close()
        return result 
      
@metric_registry.register('gpt-v')
class GPTVScorer(BaseTrajectoryMetric):
    def __init__(self, config: DictConfig, *args, **kwargs):
        """
            A description of the entire function, its parameters, and its return types.
        """
        super().__init__(config, *args, **kwargs)
        if not args:
          self.gptv = GPTV(gptv_config)
        else: 
          self.gptv = GPTV(**config)
    
    @property
    def eval_prompt(self):
      # Custom logic to generate a dynamic prompt based on the given objective
      # field involved:
        # QUERY
        # GOAL
      prompt_ver =self.config.get('PROMPT_VERSION', 'DEFAULT')
      return GPTV_EVAL_QUERY_PROMPTS[prompt_ver]
    
    def _is_valid(self, trajectory):
      """
      Extract and process the last or all observations from a trajectory based on config.
      """
      assert is_screenshot_url_accessible(self.last_obs.url)
    
    def _synthesize_and_evaluate(self, trajectory):
      """
      Combines prompt synthesis, model generation, and result processing for a single row.
      """   
      # Synthesize evaluation prompt
      eval_prompt_args = {
        "GOAL": extract_thought(self.last_obs.prompt),
        "QUERY": extract_commands(self.last_obs.prompt)
      }
      eval_prompt = self.eval_prompt.format(**eval_prompt_args)
      # Generate model completion (assuming this function takes named arguments for text and image)
      completion = self.gptv.generate_completion(
        text=eval_prompt, images=self.last_obs.images)
      
      # Process and split the completion into Score and Explanation
      score, explanation = completion.split('\n', 1)
      score = extract_first(score, 'SCORE')
      explanation = extract_first(
        explanation, 'EXPLANATION')
      return pd.Series({
        'Score': score, 
        'Explanation': explanation
        })
    
    def evaluate(self):
      return self._synthesize_and_evaluate(
        self.last_obs.prompt
        )
    
    def _process_result(self, evals):
      return evals['Score'].mean()
    
    def __call__(
      self, trajectory: Trajectory, *args: Any, **kwds: Any
      ) -> Any:
      self._process(trajectory)
      self.evals = self.evaluate()
      return self._process_result(self.evals)
    

@metric_registry.register('gpt-v_df')
class GPTVDFScorer(DFTableScorer):
    def __init__(self, config: DictConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        if not args:
          self.gptv = GPTV(gptv_config)
        else: 
          self.gptv = GPTV(**config)
        self.config = config
    
    def _process(self):
      self.required_cols = ["QUERY", "screenshot", "GOAL"]
      assert all([c in self.input_df.columns for c in self.required_cols]), f"Missing all required columns: {self.required_cols}"
      tqdm.pandas(desc='Determining entry eligibility')
      self.process_df = self.input_df[self.input_df.progress_apply(self._is_valid, axis=1)]
      print(f"Number of eligible rows:{len(self.process_df)}")
    
    def _is_valid(self, entry):
      return is_screenshot_url_accessible(entry)
    
    @property
    def eval_prompt(self):
      # Custom logic to generate a dynamic prompt based on the given objective
      # field involved:
        # QUERY
        # GOAL
      prompt_ver = self.config(
        self.config.get('PROMPT_VERSION', 'DEFAULT')
      )
      return GPTV_EVAL_QUERY_PROMPTS.get(prompt_ver)
    
    def _synthesize_and_evaluate(self, row):
      """
      Combines prompt synthesis, model generation, and result processing for a single row.
      """
      # Synthesize evaluation prompt
      prompt = self.eval_prompt.format(**row)
      
      # Generate model completion (assuming this function takes named arguments for text and image)
      completion = self.gptv.generate_completion(
        text=prompt, images=[row.screenshot])
      
      # Process and split the completion into Score and Explanation
      score, explanation = completion.split('\n', 1)
      score = extract_first(score, 'SCORE')
      explanation = extract_first(
        explanation, 'EXPLANATION')
      return pd.Series({
        'Score': score, 
        'Explanation': explanation
        })
    
    def evaluate(self):
      tqdm.pandas(desc='Evaluating with GPT-V')
      evals = self.process_df.progress_apply(
        self._synthesize_and_evaluate, axis=1)
      return evals

    def _process_result(self, evals):
      return evals['Score'].mean()
    
    def __call__(self, dataset: Union[GPTVDFScorerInput, pd.DataFrame], *args: Any, **kwds: Any) -> Any:
      self.input_df = dataset
      self._process()
      self.evals = self.evaluate()
      return self._process_result(self.evals)


# Example usage
if __name__ == "__main__":
    df = pd.DataFrame({
      'chat_completion_messages': [
          '{"target": "Find the product XYZ description", "QUERY": "Navigate to XYZ product page"}',
          '{"target": "Check shipping options for XYZ", "QUERY": "Go to shipping information section"}'
      ],
      'screenshot': [
          'path/to/screenshot1.jpg',
          'path/to/screenshot2.jpg'
          # paths to screenshots relevant to each chat completion message
      ],
      'inputs': [
          'User navigates to the XYZ product page to find descriptions',
          'User scrolls through the product page to check shipping options'
          # descriptions of user actions for each scenario
      ]
    })

    evaluator = GPTVScorer()

    # Running the evaluator
    evaluation_results = evaluator(df)
    for result in evaluation_results:
        print(result)
