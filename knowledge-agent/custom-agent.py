from langchain.agents import load_tools, initialize_agent, AgentType, create_openai_tools_agent, AgentExecutor
from langchain.tools import BaseTool, StructuredTool
from openai import OpenAI
import requests
import os
import json
from langchain.pydantic_v1 import BaseModel, Field
from typing import Type
from langchain_openai import ChatOpenAI
import gradio as gr
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)

class CreateStakeholderInput(BaseModel):
    """Inputs for creating the stakeholder in qapita platform"""

    legal_name :str = Field(description="""Legal name of the stakeholder, 
    or if not provided it will be combination of first name and last name of the stakeholder""")
    first_name :str = Field(description="First name of the stakeholder")
    last_name :str = Field(description="Last name of the stakeholder")
    stakeholder_type :str = Field(default="Individual",description="[OPTIONAL]Type of the stakeholder that user wants to create, the only valid options are 'Individual' and 'Institution', if no type provided use 'Individual' as stakeholder_type")
    is_employee :bool = Field(default=False, description="[OPTIONAL]Provides whether the stakholder is an employee or not, If not provided consider it to be False")
    issuerEmployeeId :str = Field(default=None, description="[OPTIONAL]Represent the employee Id of a stakeholder, this will be a required field only if the stakeholder is an employee aka is_employee is True")

def is_string_null_empty_or_whitespace(s):
    return s is None or s.strip() == ''

def create_stakeholder(legal_name:str,first_name:str,last_name:str, stakeholder_type:str="Individual", is_employee:bool=False, issuerEmployeeId:str=""):
    """Creates a stakeholder in qapita platform."""

    if is_employee and is_string_null_empty_or_whitespace(issuerEmployeeId):
        return {
            "statusCode":400,
            "errorMessage": "If stakeholder is an employee then the issuer employee id is required as well."
        }
    
    if stakeholder_type.lower() != "individual" and stakeholder_type.lower() != "institution":
        return {
            "statusCode":400,
            "errorMessage": "Invalid Stakeholder type was provided the only valid options are 'Individual' or 'Institution'"
        }

    individual_data = {
            "issuerId": 1,
            "legalName": legal_name,
            "primaryContact": {
                "firstName": first_name,
                "lastName": last_name,
                "email": "",
                "secondaryEmail": "",
                "mobileNumbers": None,
                "primaryMobileNumber": None
            },
            "address": None,
            "primaryBankAccount": None,
            "personalIds": [],
            "isEmployee": is_employee,
            "issuerEmployeeId": issuerEmployeeId,
            "dateOfBirth": None,
            "commencementDate": None,
            "customFields": [
                {
                    "fieldDefinitionId": 54,
                    "dataType": "Text",
                    "documentName": None,
                    "value": None
                },
                {
                    "fieldDefinitionId": 2410,
                    "dataType": "Date",
                    "documentName": None,
                    "value": None
                },
                {
                    "fieldDefinitionId": 2405,
                    "dataType": "Number",
                    "documentName": None,
                    "value": None
                },
                {
                    "fieldDefinitionId": 2407,
                    "dataType": "Text",
                    "documentName": None,
                    "value": None
                }
            ],
            "dematAccounts": [],
            "taxId": None,
            "nationality": None,
            "stakeholderType": stakeholder_type,
            "documents": [],
            "nominees": [],
            "employmentHistory": []
    }

    institutional_data = {
        "legalName": legal_name,
        "primaryContact": {
            "firstName": first_name,
            "lastName": last_name,
            "email": ""
        },
        "issuerId": 1,
        "issuerEmployeeId": "",
        "customFields": [],
        "taxId": "",
        "stakeholderType": "Institution"
    }

    data = individual_data
    if stakeholder_type.lower() == "institution":
        data = institutional_data

    headers = {
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjU2QzdBQ0Y1QzAxMTE1RThBNDMxODg5QzNBRkU1MzcwIiwidHlwIjoiYXQrand0In0.eyJpc3MiOiJodHRwczovL2F1dGgucWFwaXRhLmRldiIsIm5iZiI6MTcwNzgwMzAwNCwiaWF0IjoxNzA3ODAzMDA0LCJleHAiOjE3MDc4MDY2MDQsImF1ZCI6WyJxYXBpdGEuY2FwaXRhbGl6YXRpb24iLCJodHRwczovL2F1dGgucWFwaXRhLmRldi9yZXNvdXJjZXMiXSwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsImFkZHJlc3MiLCJlbWFpbCIsInJvbGVzIiwicWFwaXRhLmNhcGl0YWxpemF0aW9uIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbInB3ZCJdLCJjbGllbnRfaWQiOiJxYXBpdGEucW1hcC51YXQud2ViLnVpIiwic3ViIjoiOWFjNTU3ZTMtNTNiNy00OTA2LThmZjctMjQwMjA2MTBmNzEwIiwiYXV0aF90aW1lIjoxNzA3MjAyOTEzLCJpZHAiOiJsb2NhbCIsImxhc3RfbG9naW4iOjE3MDc4MDIxMDksImxhc3RfbG9nb3V0IjoxNzA3ODAxODI5LCJlbWFpbCI6Inlhc2h3YW50aC5wdXR0YUBxYXBpdGFjb3JwLmNvbSIsIm5hbWUiOiJZYXNod2FudGggUHV0dGEiLCJnaXZlbl9uYW1lIjoiWWFzaHdhbnRoIiwiZmFtaWx5X25hbWUiOiJQdXR0YSIsInJvbGUiOiJBZG1pbmlzdHJhdG9yIn0.m9LQoB8df79dcYNPQTNjCA0Ukw80whn1dGpp7eLYLi9lX4Tv7GLzzoWjfrba_cY743oqV3MDCXCA-nlKB6XPe2rEKegcINW18eSEsbGaT4ZVH0KAyP-TC8t0OJZR7JkBGJNLN90qo8Yx_ihimHwE8ed6JOJJIe23_JsHTjg5EF8vQtwUdIvQM6-tnT2FGvFm2bkWNshykRWo2NN_CGIp_f89fgNDSzuAYYa9o9rjq1RAK3KMy7HdM04E8NhSPFKaDmFCLeJSTHjakYZ4hQDVuemUF6KAXvZO4WvDWePYYnnkm0nsZAqR89JnqJ1RqskFtLd8tmAl0jf3VRqrZUwIHw',  
            'Content-Type': 'application/json'
    }

    response = requests.put("https://captableuat.qapita.dev/api/v2/issuers/1/register-stakeholder", json=data, headers=headers)
    if response.status_code == 200:
        print('Success:', response.json())
    else:
        print('An error occurred:', response.text)

    return response.json()

