from langchain.agents import (
    load_tools,
    initialize_agent,
    AgentType,
    create_openai_tools_agent,
    AgentExecutor,
)
from langchain.tools import BaseTool, StructuredTool
from openai import OpenAI
import requests
import os
import json
from pydantic.v1 import BaseModel, Field
from typing import Type
from langchain_openai import ChatOpenAI
import gradio as gr
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import List
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

base_url = "https://captableuat.qapita.dev"
issuer_id = 1
access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjYxQ0UwMDkyRkUzRTNEQTRENDg0Qjg3N0RCRTdGQzBFIiwidHlwIjoiYXQrand0In0.eyJpc3MiOiJodHRwczovL2F1dGgucWFwaXRhLmRldiIsIm5iZiI6MTcwODAzODIwOCwiaWF0IjoxNzA4MDM4MjA4LCJleHAiOjE3MDgwNDE4MDgsImF1ZCI6WyJxYXBpdGEuY2FwaXRhbGl6YXRpb24iLCJodHRwczovL2F1dGgucWFwaXRhLmRldi9yZXNvdXJjZXMiXSwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsImFkZHJlc3MiLCJlbWFpbCIsInJvbGVzIiwicWFwaXRhLmNhcGl0YWxpemF0aW9uIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbInB3ZCJdLCJjbGllbnRfaWQiOiJxYXBpdGEucW1hcC51YXQud2ViLnVpIiwic3ViIjoiOWFjNTU3ZTMtNTNiNy00OTA2LThmZjctMjQwMjA2MTBmNzEwIiwiYXV0aF90aW1lIjoxNzA4MDI3NjI3LCJpZHAiOiJsb2NhbCIsImxhc3RfbG9naW4iOjE3MDc5OTU1OTYsImxhc3RfbG9nb3V0IjoxNzA3OTIyNjgwLCJlbWFpbCI6Inlhc2h3YW50aC5wdXR0YUBxYXBpdGFjb3JwLmNvbSIsIm5hbWUiOiJZYXNod2FudGggUHV0dGEiLCJnaXZlbl9uYW1lIjoiWWFzaHdhbnRoIiwiZmFtaWx5X25hbWUiOiJQdXR0YSIsInJvbGUiOiJBZG1pbmlzdHJhdG9yIiwic2lkIjoiNEFFNUVERjMzQ0Q0RDg2RDVCMUE1NDM2ODlGMkI5REIifQ.El43NMCOW0hXTUBpgUiybh9sV69a6ghr3nWSWeLUJGNXfuC1hquc31TLe4phzYL-PLaSuNLM_M9hsFUPpN_2IR8qqqBkQmCT8w2ncIXuPFvy0C8c6ekq-7hudUG5fi8VjqcIttORF0r5ZkGY5xQof8RtWIjbdBQyR_f_iJEq3tRgKNpO6kF5l8sxfb3NB4KRmHVn6zq1bSbhlyI-HHBgDbUYBivTW-y6IxgBL6e_LaBJCywi6fH35OWBlq3ePurZAqdFKf6SSUjJPnOaOAb-jZ5vabHceZpM0UG6t1BtGV1obubfOaGxsnU5yRomx7nlkpFxoTfYSdZf1A9QNDQgGg"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}


class OptionAwardExerciseWindowConfigurationInput(BaseModel):
    """Inputs for configuring the exercise window for option awards."""

    is_enabled: bool = Field(description="""Enables or disables the exercise window.""")
    notify_stakeholders: bool = Field(
        description="""Enables or disabled the settings that notifies the stakeholders, when the exercise window gets opened"""
    )
    exercise_window_start_date: str = Field(
        description="""Start date for opening the option award exercise window.Date Format should be in yyyy-mm-dd."""
    )
    exercise_window_end_date: str = Field(
        description="""End date for opening the option award exercise window.Date Format should be in yyyy-mm-dd."""
    )
    stakeholder_filter_status: List[str] = Field(
        description="""Defines a list of string listing stakeholder statuses, that are eligible for the exercise window. 
        Only 'Active' and 'Separated' are valid statuses. This list must include at least one of these statuses and should not be left empty."""
    )


