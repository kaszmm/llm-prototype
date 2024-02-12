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
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)

class CreateStakeholderInput(BaseModel):
    """Inputs for creating the stakeholder in qapita platform"""

    legal_name :str = Field(description="Legal name of the stakeholder")
    first_name :str = Field(description="First name of the stakeholder")
    last_name :str = Field(description="Last name of the stakeholder")

def create_stakeholder(legal_name:str,first_name:str,last_name:str):
    """Creates a stakeholder in qapita platform"""
    data = {
            "stakeholderId": 1700,
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
            "isEmployee": False,
            "issuerEmployeeId": "",
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
            "stakeholderType": "Individual",
            "documents": [],
            "nominees": [],
            "employmentHistory": []
    }

    headers = {
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjU2QzdBQ0Y1QzAxMTE1RThBNDMxODg5QzNBRkU1MzcwIiwidHlwIjoiYXQrand0In0.eyJpc3MiOiJodHRwczovL2F1dGgucWFwaXRhLmRldiIsIm5iZiI6MTcwNzY3NDY4NywiaWF0IjoxNzA3Njc0Njg3LCJleHAiOjE3MDc2NzgyODcsImF1ZCI6WyJxYXBpdGEuY2FwaXRhbGl6YXRpb24iLCJodHRwczovL2F1dGgucWFwaXRhLmRldi9yZXNvdXJjZXMiXSwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsImFkZHJlc3MiLCJlbWFpbCIsInJvbGVzIiwicWFwaXRhLmNhcGl0YWxpemF0aW9uIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbInB3ZCJdLCJjbGllbnRfaWQiOiJxYXBpdGEucW1hcC51YXQud2ViLnVpIiwic3ViIjoiOWFjNTU3ZTMtNTNiNy00OTA2LThmZjctMjQwMjA2MTBmNzEwIiwiYXV0aF90aW1lIjoxNzA3MjAyOTEzLCJpZHAiOiJsb2NhbCIsImxhc3RfbG9naW4iOjE3MDc2NTU1NDEsImxhc3RfbG9nb3V0IjoxNzA3NDgyODcwLCJlbWFpbCI6Inlhc2h3YW50aC5wdXR0YUBxYXBpdGFjb3JwLmNvbSIsIm5hbWUiOiJZYXNod2FudGggUHV0dGEiLCJnaXZlbl9uYW1lIjoiWWFzaHdhbnRoIiwiZmFtaWx5X25hbWUiOiJQdXR0YSIsInJvbGUiOiJBZG1pbmlzdHJhdG9yIiwic2lkIjoiMzUwOTVGRDcxODBCRjA0QzMwM0MwRkIzQURFQjhBRTUifQ.LyDNh9wS3Jg7UledMRXctVmZDVBh_ggSLH7TPJ-HwHEaMKhGloFYorzfRkx4G2Kou4z87zdCAECSxdw8IUdRdiRyTbiSPNSNffYzUKqiBpdAUGIK6V700iDmlTtJFpgLpRLo2sa5f1WYawMXzE3ZqeUNG2krATZlGYPnocaSOkyFNuHuF5g9LJkOytZNMo6BHiwd5LkuvJ82B0-1Nnzs7hhuBmfu3pJVblWACecGVxNAkUudZw0xBQl9R1GW-KbL1aaSg-TaYLaftcEvxlm9jXWV0g7vcrw6dvXRpbdrTS2LD9sde3CWC5To8z9rdRCF8PeWaGDLniQF3DBsm8Dxlg',  
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

def execute_task(input_text):
    response = agent_executor.invoke({"input": input_text, "chat_history":[]})
    print(response)
    return response["output"]

# create ui interface to interact with gpt-3 model
iface = gr.Interface(fn=execute_task,
                     inputs=gr.components.Textbox(lines=7, placeholder="Enter your execution here"),
                     outputs="text",
                     title="Qapita AI ChatBot: Your Knowledge Companion Powered-by ChatGPT",
                     description="Execute the any task provided by the user")
iface.launch(share=True)
