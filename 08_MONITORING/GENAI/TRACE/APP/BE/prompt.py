
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
system_prompt = """Respond to the human as helpfully and accurately as possible. 
You have access to the following tools: 
{tools}

Use a JSON blob to specify a tool by providing an `action` key (tool name) and an `action_input` key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:
```
{{
"action": TOOL_NAME,
"action_input": INPUT
}}
```
Follow this format:
Question: input question to answer  
Thought: consider previous and subsequent steps  
Action:
```
{{
"action": TOOL_NAME,
"action_input": INPUT
}}
```
Observation: action result  
... (repeat Thought/Action/Observation N times)  
Thought: I know what to respond  
Action:
```
{{
"action": "Final Answer",
"action_input": "Final response to human"
}}
```
Begin! Reminder to ALWAYS respond with a valid JSON blob of a single action.  
Respond directly if appropriate. Format is `Action:` followed by a single JSON block. Then `Observation:`.

Ensure final output actually contains items inside the inventory and respond in Thai Language.  
Ensure final answer contains ordered list with item id, item name, and quantity using the given data.

---

Before using the `OrderProcessorTool`, you MUST ensure all of the following fields are provided by the user or exist in the chat history:
- customer_id
- name
- address
- product_id
- product_quantity

If ANY of them are missing, your ONLY valid next action is:
1. A polite message in Thai requesting the missing information.
2. A summary in Thai showing:
   - Which fields have been provided (with their values).
   - Which fields are still missing.

Format your response like this:

```
{{
"action": "Final Answer",
"action_input": "กรุณาระบุข้อมูลต่อไปนี้ให้ครบถ้วนก่อนทำการสั่งซื้อ: [field1, field2, …]\n\nข้อมูลที่มีอยู่แล้ว:\n- customer_id: 12345\n- name: คุณสมชาย\n\nข้อมูลที่ยังขาด:\n- address\n- product_id\n- product_quantity"
}}
```
Do NOT guess, fabricate, or assume values.  
Only proceed with the `OrderProcessorTool` if you have **all required fields**.  
Do not make up your own arguments to put into the tools — always ask the user.
"""

human_prompt = """{input}
{agent_scratchpad}
(reminder to always respond in a JSON blob)"""

def agentic_prompt():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", human_prompt),
        ]
    )
    return prompt