def configure_exercise_window(
    is_enabled: bool,
    stakeholder_filter_status: List[str],
    exercise_window_start_date: str,
    exercise_window_end_date: str,
    notify_stakeholders: bool = False,
):
    """Configures the exercise window only for option award.
    This function can enable or disable the exercise window, it can open the exercise window permanently
    by not providing any start and end date for exercise window, also it can enabled or disable the notfiy stakeholders flag.
    It can also change the stakeholder filter status list"""

    # status_array = stakeholder_filter_status.split(",")
    # if len(status_array) == 0:
    #     return {
    #         "statusCode": 400,
    #         "errorMessage": "No stakeholder status filter got passed!",
    #     }

    cur_date_range = None
    if not is_string_null_empty_or_whitespace(
        exercise_window_start_date
    ) and not is_string_null_empty_or_whitespace(exercise_window_end_date):
        cur_date_range = {
            "startDate": exercise_window_start_date,
            "endDate": exercise_window_end_date,
        }

    exercise_data = {
        "commands": [
            {
                "issuerConfigurationId": 1,
                "$type": "UpdateEquityAwardWindowApiCommand",
                "equityAwardWindow": {
                    "instrumentType": "OptionAward",
                    "isEnabled": is_enabled,
                    "equityActionType": "Exercise",
                    "notifyStakeholders": notify_stakeholders,
                    "timeSettings": {
                        "timeZone": "Asia/Kolkata",
                        "dateRange": cur_date_range,
                        "timeRestrictions": [],
                    },
                    "stakeholderFilter": {
                        "statuses": stakeholder_filter_status,
                        "fields": [],
                    },
                },
            }
        ]
    }

    response = requests.put(
        f"{base_url}/api/v1/issuers/{issuer_id}/configurations",
        json=exercise_data,
        headers=headers,
    )

    print(response)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("An error occurred:", response.text)
        
    return response.json()


configure_option_award_exercise_window_tool = StructuredTool.from_function(
    func=configure_exercise_window,
    name="configure_option_award_exercise_window",
    # description="""This tool configures the exercise window for option awards.
    # It requires either both start and end dates for the exercise window, or an indication to keep the window open indefinitely.
    # If neither dates nor a request for indefinite opening are provided, the user's request will be rejected.
    # Also assume window to be enabled when user either specify the start and end exercise window date or  an indication to keep the window open indefinitely.
    # Exercise window start and end date must be in yyyy-mm-dd format, example: '2024-09-17', also end date must not me less than start date.
    # This tool takes multiple parameters like enabling or disabling the window using 'is_enabled" flag.
    # It can also set configuration of notfying stakeholder upon window opening using 'notify_stakeholders' flag.
    # The tool also manages stakeholder filters. It accepts a list of filter options where the valid choices are: ['Active'] for currently active grantees, ['Separated'] for grantees who are no longer active, or ['Active', 'Separated'] to include both groups. Users are required to specify one of these scenarios when setting the stakeholder status filter.
    # """,
    description="""This tool manages the option award exercise window. It requires start and end dates ('yyyy-mm-dd' format) or an option for indefinite opening. Without these, requests are rejected. The window is considered enabled with specified dates or indefinite opening request. The 'is_enabled' flag controls window activation, and 'notify_stakeholders' flag manages stakeholder notifications. Stakeholder filters are required: options are 'Active', 'Separated', or both. The end date must not precede the start date.""",
    args_schema=OptionAwardExerciseWindowConfigurationInput,
    return_direct=False,
)


