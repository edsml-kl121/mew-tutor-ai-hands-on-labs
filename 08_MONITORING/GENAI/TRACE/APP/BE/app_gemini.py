from flask import Flask, request, jsonify
from langchain.tools.render import render_text_description_and_args
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from tools import GroceryInvetorySearchTool, RecommenderSystemTool, OrderProcessorTool
from prompt import agentic_prompt
from dotenv import load_dotenv
import os
# from langchain_openai import OpenAI, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
google_api_key = os.environ["GOOGLE_API_KEY"]
# Initialize Flask app
app = Flask(__name__)
#
llm = ChatGoogleGenerativeAI(
    # model="gemini-2.5-flash-preview-04-17",
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=5,
    # other params...
)

# Initialize tools and chain
message_history = ChatMessageHistory()
tools = [
    GroceryInvetorySearchTool().get_tool(),
    # RecommenderSystemTool().get_tool(),
    OrderProcessorTool().get_tool(),
]

prompt = agentic_prompt().partial(
    tools=render_text_description_and_args(list(tools)),
    tool_names=", ".join([t.name for t in tools]),
)

chain = (
    RunnablePassthrough.assign(
        agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
    )
    | prompt
    | llm
    | JSONAgentOutputParser()
)

agent_executor_chat = AgentExecutor(
    agent=chain, tools=tools, handle_parsing_errors=True, verbose=True
)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor_chat,
    get_session_history=lambda session_id: message_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Define the /chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Parse user input from the request
        data = request.json
        user_input = data.get("input")
        session_id = data.get("session_id", "default_session")

        # Ensure input is provided
        if not user_input:
            return jsonify({"error": "Missing 'input' field in request body."}), 400

        # Invoke the agent with chat history
        response = agent_with_chat_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )

        # Return the response
        print(response)
        print("RESPONSE", response["output"])
        return {"response": response["output"]}

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
