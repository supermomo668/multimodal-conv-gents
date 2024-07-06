# Multimodal Vision Agent

## Dialogue Package  [On-going]
In `dialogue/`, run pipeline by `dialogue/main.py` to execute conversation generation.
For example:
```
$projects/agent
python -m dialogue.main --config-path=../configs --config-name=default
```

### Customization Notes

**Data Preparation**: Adapt the data preparation step within `compute_vision_metrics` to convert your model’s predictions and the associated metadata (e.g., queries, goals, screenshots) into a DataFrame format compatible with `GPTVScorer`.
**Result Processing**: Customize how you process the evaluation results from `GPTVScorer` into the metrics dictionary returned by `compute_vision_metrics`, ensuring it matches the format expected by your evaluation workflow.
## Conclusion

By adapting `GPTVScorer` for use as a custom metric in Hugging Face, you can leverage its advanced vision evaluation capabilities directly within your training and evaluation pipelines. This integration enriches the feedback loop during model development, enabling a more nuanced understanding of model performance in visually-augmented tasks.