create_stakeholder_tool = StructuredTool.from_function(
    func=create_stakeholder,
    name = "create_stakeholder_tool",
    description="""This tool can be used to create the stakeholder in qapita platform.
    This tool requires legal name, first and last name of the stakeholder in order to create a stakeholder.
    If legal name not provided and stakeholder full name is provided then use the full name as legal name and pick the first and last name from the full name provided.
    """,
    args_schema=CreateStakeholderInput,
    return_direct=False
)

langchainLlm = ChatOpenAI(model="ft:gpt-3.5-turbo-0613:personal::8q3apor4",temperature=0.2, streaming=True)

sytem_template ="""You are a helpful assitant who can do all sort of actions like creating a stakeholder and other function callings."""
human_template = "{input}"
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(sytem_template),
        MessagesPlaceholder(variable_name="chat_history",optional=True),
        HumanMessagePromptTemplate.from_template(input_variables=["input"], template=human_template),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

tools = [create_stakeholder_tool] 

agent = create_openai_tools_agent(langchainLlm,tools,prompt)
agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True)

message_history = ChatMessageHistory()
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: message_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
def execute_task(input_text):
    response = agent_with_chat_history.invoke({"input": input_text} , config={"configurable": {"session_id": "<foo>"}})
    print(response)
    return response["output"]

# create ui interface to interact with gpt-3 model
iface = gr.Interface(fn=execute_task,
                     inputs=gr.components.Textbox(lines=7, placeholder="Enter your execution here"),
                     outputs="text",
                     title="Qapita AI ChatBot: Your Knowledge Companion Powered-by ChatGPT",
                     description="Execute the any task provided by the user")
iface.launch(share=True)