import os

# Fix for SSL_CERT_FILE issue if it's set incorrectly in the environment
if "SSL_CERT_FILE" in os.environ and not os.path.exists(os.environ["SSL_CERT_FILE"]):
    del os.environ["SSL_CERT_FILE"]

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

class Brain:
    def __init__(self, model_name="llama3.1:8b", base_url="http://localhost:11434"):
        self.llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.3)
        self.system_prompt = """You are JARVIS (Just A Rather Very Intelligent System), a sophisticated AI created by Tony Stark.
        You are now operating on a high-performance MSI Vector 17 machine.
        
        Personality Traits:
        - Eloquent, professional, and slightly witty.
        - Use British English spelling and mannerisms where appropriate (e.g., "sir," "at your service," "checking systems").
        - Be proactive. If a system value looks abnormal (e.g., high heat), mention it.
        
        Capabilities:
        - You have access to real-time system telemetry for this MSI machine.
        - You can control media, volume, and launch applications.
        - You can search the web for real-time data.
        - You have long-term memory access to user documents.

        Guidelines:
        - Respond in a natural, conversational tone.
        - Keep responses concise but highly informative.
        - If the user asks for a status report, provide a comprehensive overview of the machine's vitals.
        """
        
        # Define tools using langchain's @tool decorator
        @tool
        def get_system_telemetry():
            """Get current CPU, GPU usage, battery status, and temperatures for the MSI Vector 17."""
            from src.tools.system_tools import SystemTools
            return SystemTools().get_system_telemetry()

        @tool
        def control_media(action: str):
            """Control media (mute, vol_up, vol_down, next, prev, play_pause)."""
            from src.tools.system_tools import SystemTools
            return SystemTools().control_media(action)

        @tool
        def launch_application(app_name: str):
            """Launch an application (e.g., chrome, vscode, notepad, spotify)."""
            from src.tools.system_tools import SystemTools
            return SystemTools().launch_app(app_name)

        @tool
        def web_search(query: str):
            """Search the web for real-time information using the TAVILY search engine."""
            from src.tools.web_tools import WebTools
            return WebTools().search(query)

        self.tools = [get_system_telemetry, control_media, launch_application, web_search]
        
        # Create the agent
        # Older versions of langgraph use 'prompt' instead of 'state_modifier'
        self.agent_executor = create_react_agent(
            self.llm, 
            tools=self.tools,
            prompt=self.system_prompt
        )
        
        # In-memory history for this session
        self.messages = []

    async def stream_response(self, user_input, memory=None):
        """Streams a response, handling RAG and tool calling via ReAct loop."""
        
        # Check for RAG trigger
        context = ""
        if memory and any(word in user_input.lower() for word in ["my notes", "my documents", "my files", "project"]):
            docs = memory.query(user_input)
            if docs:
                context = "\n\n[STARK ARCHIVES]:\n" + "\n".join(docs)
        
        full_input = user_input + context
        self.messages.append(HumanMessage(content=full_input))
        
        # Run the agent
        async for event in self.agent_executor.astream({"messages": self.messages}):
            if "agent" in event:
                message = event["agent"]["messages"][-1]
                if isinstance(message, AIMessage) and message.content:
                    yield message.content
            elif "tools" in event:
                tool_msg = event["tools"]["messages"][-1]
                print(f"\n[JARVIS]: Accessing {tool_msg.name}...")

        # Update history with the final result
        final_state = await self.agent_executor.ainvoke({"messages": self.messages})
        self.messages = final_state["messages"]

    def clear_history(self):
        self.messages = []
