import os
from openai import OpenAI
import json
from app.services.search import search_web

def stream_ai_response(message_history, system_prompt, model_id="meta/llama-3.1-70b-instruct"):
    token = os.environ.get('NVIDIA_API_KEY')
    
    if not token:
        yield f"[Warning: NVIDIA_API_KEY not set. Mocking response] "
        prompt = message_history[-1]['content'] if message_history else ""
        words = f"Mock response for: '{prompt}'. Agent: {system_prompt}".split(' ')
        for i, word in enumerate(words):
            yield word if i == 0 else ' ' + word
        return

    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=token,
        )
        messages = [{"role": "system", "content": system_prompt}]
        for msg in message_history:
            role = "assistant" if msg.get("role") == "ai" else "user"
            messages.append({"role": role, "content": msg.get("content", "")})
            
        tools = [{
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Searches the web for up-to-date information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"}
                    },
                    "required": ["query"]
                }
            }
        }]

        active_model = model_id
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=active_model,
                stream=True,
                tools=tools
            )
        except Exception as e:
            if "unknown_model" in str(e).lower() or "unknown model" in str(e).lower() or "400" in str(e) or "404" in str(e) or "410" in str(e):
                active_model = "meta/llama-3.1-70b-instruct"
                yield f"[Notice: '{model_id}' is unavailable on your account. Falling back to {active_model}]\n\n"
                response = client.chat.completions.create(
                    messages=messages,
                    model=active_model,
                    stream=True,
                    tools=tools
                )
            else:
                raise e
                
        tool_calls = {}
        finish_reason = None
        for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls:
                            tool_calls[idx] = {"id": tc.id, "name": tc.function.name, "arguments": ""}
                        if tc.function.arguments:
                            tool_calls[idx]["arguments"] += tc.function.arguments
                elif delta.content is not None:
                    yield delta.content
        
        if finish_reason == "tool_calls":
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}} 
                    for tc in tool_calls.values()
                ]
            })
            
            for tc in tool_calls.values():
                if tc["name"] == "search_web":
                    try:
                        args = json.loads(tc["arguments"])
                        yield f"\n*[Searching web for: {args.get('query')}]*\n"
                        results = search_web(args.get("query", ""))
                        messages.append({"role": "tool", "tool_call_id": tc["id"], "content": str(results)})
                    except Exception as e:
                        messages.append({"role": "tool", "tool_call_id": tc["id"], "content": f"Error: {e}"})
            
            response2 = client.chat.completions.create(
                messages=messages,
                model=active_model,
                stream=True
            )
            for chunk2 in response2:
                if chunk2.choices and chunk2.choices[0].delta.content is not None:
                    yield chunk2.choices[0].delta.content

    except Exception as e:
        yield f"\n[Error: {str(e)}]"
