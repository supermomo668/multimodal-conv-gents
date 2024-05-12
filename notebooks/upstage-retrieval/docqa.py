# pip install -U langchain-core langchain-upstage
from langchain_core.messages import HumanMessage
from langchain_upstage import ChatUpstage
from langchain_upstage import UpstageGroundednessCheck
from langchain_upstage import UpstageLayoutAnalysisLoader

# Free API keys for unlimited use. No need to register, just use ‘em!
docai_api_key = "hack-with-upstage-docai-0427"
solar_api_key = "hack-with-upstage-solar-0427"

def pdf_to_text(filenames, output_type="html"):
    chunks = UpstageLayoutAnalysisLoader(filenames,
        use_ocr=False, split="element",
        output_type=output_type, api_key=docai_api_key
    ).load()  # Should take several minutes
    return " ".join([chunk.page_content for chunk in chunks])

def ask_solar(context, question):
    chat = ChatUpstage(model="solar-1-mini-32k-chat",
                       upstage_api_key=solar_api_key)
    content = "Answer the following question:" + question \
    + "by using the following context:" + context
    answer = chat.invoke([HumanMessage(content=content)])
    return answer.content

def check_groundedness(context, question, answer):
    groundedness_check = UpstageGroundednessCheck(api_key=solar_api_key)
    response = groundedness_check.invoke(
        {"context": context, "answer": answer}
    )
    return response == "grounded"

context = pdf_to_text(["./upstage.png"])
question = "When was Upstage founded?"
answer = ask_solar(context, question)
if check_groundedness(context, question, answer):
    print(answer)
