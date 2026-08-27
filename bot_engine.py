"""
Bot Engine module for the AI Chatbot.
Provides a built-in smart assistant (offline/rule-based) and optional external LLM API integration.
"""

import math
import re
import ast
import json
import urllib.request
import urllib.error
from datetime import datetime

class SmartAssistant:
    """Built-in conversational assistant working without API keys."""

    PERSONAS = {
        "general": {
            "name": "General Assistant",
            "system": "I am a helpful, friendly, and knowledgeable AI assistant.",
            "greeting": "Hello! How can I help you today?"
        },
        "coder": {
            "name": "Code Expert",
            "system": "I am a senior software developer skilled in Python, JavaScript, HTML/CSS, SQL, C++, and system architecture.",
            "greeting": "Code Expert ready! What algorithm, script, or bug are we tackling today?"
        },
        "math": {
            "name": "Math & Logic Tutor",
            "system": "I am a mathematics and logic expert. I solve equations, explain formulas, and break down complex logic step-by-step.",
            "greeting": "Greetings! Ask me any math problem, calculation, or logic puzzle."
        },
        "writer": {
            "name": "Creative Writer",
            "system": "I am an imaginative creative writer, story generator, and content editor.",
            "greeting": "Welcome! Let's draft a compelling story, blog post, poem, or essay together."
        },
        "concise": {
            "name": "Concise Bot",
            "system": "I provide direct, brief, bullet-pointed answers with zero fluff.",
            "greeting": "Concise Bot ready. State your request."
        }
    }

    @staticmethod
    def safe_eval_math(expr_str):
        """Safely evaluates math expressions using python's AST."""
        try:
            # Clean string
            clean_str = expr_str.strip().lower()
            clean_str = clean_str.replace('^', '**').replace('×', '*').replace('÷', '/')
            
            # Match mathematical words
            clean_str = re.sub(r'sqrt\((.*?)\)', r'math.sqrt(\1)', clean_str)
            clean_str = re.sub(r'pi', r'math.pi', clean_str)
            clean_str = re.sub(r'sin\((.*?)\)', r'math.sin(\1)', clean_str)
            clean_str = re.sub(r'cos\((.*?)\)', r'math.cos(\1)', clean_str)
            clean_str = re.sub(r'tan\((.*?)\)', r'math.tan(\1)', clean_str)
            clean_str = re.sub(r'log\((.*?)\)', r'math.log10(\1)', clean_str)

            allowed_names = {
                "math": math, "sqrt": math.sqrt, "pi": math.pi,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log10, "abs": abs, "round": round
            }
            code = compile(clean_str, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    return None
            result = eval(code, {"__builtins__": {}}, allowed_names)
            return result
        except Exception:
            return None

    @classmethod
    def generate_response(cls, user_message, persona_key="general", history=None):
        """Generates a smart response using pattern recognition and knowledge base."""
        msg = user_message.strip()
        msg_lower = msg.lower()
        persona = cls.PERSONAS.get(persona_key, cls.PERSONAS["general"])

        # 1. Check for Math / Calculation requests
        math_patterns = [
            r'^(?:calculate|compute|what is|eval|evaluate|solve)?\s*([0-9\.\s\+\-\*\/\^\(\)\%\,\s(?:sqrt|pi|sin|cos|tan|log)]+)$',
            r'^([0-9\.\s\+\-\*\/\^\(\)]+)$'
        ]
        for pat in math_patterns:
            match = re.match(pat, msg_lower)
            if match:
                expr = match.group(1)
                # Check if it has math operators
                if any(op in expr for op in ['+', '-', '*', '/', '^', 'sqrt', 'sin', 'cos']):
                    val = cls.safe_eval_math(expr)
                    if val is not None:
                        if isinstance(val, float) and val.is_integer():
                            val = int(val)
                        return f"🔢 **Calculation Result:**\n\n```text\n{expr.strip()} = {val}\n```"

        # 2. Check for Greetings
        if any(w in msg_lower for w in ["hello", "hi", "hey", "greetings", "good morning", "good evening", "howdy"]):
            prefix = persona.get("greeting", "Hello!")
            return f"{prefix}\n\nI am operating in **{persona['name']}** mode. How can I assist you right now?"

        # 3. Check for Time / Date queries
        if any(phrase in msg_lower for phrase in ["what time is it", "current time", "today's date", "what is the date"]):
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            return f"🕒 **Current Local Time:** {time_str}\n📅 **Date:** {date_str}"

        # 4. Code Generation Requests
        if any(w in msg_lower for w in ["code", "python", "javascript", "function", "html", "css", "script", "program"]):
            if "python" in msg_lower or "reverse" in msg_lower:
                return (
                    "Here is a clean Python snippet to solve that:\n\n"
                    "```python\n"
                    "def reverse_string(text: str) -> str:\n"
                    "    \"\"\"Reverses the input string efficiently.\"\"\"\n"
                    "    return text[::-1]\n\n"
                    "# Example usage:\n"
                    "sample = 'Hello, AI Chatbot!'\n"
                    "print('Original:', sample)\n"
                    "print('Reversed:', reverse_string(sample))\n"
                    "```\n\n"
                    "Feel free to request any specific modifications!"
                )
            if "javascript" in msg_lower or "js" in msg_lower:
                return (
                    "Here is a JavaScript solution:\n\n"
                    "```javascript\n"
                    "// Async fetch example\n"
                    "async function fetchData(url) {\n"
                    "    try {\n"
                    "        const response = await fetch(url);\n"
                    "        const data = await response.json();\n"
                    "        console.log('Fetched Data:', data);\n"
                    "        return data;\n"
                    "    } catch (error) {\n"
                    "        console.error('Error fetching data:', error);\n"
                    "    }\n"
                    "}\n"
                    "```"
                )
            if "html" in msg_lower or "css" in msg_lower or "web page" in msg_lower:
                return (
                    "Here is a modern HTML/CSS layout template:\n\n"
                    "```html\n"
                    "<!DOCTYPE html>\n"
                    "<html lang=\"en\">\n"
                    "<head>\n"
                    "    <meta charset=\"UTF-8\">\n"
                    "    <title>Modern Card Component</title>\n"
                    "    <style>\n"
                    "        .card {\n"
                    "            background: #ffffff;\n"
                    "            border-radius: 12px;\n"
                    "            padding: 24px;\n"
                    "            box-shadow: 0 10px 25px rgba(0,0,0,0.1);\n"
                    "            font-family: system-ui, sans-serif;\n"
                    "        }\n"
                    "    </style>\n"
                    "</head>\n"
                    "<body>\n"
                    "    <div class=\"card\">\n"
                    "        <h2>Card Title</h2>\n"
                    "        <p>This is a sleek component layout.</p>\n"
                    "    </div>\n"
                    "</body>\n"
                    "</html>\n"
                    "```"
                )

        # 5. Jokes & Humor
        if "joke" in msg_lower or "funny" in msg_lower:
            jokes = [
                "Why do programmers prefer dark mode?\nBecause light attracts bugs! 🐛",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "A SQL query walks into a bar, walks up to two tables and asks: *'Can I join you?'*",
                "Why did the developer break up with their keyboard?\nBecause it wasn't their type! ⌨️"
            ]
            import random
            return f"😄 **Here's a joke for you:**\n\n{random.choice(jokes)}"

        # 6. Capabilities & Help
        if any(w in msg_lower for w in ["who are you", "what can you do", "help", "features", "capabilities"]):
            return (
                "✨ **I am your AI Chatbot!** Here is what I can do:\n\n"
                "- 💬 **Conversational AI**: Answer questions, discuss topics, and assist with tasks.\n"
                "- 💻 **Coding Assistance**: Generate Python, JS, HTML/CSS, SQL code snippets.\n"
                "- 🔢 **Math Solver**: Evaluate mathematical expressions (`sqrt(144)`, `2^10`, `15 * 8`).\n"
                "- 🎭 **Personas**: Switch roles between Code Expert, Math Tutor, Creative Writer, and Concise Bot.\n"
                "- 🔑 **LLM Provider Integration**: Connect your Google Gemini, OpenAI, or Ollama API key in Settings for live cloud/local AI model responses.\n"
                "- 📁 **Chat History**: Save, organize, rename, and export multiple chat conversations."
            )

        # 7. Default Contextual / Intelligent Response
        if persona_key == "coder":
            return (
                f"As a **Code Expert**, I analyzed your query: *\"{msg}\"*\n\n"
                "I can write full scripts, refactor code, debug errors, or explain software design patterns. "
                "Could you specify the language or framework you are working with?"
            )
        elif persona_key == "math":
            return (
                f"As a **Math & Logic Tutor**, regarding *\"{msg}\"*\n\n"
                "I can break down mathematical equations step-by-step or solve logic problems. "
                "Provide an equation or expression, and I will solve it for you!"
            )
        elif persona_key == "writer":
            return (
                f"As a **Creative Writer**, inspired by *\"{msg}\"*\n\n"
                "I can compose stories, draft blog articles, refine tone, or write poetry. "
                "What tone or style would you like to explore?"
            )
        elif persona_key == "concise":
            return (
                f"• Query: {msg}\n"
                f"• Status: Processed\n"
                f"• Action: Ready for specific instructions or questions."
            )

        # General default response
        return (
            f"I understand you are asking about: **\"{msg}\"**\n\n"
            "I am ready to help! You can ask me for code snippets, calculations, writing suggestions, or connect your **Gemini / OpenAI API key** in the Settings gear icon ⚙️ at the top right to enable live LLM completions."
        )


class ExternalLLMEngine:
    """Handles external LLM completion calls to OpenAI, Google Gemini, and Ollama."""

    @staticmethod
    def call_gemini(api_key, model, prompt, system_instruction=""):
        """Calls Google Gemini REST API."""
        if not model:
            model = "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"System Instruction: {system_instruction}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow your persona instructions."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {"contents": contents}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                candidates = res_json.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                return "No response content returned by Gemini API."
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            return f"❌ **Gemini API Error ({e.code}):** {err_msg}"
        except Exception as e:
            return f"❌ **Connection Error:** {str(e)}"

    @staticmethod
    def call_openai(api_key, model, prompt, system_instruction=""):
        """Calls OpenAI Chat Completion REST API."""
        if not model:
            model = "gpt-3.5-turbo"
        url = "https://api.openai.com/v1/chat/completions"

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                choices = res_json.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return "No response content returned by OpenAI API."
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            return f"❌ **OpenAI API Error ({e.code}):** {err_msg}"
        except Exception as e:
            return f"❌ **Connection Error:** {str(e)}"

    @staticmethod
    def call_ollama(endpoint, model, prompt, system_instruction=""):
        """Calls Ollama Local API."""
        if not endpoint:
            endpoint = "http://localhost:11434"
        if not model:
            model = "llama3"
            
        url = f"{endpoint.rstrip('/')}/api/generate"
        full_prompt = f"{system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                return res_json.get("response", "No response returned from Ollama.")
        except Exception as e:
            return f"❌ **Ollama Connection Error:** Could not connect to {endpoint}. Is Ollama running locally?"


def get_bot_reply(user_message, persona="general", provider="builtin", api_key="", model="", endpoint=""):
    """Main routing function to generate bot response."""
    persona_info = SmartAssistant.PERSONAS.get(persona, SmartAssistant.PERSONAS["general"])
    system_text = persona_info.get("system", "")

    if provider == "gemini" and api_key:
        return ExternalLLMEngine.call_gemini(api_key, model, user_message, system_text)
    elif provider == "openai" and api_key:
        return ExternalLLMEngine.call_openai(api_key, model, user_message, system_text)
    elif provider == "ollama":
        return ExternalLLMEngine.call_ollama(endpoint, model, user_message, system_text)
    else:
        return SmartAssistant.generate_response(user_message, persona)
