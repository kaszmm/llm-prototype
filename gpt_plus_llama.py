import os

os.environ["OPENAI_API_KEY"] = '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'

from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, LLMPredictor, ServiceContext, PromptHelper, StorageContext, load_index_from_storage
from langchain_community.chat_models import ChatOpenAI
import gradio as gr
import sys

def init_index(directory_path):
    # model params
    # max_input_size: maximum size of input text for the model.
    # num_outputs: number of output tokens to generate.
    # max_chunk_overlap: maximum overlap allowed between text chunks.
    # chunk_size_limit: limit on the size of each text chunk.
    max_input_size = 4096
    num_outputs = 512
    max_chunk_overlap = 0.5
    chunk_size_limit = 600

    # llm predictor with langchain ChatOpenAI
    # ChatOpenAI model is a part of the LangChain library and is used to interact with the GPT-3.5-turbo model provided by OpenAI
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo", max_tokens=num_outputs))

    # read documents from docs folder
    documents = SimpleDirectoryReader(directory_path).load_data()

    # init index with documents data
    # This index is created using the LlamaIndex library. It processes the document content and constructs the index to facilitate efficient querying
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

    # save the created index
    index.storage_context.persist(persist_dir='./storage')

    return index

def chatbot(input_text):
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir='./storage')
    
    # load index
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine()
    
    # get response for the question
    response = query_engine.query(input_text)

    return response.response

# create index
init_index("docs")

# create ui interface to interact with gpt-3 model
iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, placeholder="Enter your question here"),
                     outputs="text",
                     title="Frost AI ChatBot: Your Knowledge Companion Powered-by ChatGPT",
                     description="Ask any question about rahasak research papers")
iface.launch(share=True)