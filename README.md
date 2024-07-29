# Multimodal Thoughtful Conversation Agents

![Publish to TestPyPI](https://github.com/supermomo668/multimodal-conv-agents/actions/workflows/publish-testpypi.yml/badge.svg)

# Sections
In `thought_agents/`, the following main modules are available:
* dialogue
  * web tools 
* vision (gpt-vision) evaluator

## Dialogue
 run pipeline by `dialogue/main.py` to execute conversation generation.
For example:
```
$projects/agent
python -m dialogue.main --config-path=../configs --config-name=default
```

## GPT-Vision for Thoughtful structured evaluation

Leverage `vision.gptv.main` for evaluating task completion with custom images and/or textual inputs. Scoring rubrics are defined in `vision/metric` as pydantic base classes.
Adding `Field` description for the Field data will enable evaluation to be generated on those rubrics.

  ### Customization Notes

  **Data Preparation**: Adapt the data preparation step within `compute_vision_metrics` to convert your model’s predictions and the associated metadata (e.g., queries, goals, screenshots) into a DataFrame format compatible with `GPTVScorer`.
  **Result Processing**: Customize how you process the evaluation results from `GPTVScorer` into the metrics dictionary returned by `compute_vision_metrics`, ensuring it matches the format expected by your evaluation workflow.
  ## Conclusion

  By adapting `GPTVScorer` for use as a custom metric in Hugging Face, you can leverage its advanced vision evaluation capabilities directly within your training and evaluation pipelines. This integration enriches the feedback loop during model development, enabling a more nuanced understanding of model performance in visually-augmented tasks.