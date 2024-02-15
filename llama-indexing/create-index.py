from openai import OpenAI
from llama_index.llms import OpenAI
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, ServiceContext, set_global_service_context, download_loader
from llama_index.embeddings import OpenAIEmbedding
from IPython.display import Markdown, display
import gradio as gr
import os
from pathlib import Path
from llama_hub.youtube_transcript import YoutubeTranscriptReader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

# load the api key
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])


def create_index():

    print("loading the indexes")
    # load pdf, texts documents
    totalDocuments = []
    documents = SimpleDirectoryReader("./data/Training_data").load_data()
    totalDocuments.extend(documents)

    # load image json metadata
    JSONReader = download_loader("JSONReader")
    loader = JSONReader()
    images_paths = fetch_files_with_path("./data/Training_images",["jsonl"])
    for image_path in images_paths:
        isJsonl = image_path.endswith("jsonl")
        jsonDoc = loader.load_data(Path(image_path), is_jsonl=isJsonl)
        totalDocuments.extend(jsonDoc)

    # crawl static qapita websites
    SimpleWebPageReader = download_loader("SimpleWebPageReader")
    loader = SimpleWebPageReader()
    crawledDocs = loader.load_data(urls=["https://www.qapita.com/products/advisory-consulting",
    "https://www.qapita.com/products/valuations",
    "https://www.qapita.com/blogs",
    "https://www.qapita.com/open-source-resource",
    "https://www.qapita.com/products",
    "https://www.qapita.com/about",
    "https://www.qapita.com/products/equity-awards",
    "https://www.qapita.com/products/captable",
    "https://www.qapita.com",
    "https://qapita-fintech.freshdesk.com/support/home",
    "https://qapita-fintech.freshdesk.com/support/solutions/72000225115"])

    totalDocuments.extend(crawledDocs)

    # load video transcribes (should we keep this??)
    # loader = YoutubeTranscriptReader()
    # transcribeDocs = loader.load_data(ytlinks=["https://www.youtube.com/watch?v=na8Tfc644F8",
    # "https://www.youtube.com/watch?v=i99sAFAQVzs",
    # "https://www.youtube.com/watch?v=acxTObBgFKc",
    # "https://www.youtube.com/watch?v=-ybCdKtF0oA",
    # "https://www.youtube.com/watch?v=931Qi6ae088",
    # "https://www.youtube.com/watch?v=NSYSbkX72lg",
    # "https://www.youtube.com/watch?v=I49CDQVJGXA",
    # "https://www.youtube.com/watch?v=WfUzkKiRJnM",
    # "https://www.youtube.com/watch?v=ciM0w77HWaQ",
    # "https://www.youtube.com/watch?v=7kLw2lxdUTg",
    # "https://www.youtube.com/watch?v=oSLfiBccTh0",
    # "https://www.youtube.com/watch?v=AmCavk6v7YM",
    # "https://www.youtube.com/watch?v=QoYFLJvx3rQ"])

    # totalDocuments.extend(transcribeDocs)

    # change the underlying llm for llama index using service context
    openAILLM = OpenAI(model="ft:gpt-3.5-turbo-1106:personal::8rmDmwlR",temperature=0.1)
    # service_context = ServiceContext.from_defaults(llm=openAILLM, chunk_size=512,chunk_overlap=30)

    # get openai embed model
    embed_model = OpenAIEmbedding()
    # service context along with embed model, that helps find our relevance between the input query and knowledge base
    service_context = ServiceContext.from_defaults(llm=openAILLM, chunk_size=512,chunk_overlap=80, embed_model=embed_model)

    # creating vector index based on data
    # index = VectorStoreIndex.from_documents(documents)
    # OR
    index = VectorStoreIndex.from_documents(documents=totalDocuments,service_context=service_context) # index with custom openAI model

    # persist the index in storage
    index.storage_context.persist(persist_dir="./storage")

    print("loaded the indexes")


def fetch_files_with_path(directory, allowed_extensions):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            fileExtension = file.split(".", 1)
            if fileExtension in allowed_extensions:
                # Join the directory path with the file name to get the relative path
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    return file_paths


def chatbot(input_text, history=None):

    response = chain.invoke(input_text)

    print(response)
    return response.response

#create_index()

# To access the stored index
storage_context = StorageContext.from_defaults(persist_dir="./storage")

loaded_index = load_index_from_storage(storage_context=storage_context)

# create chat engine
chat_engine = loaded_index.as_retriever() # there is also something called as_query_engine

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI()
output_parser = StrOutputParser()

setup_and_retrieval = RunnableParallel(
    {"context": chat_engine, "question": RunnablePassthrough()}
)

chain = setup_and_retrieval | prompt | model | output_parser


# create ui interface to interact with gpt-3 model
# iface = gr.Interface(fn=chatbot,
#                      inputs=gr.components.Textbox(lines=7, placeholder="Enter your question here"),
#                      outputs="text",
#                      title="Qapita AI ChatBot: Your Knowledge Companion Powered-by ChatGPT",
#                      description="Ask any question about qapita's esop management platform")
# iface.launch(share=True)

iface = gr.ChatInterface(
    chatbot,
    chatbot=gr.Chatbot(height=600),
    textbox=gr.Textbox(placeholder="Ask any question about qapita", container=False, scale=7),
    title="Qapita's AI Chatbot: Saarthi",
    description="Ask any question about qapita's esop management platform to your assistant Saarthi",
    theme="base",
    retry_btn="Retry",
    undo_btn=None,
    clear_btn="Clear History"
)
iface.launch(share=True)