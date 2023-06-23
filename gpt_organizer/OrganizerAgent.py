import os
from typing import List

from langchain.agents import (
    initialize_agent,
    Tool,
    AgentType,
    Agent,
    OpenAIFunctionsAgent,
    AgentExecutor,
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.schema import SystemMessage
import langchain

import gpt_organizer.prompts as prompts
from gpt_organizer.utils import *


langchain.debug = True


class OrganizerAgent:
    _openai_api_key = os.getenv("OPENAI_API_KEY")
    _llm = ChatOpenAI(
        model="gpt-3.5-turbo-0613",
        temperature=0,
        openai_api_key=_openai_api_key,
    )

    @classmethod
    def _create_report_writer(
        cls, message_history_str: str, form_prompt: str
    ) -> LLMChain:
        # Compose prompt
        template = (
            form_prompt + f"\nChat History: {message_history_str}" + "\n{ai_input}"
        )
        prompt = PromptTemplate(
            template=template,
            input_variables=["ai_input"],
        )
        sys_prompt = SystemMessagePromptTemplate(prompt=prompt)
        chat_prompt = ChatPromptTemplate.from_messages([sys_prompt])

        # Create chain
        return LLMChain(llm=cls._llm, prompt=chat_prompt, verbose=True)

    @classmethod
    def _create_agent(
        cls, message_history_str: str, prompt: str, form_prompt: str
    ) -> AgentExecutor:
        template = prompt

        # Compose agent prompt
        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=SystemMessage(content=template)
        )
        print(prompt)

        # Create agent tools
        report_writer = cls._create_report_writer(message_history_str, form_prompt)
        tools = [
            Tool(
                name="ReportWriter",
                func=report_writer.run,
                description="Useful for writing a report.",
            )
        ]

        agent = OpenAIFunctionsAgent(
            tools=tools,
            llm=cls._llm,
            prompt=prompt,
            verbose=True,
        )
        return AgentExecutor.from_agent_and_tools(agent, tools)

    @classmethod
    def get_response(
        cls,
        messages: List[str],
        prompt: str = prompts.DEMO_PROMPT,
        form_prompt: str = prompts.FORM_INSTRUCTIONS,
    ) -> str:
        # Create message history
        message_history_str = compose_message_history(messages)
        agent = cls._create_agent(message_history_str, prompt, form_prompt)

        # Prompt agent for response
        message_history_str += "\nAI:"
        return agent.run(f"Chat history: {message_history_str}")
