
import json
import requests
import os
import threading
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

API_KEY = "AIzaSyBvfFBYUKTfG5u2KBlsotww4AboJAm2gvA"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

class ChatHistory:
    def __init__(self):
        self.chats = []
        self.load_from_file()

    def load_from_file(self):
        try:
            if os.path.exists("chat_history.json"):
                with open("chat_history.json", "r") as f:
                    self.chats = json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")

    def save_to_file(self):
        try:
            with open("chat_history.json", "w") as f:
                json.dump(self.chats, f, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")

    def add_chat(self, role, content):
        self.chats.append({"role": role, "content": content})
        self.save_to_file()

    def clear_history(self):
        self.chats = []
        self.save_to_file()

class ChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HEAR ME OUT - AI Chat")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        self.chat_history = ChatHistory()
        self.setup_ui()
        self.load_chat_history()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2d2d2d", height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="HEAR ME OUT", 
            font=("Arial", 20, "bold"),
            bg="#2d2d2d",
            fg="#00d4ff"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Developed By Raviraj Sharma",
            font=("Arial", 10),
            bg="#2d2d2d",
            fg="#888888"
        )
        subtitle_label.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(
            header_frame,
            text="Clear Chat",
            command=self.clear_chat,
            bg="#ff4444",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5
        )
        clear_btn.pack(side=tk.RIGHT, padx=20)
        
        # Chat display area
        chat_frame = tk.Frame(self.root, bg="#1e1e1e")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="white",
            relief=tk.FLAT,
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for styling
        self.chat_display.tag_config("user", foreground="#00d4ff", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("ai", foreground="#4ade80", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("message", foreground="#ffffff", font=("Arial", 11))
        self.chat_display.tag_config("time", foreground="#888888", font=("Arial", 9))
        
        # Input area
        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=("Arial", 11),
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="white",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", self.handle_enter)
        self.input_field.bind("<Shift-Return>", lambda e: None)
        
        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#00d4ff",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            width=10
        )
        send_btn.pack(side=tk.RIGHT)
        
    def load_chat_history(self):
        """Load existing chat history into the display"""
        if not self.chat_history.chats:
            self.display_welcome_message()
        else:
            for chat in self.chat_history.chats:
                if chat["role"] == "user":
                    self.display_message("You", chat["content"], "user")
                else:
                    self.display_message("AI", chat["content"], "ai")
    
    def display_welcome_message(self):
        """Display welcome message when no chat history exists"""
        self.chat_display.config(state=tk.NORMAL)
        welcome = "\n\n✨ Welcome to HEAR ME OUT ✨\n\n"
        welcome += "Start a conversation and explore the power of AI.\n"
        welcome += "Your chat history will be saved automatically.\n\n"
        self.chat_display.insert(tk.END, welcome, "time")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def display_message(self, sender, message, tag):
        """Display a message in the chat window"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add sender name with styling
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        
        # Add message content
        self.chat_display.insert(tk.END, f"{message}\n\n", "message")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def handle_enter(self, event):
        """Handle Enter key press"""
        if not event.state & 0x1:  # Check if Shift is not pressed
            self.send_message()
            return "break"
    
    def send_message(self):
        """Send user message and get AI response"""
        user_input = self.input_field.get("1.0", tk.END).strip()
        
        if not user_input:
            return
        
        # Display user message
        self.display_message("You", user_input, "user")
        self.chat_history.add_chat("user", user_input)
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Show typing indicator
        self.display_typing_indicator()
        
        # Get AI response in a separate thread
        thread = threading.Thread(target=self.get_ai_response, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def display_typing_indicator(self):
        """Show typing indicator"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "AI is typing...\n", "time")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def remove_typing_indicator(self):
        """Remove typing indicator"""
        self.chat_display.config(state=tk.NORMAL)
        content = self.chat_display.get("1.0", tk.END)
        if "AI is typing..." in content:
            # Find and delete the typing indicator line
            index = self.chat_display.search("AI is typing...", "1.0", tk.END)
            if index:
                self.chat_display.delete(index, f"{index} lineend + 1c")
        self.chat_display.config(state=tk.DISABLED)
    
    def get_ai_response(self, user_text):
        """Get response from AI API"""
        try:
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": user_text}]
                        }
                    ]
                },
                timeout=30
            )
            
            if response.status_code != 200:
                ai_response = f"Error: HTTP error! status: {response.status_code}"
            else:
                data = response.json()
                ai_response = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response from AI.").strip()
                ai_response = re.sub(r'\*', '', ai_response)
            
            # Update UI in main thread
            self.root.after(0, self.update_with_response, ai_response)
            
        except Exception as e:
            error_msg = f"Error: Unable to get a response from the server. {str(e)}"
            self.root.after(0, self.update_with_response, error_msg)
    
    def update_with_response(self, response):
        """Update UI with AI response"""
        self.remove_typing_indicator()
        self.display_message("AI", response, "ai")
        self.chat_history.add_chat("assistant", response)
    
    def clear_chat(self):
        """Clear all chat history"""
        result = messagebox.askyesno(
            "Clear Chat",
            "Are you sure you want to delete all chats?"
        )
        if result:
            self.chat_history.clear_history()
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.display_welcome_message()

def main():
    root = tk.Tk()
    app = ChatUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()