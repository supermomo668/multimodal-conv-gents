# Simple Document QA demo with Upstage Full-stack LLM

These are self-contained sample snippets to get you started.

## Setup
``` bash
git clone https://gist.github.com/7329318a000330e1688409d9dc4ca781.git upstage_demo
cd upstage_demo
```

## Document QA (takes ~10 secs)


- Input (Try changing input documents and questions!)
    - Document: [upstage.png](https://gist.github.com/e9t/7329318a000330e1688409d9dc4ca781/raw/e2a6d9a98fc081fc1f9791af08fa17027cbbb4c1/upstage.png)
    - Question: "When was Upstage founded?"
- Output: Returns grounded answer, such as "Upstage was founded on October 5th, 2020." (Output may vary.)

```
pip install -U langchain-core langchain-upstage
python docqa.py
```

## Retrieval (takes ~3 mins)

- Input:
    - Single PDF document or documents. Here we download [this paper](https://www.nature.com/articles/s41467-018-04252-2) and rename it to `./crispr.pdf`.
    - Question: "What are the future directions of CRISPR?"
- Output: Returns most relevant n chunks from a Vector DB.

```
pip install -U langchain-chroma langchain-upstage
python retrieval.py
```
