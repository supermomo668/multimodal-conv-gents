from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate

map_prompt_template = ChatPromptTemplate(
  messages=[HumanMessagePromptTemplate(prompt=PromptTemplate(
    template = 'The following is a set of documents:\n{docs}\nBased on this list of docs, please identify the main themes \nHelpful Answer:',
    input_variables=['doc_summaries']
  ))], 
  input_variables=['doc_summaries'],
)

reduce_prompt_template = ChatPromptTemplate(
  messages=[HumanMessagePromptTemplate(prompt=PromptTemplate(
    template = """
    The following is set of summaries:
    {doc_summaries}
    Take these and distill it into a comprehensive and detailed summary.
    Helpful Answer:
    """,
    input_variables=['doc_summaries']
  ))], 
  input_variables=['doc_summaries'],
)

