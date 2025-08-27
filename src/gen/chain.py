from typing import List, Optional, TypedDict, Any, Annotated

# from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from flaskr.gen.tools.finance import stock_data
# from gen_ui_backend.tools.github import github_repo
# from gen_ui_backend.tools.invoice import invoice_parser
# from gen_ui_backend.tools.weather import weather_data


class GenerativeUIState(TypedDict, total=False):
    messages: Annotated[list, add_messages]


def invoke_model(state: GenerativeUIState, config: RunnableConfig) -> GenerativeUIState:
    # tools_parser = JsonOutputToolsParser()
    prompt_template = ChatPromptTemplate(
        [
            (
                "system",
                "You are a helpful assistant. You're provided a list of tools, and an input from the user.\n"
                + "Your job is to determine whether or not you have a tool which can handle the users input, or respond with plain text.",
            ),
            MessagesPlaceholder("input")
        ]
    )
    # initial_prompt = ChatPromptTemplate.from_messages(
    #     [
    #         (
    #             "system",
    #             "You are a helpful assistant. You're provided a list of tools, and an input from the user.\n"
    #             + "Your job is to determine whether or not you have a tool which can handle the users input, or respond with plain text.",
    #         ),
    #         MessagesPlaceholder("input"),
    #     ]
    # )
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    # tools = [github_repo, invoice_parser, weather_data]
    tools = [stock_data]
    model_with_tools = model.bind_tools(tools)
    # chain = initial_prompt | model_with_tools
    agent = prompt_template | model_with_tools
    # result = chain.invoke({"input": state["input"]}, config)
    result = agent.invoke(state["messages"])

    return { "messages": [result] }


# def invoke_tools_or_return(state: GenerativeUIState) -> str:
#     if "result" in state and isinstance(state["result"], str):
#         return END
#     elif "tool_calls" in state and isinstance(state["tool_calls"], list):
#         return "invoke_tools"
#     else:
#         raise ValueError("Invalid state. No result or tool calls found.")


# def invoke_tools(state: GenerativeUIState) -> GenerativeUIState:
#     tools_map = {
#         "stock_data": stock_data,
#     }

#     if state["tool_calls"] is not None:
#         print(state, stock_data)
#         tool = state["tool_calls"][0]
#         selected_tool = tools_map[tool["name"]]
#         return {"tool_result": selected_tool.invoke(tool["args"])}
#     else:
#         raise ValueError("No tool calls found in state.")


def create_graph() -> Any:
    workflow = StateGraph(GenerativeUIState)

    tool_node = ToolNode(tools=[stock_data])

    workflow.add_node("invoke_model", invoke_model)  # type: ignore
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "invoke_model")
    workflow.add_conditional_edges("invoke_model", tools_condition)
    workflow.add_edge("tools", "invoke_model")
    # workflow.add_edge("invoke_model", "invoke_tools")
    
    # workflow.set_finish_point("invoke_model")

    graph = workflow.compile()

    return graph