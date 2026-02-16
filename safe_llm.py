

import os
from dotenv import load_dotenv
from groq import Groq
import uuid
import json
from datetime import datetime, timezone

# Load environment variables
load_dotenv()


class SafeLLM:
    """
    LangChain-compatible LLM wrapper for Groq API.
    
    Provides the same interface as ChatOpenAI but uses Groq's API
    for faster, more efficient inference with open-source models.
    """
    
    def __init__(self, model_name="openai/gpt-oss-120b", temperature=0):
        """
        Initialize SafeLLM with Groq client.
        
        Args:
            model_name: Groq model to use
            temperature: Temperature for sampling (0-1)
        """
        self.model_name = model_name
        self.temperature = temperature
        
        # Verify Groq API key
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("❌ GROQ_API_KEY not found in environment variables!")
        
        self.client = Groq(api_key=groq_key)
        self.tools = []
        self.parallel_tool_calls = False
        self.tool_choice = None
        self._invoke_stack = 0
        
        # LangSmith setup
        self.langsmith_tracing = os.getenv("LANGSMITH_TRACING_V2", "false").lower() == "true"
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "default")
        self.langsmith_workspace_id = os.getenv("LANGSMITH_WORKSPACE_ID")
        
        if self.langsmith_tracing:
            try:
                from langsmith import Client
                langsmith_key = os.getenv("LANGSMITH_API_KEY")
                
                if not langsmith_key:
                    print("⚠️  LANGSMITH_API_KEY not found, disabling tracing")
                    self.langsmith_tracing = False
                    self.langsmith_client = None
                else:
                    # Set workspace_id in environment
                    if self.langsmith_workspace_id:
                        os.environ["LANGSMITH_WORKSPACE_ID"] = self.langsmith_workspace_id
                    
                    self.langsmith_client = Client(api_key=langsmith_key)
                    print(f"✅ LangSmith enabled for project: {self.langsmith_project}")
                    
            except ImportError:
                print("⚠️  langsmith not installed. Run: pip install langsmith")
                self.langsmith_tracing = False
                self.langsmith_client = None
            except Exception as e:
                print(f"⚠️  LangSmith init failed: {e}")
                self.langsmith_tracing = False
                self.langsmith_client = None

    def invoke(self, messages, config=None):
        """
        Invoke the LLM with messages.
        
        Accepts LangChain message format and converts to Groq format.
        
        Args:
            messages: List of LangChain messages or single message
            config: Optional RunnableConfig (for LangChain compatibility)
            
        Returns:
            AIMessage with response
        """
        if self._invoke_stack > 0:
            return messages[-1] if isinstance(messages, list) else messages
        
        self._invoke_stack += 1
        run_id = None
        
        try:
            formatted_messages = self._format_messages(messages)
            
            request_params = {
                "model": self.model_name,
                "messages": formatted_messages,
                "temperature": self.temperature
            }
            
            if self.tools:
                request_params["tools"] = self._format_tools()
                
                # Handle tool_choice
                if self.tool_choice:
                    if self.tool_choice == "auto":
                        request_params["tool_choice"] = "auto"
                    elif self.tool_choice == "required" or self.tool_choice == "any":
                        # Groq doesn't support 'any' or 'required', use 'auto' instead
                        request_params["tool_choice"] = "auto"
                    elif isinstance(self.tool_choice, str):
                        # Specific tool name - Groq supports this
                        request_params["tool_choice"] = {
                            "type": "function",
                            "function": {"name": self.tool_choice}
                        }
                else:
                    request_params["tool_choice"] = "auto"
            
            # Start trace in LangSmith
            if self.langsmith_tracing and self.langsmith_client:
                try:
                    run_id = str(uuid.uuid4())
                    
                    self.langsmith_client.create_run(
                        id=run_id,
                        name="groq_llm_call",
                        run_type="llm",
                        inputs={
                            "messages": formatted_messages,
                            "model": self.model_name,
                            "temperature": self.temperature
                        },
                        project_name=self.langsmith_project,
                        start_time=datetime.now(timezone.utc)
                    )
                    
                except Exception as e:
                    print(f"[LangSmith] Create run failed: {e}")
                    run_id = None
            
            # Call Groq API
            response = self.client.chat.completions.create(**request_params)
            message = response.choices[0].message
            
            from langchain_core.messages import AIMessage, ToolCall
            
            tool_calls = []
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tc in message.tool_calls:
                    # Convert arguments from string to dict
                    try:
                        args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                    except json.JSONDecodeError:
                        args = {}
                    
                    tool_calls.append(ToolCall(
                        name=tc.function.name,
                        args=args,
                        id=tc.id
                    ))
            
            result = AIMessage(
                content=message.content or "",
                tool_calls=tool_calls
            )
            
            # End trace and save output
            if self.langsmith_tracing and self.langsmith_client and run_id:
                try:
                    self.langsmith_client.update_run(
                        run_id=run_id,
                        outputs={
                            "content": result.content,
                            "model": self.model_name
                        },
                        end_time=datetime.now(timezone.utc)
                    )
                    print(f"✅ Run logged to LangSmith: {run_id[:8]}...")
                    
                except Exception as e:
                    print(f"[LangSmith] Update run failed: {e}")
            
            return result
            
        finally:
            self._invoke_stack -= 1

    def stream(self, messages, config=None):
        """
        Stream responses from the LLM.
        
        Accepts LangChain message format and streams response chunks.
        
        Args:
            messages: List of LangChain messages or single message
            config: Optional RunnableConfig (for LangChain compatibility)
            
        Yields:
            AIMessageChunk objects with partial content
        """
        from langchain_core.messages import AIMessageChunk, ToolCall, ToolCallChunk
        
        formatted_messages = self._format_messages(messages)
        
        request_params = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": self.temperature,
            "stream": True
        }
        
        if self.tools:
            request_params["tools"] = self._format_tools()
            
            # Handle tool_choice
            if self.tool_choice:
                if self.tool_choice == "auto":
                    request_params["tool_choice"] = "auto"
                elif self.tool_choice == "required" or self.tool_choice == "any":
                    request_params["tool_choice"] = "auto"
                elif isinstance(self.tool_choice, str):
                    request_params["tool_choice"] = {
                        "type": "function",
                        "function": {"name": self.tool_choice}
                    }
            else:
                request_params["tool_choice"] = "auto"
        
        # Call Groq API with streaming
        stream = self.client.chat.completions.create(**request_params)
        
        # Track tool calls being built
        tool_call_chunks = {}
        
        for chunk in stream:
            if not chunk.choices:
                continue
                
            delta = chunk.choices[0].delta
            
            # Handle content chunks
            if hasattr(delta, 'content') and delta.content:
                yield AIMessageChunk(content=delta.content)
            
            # Handle tool call chunks
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    index = tc_delta.index
                    
                    # Initialize tool call if new
                    if index not in tool_call_chunks:
                        tool_call_chunks[index] = {
                            'id': tc_delta.id if hasattr(tc_delta, 'id') else None,
                            'name': '',
                            'args': ''
                        }
                    
                    # Update tool call data
                    if hasattr(tc_delta, 'id') and tc_delta.id:
                        tool_call_chunks[index]['id'] = tc_delta.id
                    
                    if hasattr(tc_delta, 'function'):
                        if hasattr(tc_delta.function, 'name') and tc_delta.function.name:
                            tool_call_chunks[index]['name'] = tc_delta.function.name
                        if hasattr(tc_delta.function, 'arguments') and tc_delta.function.arguments:
                            tool_call_chunks[index]['args'] += tc_delta.function.arguments
                    
                    # Yield tool call chunk
                    yield AIMessageChunk(
                        content="",
                        tool_call_chunks=[
                            ToolCallChunk(
                                name=tool_call_chunks[index]['name'] or None,
                                args=tc_delta.function.arguments if hasattr(tc_delta, 'function') and hasattr(tc_delta.function, 'arguments') else None,
                                id=tool_call_chunks[index]['id'],
                                index=index
                            )
                        ]
                    )
        
        # Yield final message with complete tool calls
        if tool_call_chunks:
            complete_tool_calls = []
            for idx in sorted(tool_call_chunks.keys()):
                tc = tool_call_chunks[idx]
                try:
                    args = json.loads(tc['args']) if tc['args'] else {}
                except json.JSONDecodeError:
                    args = {}
                
                complete_tool_calls.append(ToolCall(
                    name=tc['name'],
                    args=args,
                    id=tc['id'] or f"call_{idx}"
                ))
            
            yield AIMessageChunk(
                content="",
                tool_calls=complete_tool_calls
            )

    def _format_messages(self, messages):
        """
        Convert LangChain messages to Groq format.
        
        Args:
            messages: List of LangChain messages
            
        Returns:
            List of Groq-formatted message dictionaries
        """
        formatted = []
        for msg in messages:
            if hasattr(msg, 'type'):
                if msg.type == "system":
                    formatted.append({"role": "system", "content": msg.content})
                elif msg.type == "human":
                    formatted.append({"role": "user", "content": msg.content})
                elif msg.type == "ai":
                    msg_dict = {"role": "assistant", "content": msg.content or ""}
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        msg_dict["tool_calls"] = [
                            {
                                "id": tc.get("id", f"call_{i}"),
                                "type": "function",
                                "function": {
                                    "name": tc.get("name"),
                                    "arguments": json.dumps(tc.get("args", {}))
                                }
                            }
                            for i, tc in enumerate(msg.tool_calls)
                        ]
                    formatted.append(msg_dict)
                elif msg.type == "tool":
                    formatted.append({
                        "role": "tool",
                        "content": msg.content,
                        "tool_call_id": msg.tool_call_id
                    })
            else:
                formatted.append(msg)
        return formatted

    def _format_tools(self):
        """
        Format tools for Groq API.
        
        Converts Pydantic models or functions to Groq tool format.
        
        Returns:
            List of tool dictionaries
        """
        import inspect
        from pydantic import BaseModel
        
        formatted_tools = []
        
        for tool in self.tools:
            # Check if it's a Pydantic model
            if isinstance(tool, type) and issubclass(tool, BaseModel):
                schema = tool.model_json_schema()
                formatted_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.__name__,
                        "description": schema.get("description", f"Tool: {tool.__name__}"),
                        "parameters": {
                            "type": "object",
                            "properties": schema.get("properties", {}),
                            "required": schema.get("required", [])
                        }
                    }
                })
            else:
                # Assume it's a function
                sig = inspect.signature(tool)
                doc = inspect.getdoc(tool) or ""
                
                properties = {}
                required = []
                
                for param_name, param in sig.parameters.items():
                    param_type = "string"
                    if param.annotation != inspect.Parameter.empty:
                        if param.annotation == int:
                            param_type = "integer"
                        elif param.annotation == float:
                            param_type = "number"
                    
                    properties[param_name] = {
                        "type": param_type,
                        "description": f"Parameter {param_name}"
                    }
                    required.append(param_name)
                
                formatted_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.__name__,
                        "description": doc.split('\n')[0] if doc else f"Function {tool.__name__}",
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }
                    }
                })
        
        return formatted_tools

    def bind_tools(self, tools, parallel_tool_calls=False, tool_choice=None, **kwargs):
        """
        Bind tools to this LLM instance.
        
        Args:
            tools: List of tools (Pydantic models or functions)
            parallel_tool_calls: Whether to allow parallel tool calling
            tool_choice: Tool choice strategy (auto, required, or specific tool name)
            **kwargs: Additional arguments (ignored for compatibility)
            
        Returns:
            Self for chaining
        """
        self.tools = tools
        self.parallel_tool_calls = parallel_tool_calls
        self.tool_choice = tool_choice
        return self

    def with_config(self, config=None, **kwargs):
        """
        Return self with config (for LangChain compatibility).
        
        Args:
            config: Configuration dict
            **kwargs: Additional configuration
            
        Returns:
            Self
        """
        return self
    
    def with_listeners(self, **kwargs):
        """
        Return self with listeners (for Trustcall compatibility).
        
        Args:
            **kwargs: Listener callbacks
            
        Returns:
            Self
        """
        # Store listeners for potential future use
        self._listeners = kwargs
        return self


# Create global instance
LLM_chat = SafeLLM()