class CreateStakeholderInput(BaseModel):
    """Inputs for creating the stakeholder in qapita platform"""

    legal_name: str = Field(
        description="""Legal name of the stakeholder, 
    or if not provided it will be combination of first name and last name of the stakeholder"""
    )
    first_name: str = Field(description="First name of the stakeholder")
    last_name: str = Field(description="Last name of the stakeholder")
    stakeholder_type: str = Field(
        default="Individual",
        description="[OPTIONAL]Type of the stakeholder that user wants to create, the only valid options are 'Individual' and 'Institution', if no type provided use 'Individual' as stakeholder_type",
    )
    is_employee: bool = Field(
        default=False,
        description="[OPTIONAL]Provides whether the stakholder is an employee or not, If not provided consider it to be False",
    )
    issuerEmployeeId: str = Field(
        default=None,
        description="[OPTIONAL]Represent the employee Id of a stakeholder, this will be a required field only if the stakeholder is an employee aka is_employee is True",
    )


def is_string_null_empty_or_whitespace(s):
    return s is None or s.strip() == ""


def create_stakeholder(
    legal_name: str,
    first_name: str,
    last_name: str,
    stakeholder_type: str = "Individual",
    is_employee: bool = False,
    issuerEmployeeId: str = "",
):
    """Creates a stakeholder in qapita platform."""

    if is_employee and is_string_null_empty_or_whitespace(issuerEmployeeId):
        return {
            "statusCode": 400,
            "errorMessage": "If stakeholder is an employee then the issuer employee id is required as well.",
        }

    if (
        stakeholder_type.lower() != "individual"
        and stakeholder_type.lower() != "institution"
    ):
        return {
            "statusCode": 400,
            "errorMessage": "Invalid Stakeholder type was provided the only valid options are 'Individual' or 'Institution'",
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
            "primaryMobileNumber": None,
        },
        "address": None,
        "primaryBankAccount": None,
        "personalIds": [],
        "isEmployee": is_employee,
        "issuerEmployeeId": issuerEmployeeId,
        "dateOfBirth": None,
        "commencementDate": None,
        "customFields": [],
        "dematAccounts": [],
        "taxId": None,
        "nationality": None,
        "stakeholderType": stakeholder_type,
        "documents": [],
        "nominees": [],
        "employmentHistory": [],
    }

    institutional_data = {
        "legalName": legal_name,
        "primaryContact": {"firstName": first_name, "lastName": last_name, "email": ""},
        "issuerId": 1,
        "issuerEmployeeId": "",
        "customFields": [],
        "taxId": "",
        "stakeholderType": "Institution",
    }

    data = individual_data
    if stakeholder_type.lower() == "institution":
        data = institutional_data

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.put(
        "https://captableuat.qapita.dev/api/v2/issuers/1/register-stakeholder",
        json=data,
        headers=headers,
    )
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("An error occurred:", response.text)

    return response.json()


create_stakeholder_tool = StructuredTool.from_function(
    func=create_stakeholder,
    name="create_stakeholder_tool",
    description="""This tool can be used to create the stakeholder in qapita platform.
    This tool requires legal name, first and last name of the stakeholder in order to create a stakeholder.
    If legal name not provided and stakeholder full name is provided then use the full name as legal name and pick the first and last name from the full name provided.
    """,
    args_schema=CreateStakeholderInput,
    return_direct=False,
)

langchainLlm = ChatOpenAI(
    model="ft:gpt-3.5-turbo-0613:personal::8q3apor4", temperature=0.2, streaming=True
)

sytem_template = """You are a helpful assitant who can do all sort of actions like creating a stakeholder, configuring the exercise window only for option award and other function callings."""
human_template = "{input}"
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(sytem_template),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate.from_template(
            input_variables=["input"], template=human_template
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# tools = [create_stakeholder_tool, configure_exercise_window]
tools = [configure_option_award_exercise_window_tool]

agent = create_openai_tools_agent(langchainLlm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

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
    response = agent_with_chat_history.invoke(
        {"input": input_text}, config={"configurable": {"session_id": "<foo>"}}
    )
    print(response)
    return response["output"]


# create ui interface to interact with gpt-3 model
iface = gr.Interface(
    fn=execute_task,
    inputs=gr.components.Textbox(lines=7, placeholder="Enter your execution here"),
    outputs="text",
    title="Qapita AI ChatBot: Your Knowledge Companion Powered-by ChatGPT",
    description="Execute the any task provided by the user",
)
iface.launch(share=True)
