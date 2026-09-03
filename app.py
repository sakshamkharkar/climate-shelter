"""
Python Web Application Server for AI Chatbot.
Provides HTTP API endpoints and static web asset serving.
Runs standard Python 3 http.server on localhost:5000.
"""

import os
import sys
import json
import sqlite3
import uuid
import mimetypes
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from bot_engine import get_bot_reply, SmartAssistant

PORT = 5000
DB_FILE = os.path.join(os.path.dirname(__file__), "chatbot.db")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def init_db():
    """Initializes SQLite database schema."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            persona TEXT DEFAULT 'general',
            FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


class ChatRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler serving REST API and Web UI."""

    def log_message(self, format, *args):
        """Clean log output."""
        sys.stdout.write(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]}\n")

    def _send_json(self, data, status=200):
        """Sends a JSON HTTP response."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filepath, mime_type):
        """Sends a static file response."""
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_error(404, "File Not Found")

    def do_OPTIONS(self):
        """Handles CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handles GET HTTP requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # 1. API: Get Personas
        if path == "/api/personas":
            personas = [
                {"key": k, "name": v["name"], "system": v["system"], "greeting": v["greeting"]}
                for k, v in SmartAssistant.PERSONAS.items()
            ]
            return self._send_json({"personas": personas})

        # 2. API: List Conversations
        if path == "/api/conversations":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.title, c.created_at, c.updated_at, COUNT(m.id) as msg_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
            """)
            rows = cursor.fetchall()
            conn.close()
            convs = [
                {"id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3], "msg_count": r[4]}
                for r in rows
            ]
            return self._send_json({"conversations": convs})

        # 3. API: Get Single Conversation Messages
        if path.startswith("/api/conversations/"):
            conv_id = path.split("/")[-1]
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender, text, timestamp, persona
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
            """, (conv_id,))
            rows = cursor.fetchall()
            conn.close()
            msgs = [
                {"sender": r[0], "text": r[1], "timestamp": r[2], "persona": r[3]}
                for r in rows
            ]
            return self._send_json({"conversation_id": conv_id, "messages": msgs})

        # 4. Static Files Serving
        if path == "/" or path == "/index.html":
            file_path = os.path.join(STATIC_DIR, "index.html")
            return self._send_file(file_path, "text/html")
        else:
            rel_path = path.lstrip("/")
            file_path = os.path.join(STATIC_DIR, rel_path)
            if os.path.isfile(file_path):
                mime, _ = mimetypes.guess_type(file_path)
                return self._send_file(file_path, mime or "application/octet-stream")

        self.send_error(404, "Page Not Found")

    def do_POST(self):
        """Handles POST HTTP requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            data = json.loads(post_data.decode("utf-8"))
        except Exception:
            data = {}

        # 1. API: New Conversation
        if path == "/api/conversations/new":
            conv_id = str(uuid.uuid4())
            now_str = datetime.now().isoformat()
            title = data.get("title", "New Chat")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (conv_id, title, now_str, now_str))
            conn.commit()
            conn.close()
            return self._send_json({"id": conv_id, "title": title, "created_at": now_str})

        # 2. API: Send Chat Message
        if path == "/api/chat":
            user_msg = data.get("message", "").strip()
            conv_id = data.get("conversation_id")
            persona = data.get("persona", "general")
            provider = data.get("provider", "builtin")
            api_key = data.get("api_key", "")
            model = data.get("model", "")
            endpoint = data.get("endpoint", "")

            if not user_msg:
                return self._send_json({"error": "Message cannot be empty"}, status=400)

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            now_str = datetime.now().isoformat()
            display_time = datetime.now().strftime("%I:%M %p")

            # Create conversation if not specified or doesn't exist
            if not conv_id:
                conv_id = str(uuid.uuid4())
                # Auto title from first 30 chars of user message
                title = user_msg[:30] + ("..." if len(user_msg) > 30 else "")
                cursor.execute("""
                    INSERT INTO conversations (id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (conv_id, title, now_str, now_str))
            else:
                # Check if conversation exists
                cursor.execute("SELECT id, title FROM conversations WHERE id = ?", (conv_id,))
                row = cursor.fetchone()
                if not row:
                    title = user_msg[:30] + ("..." if len(user_msg) > 30 else "")
                    cursor.execute("""
                        INSERT INTO conversations (id, title, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (conv_id, title, now_str, now_str))
                elif row[1] == "New Chat":
                    # Update title if it was "New Chat"
                    new_title = user_msg[:30] + ("..." if len(user_msg) > 30 else "")
                    cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (new_title, conv_id))

            # Store user message
            cursor.execute("""
                INSERT INTO messages (conversation_id, sender, text, timestamp, persona)
                VALUES (?, ?, ?, ?, ?)
            """, (conv_id, "user", user_msg, display_time, persona))

            # Generate bot reply
            bot_reply = get_bot_reply(
                user_message=user_msg,
                persona=persona,
                provider=provider,
                api_key=api_key,
                model=model,
                endpoint=endpoint
            )

            # Store bot reply
            cursor.execute("""
                INSERT INTO messages (conversation_id, sender, text, timestamp, persona)
                VALUES (?, ?, ?, ?, ?)
            """, (conv_id, "bot", bot_reply, display_time, persona))

            # Update conversation timestamp
            cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now_str, conv_id))
            conn.commit()
            conn.close()

            return self._send_json({
                "success": True,
                "conversation_id": conv_id,
                "reply": bot_reply,
                "timestamp": display_time
            })

        self.send_error(404, "Endpoint Not Found")

    def do_DELETE(self):
        """Handles DELETE HTTP requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path.startswith("/api/conversations/"):
            conv_id = path.split("/")[-1]
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
            conn.commit()
            conn.close()
            return self._send_json({"success": True, "deleted": conv_id})

        self.send_error(404, "Endpoint Not Found")

    def do_PUT(self):
        """Handles PUT HTTP requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            data = json.loads(post_data.decode("utf-8"))
        except Exception:
            data = {}

        if path.startswith("/api/conversations/") and path.endswith("/title"):
            parts = path.split("/")
            conv_id = parts[3]
            new_title = data.get("title", "Chat").strip()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (new_title, conv_id))
            conn.commit()
            conn.close()
            return self._send_json({"success": True, "id": conv_id, "title": new_title})

        self.send_error(404, "Endpoint Not Found")


def run_server():
    """Runs HTTP server daemon."""
    init_db()
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, ChatRequestHandler)
    print(f"AI Chatbot Server running on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
