import requests
import tkinter as tk

class LLM_API():
    def __init__(self,ngrokURL) -> None:
        self.ngrokURL = ngrokURL
        pass

    def generate(self, query:str, temperature:float=0.1, max_tokens:int=200):
        self.data = {
                "inputs": query,
                #paramaters can be found here https://abetlen.github.io/llama-cpp-python/#llama_cpp.llama.Llama.create_completion
                "parameters": {"temperature":temperature,
                                "max_tokens":max_tokens}
                #higher temperature, more creative response is, lower more precise
                #max_token is the max amount of (simplified) "words" allowed to be generated
                }
 
        print(self.data)
        
        # Send the POST request
        response = requests.post(ngrokURL + "/generate/", json=self.data)

        # Check the response
        if response.status_code == 200:
            result = response.json()
            return "Generated Text:\n" + self.data["inputs"] + result["generated_text"].strip()
            # print("Generated Text:\n", data["inputs"], result["generated_text"].strip())
        else:
            return "Request failed with status code:"+ str(response.status_code)
            # print("Request failed with status code:", response.status_code)

############################################################################################################################################
    

class ChatbotGUI:
    def __init__(self, master, llm_api):
        self.master = master
        master.title("Chatbot Page")
        master.geometry("600x400")  # Set window size
        master.configure(bg="#2c3e50")  # Set dark background color

        # Model ID entry
        self.model_id_label = tk.Label(master, text="Model ID:", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 12))
        self.model_id_label.pack(padx=20, pady=(10, 5), anchor=tk.W)

        self.model_id_entry = tk.Entry(master, bg="#34495e", fg="#ecf0f1", font=("Arial", 12))
        self.model_id_entry.pack(fill=tk.X, padx=20, pady=(0, 10), ipady=5)  # Allow expansion and padding

        # Model ID button
        self.model_id_button = tk.Button(master, text="Apply", bg="#3498db", fg="white", font=("Arial", 12), command=self.apply_model_id)
        self.model_id_button.pack(padx=20, pady=(0, 10), ipadx=10)  # Adjusted padding and size

        # Create chat display area
        self.chat_display = tk.Text(master, bg="#34495e", fg="#ecf0f1", font=("Arial", 12), wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Input prompt label
        self.prompt_label = tk.Label(master, text="Input your prompts:", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 12))
        self.prompt_label.pack(padx=20, pady=(10, 5), anchor=tk.W)

        # Send button for prompt
        self.send_button = tk.Button(master, text="Send", bg="#3498db", fg="white", font=("Arial", 12), command=self.send_message)
        self.send_button.pack(side=tk.BOTTOM, padx=20, pady=(10, 20), ipadx=10)  # Adjusted padding and size
        # Input prompt entry
        self.prompt_entry = tk.Text(master, bg="#34495e", fg="#ecf0f1", font=("Arial", 12), wrap=tk.WORD)
        self.prompt_entry.pack(fill=tk.Y, padx=20, pady=(0, 10), ipady=5, expand=True)  # Allow expansion and padding

        # Initialize model prefix
        self.model_prefix = "Llama 2"

        self.llm_api = llm_api



    def apply_model_id(self):
        model_id = self.model_id_entry.get()
        # Update model prefix with user input
        self.model_prefix = model_id if model_id else "Llama 2"
        self.display_message(f"Model ID applied: {self.model_prefix}", sender="bot")
        # self.model_id_entry.delete(0, tk.END)  # Clear the entry after applying

    def send_message(self):
        user_input = self.prompt_entry.get("1.0", tk.END).strip()  # Get text from start to end
        if user_input:
            model_generation = self.llm_api.generate(user_input).strip()
            self.display_message(user_input, sender="user")
            # Here you can implement logic to process the user's input and generate a response
            # For demonstration purposes, let's just echo back the user's input as the bot's response
            self.display_message(model_generation, sender="bot")
            self.prompt_entry.delete("1.0", tk.END)  # Clear the input after sending

    def display_message(self, message, sender="bot"):
        if sender == "bot":
            tag_config = {"foreground": "#3498db", "font": ("Arial", 12, "bold")}
            prefix = f"{self.model_prefix}:"
        else:
            tag_config = {"foreground": "#ecf0f1", "font": ("Arial", 12)}
            prefix = "You:"
        self.chat_display.tag_config(sender, **tag_config)
        self.chat_display.insert(tk.END, f"{prefix} {message}\n", sender)
        self.chat_display.see(tk.END)  # Scroll to the end of the text widget


if __name__ == "__main__":
    # Define the URL for the FastAPI endpoint
    ngrokURL = 'https://3482-35-185-209-85.ngrok-free.app'
    
    # Create the LLM
    llm_api = LLM_API(ngrokURL)

    # Create the main window
    root = tk.Tk()
    app = ChatbotGUI(root, llm_api)
    root.mainloop()

