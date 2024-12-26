from flask import Flask, render_template, request, session
import google.generativeai as genai
import json  


gemini_api_key = "AIzaSyC2mVAcDRYqK9GhIcyqN1p9VPmni6CFoxw"  
genai.configure(api_key=gemini_api_key)


app = Flask(__name__)


app.secret_key = 'ca746523372903c330780ff0d4013ac5' 

@app.route('/')
def index():
    """
    Home route to render the index page.
    """
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """
    Chat route to handle user messages and display the chat interface.
    Manages chat history using Flask sessions.
    """
    if 'chat_history' not in session:
        session['chat_history'] = []  # Initialize chat history

    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        bot_message = "Something went wrong."  # Default error message

        if user_message:
            try:
                # Call the Gemini API
                response = genai.GenerativeModel("gemini-1.5-flash").generate_content(user_message)
                
                # Convert response to a dictionary
                response_dict = response.to_dict()
                print("Raw API Response (as dict):", json.dumps(response_dict, indent=2))

                # Extract the bot's message
                if "candidates" in response_dict and len(response_dict["candidates"]) > 0:
                    parts = response_dict["candidates"][0].get("content", {}).get("parts", [])
                    if len(parts) > 0:
                        bot_message = parts[0].get("text", "No text found").strip()
                    else:
                        bot_message = "No valid content parts found in response."
                else:
                    bot_message = "No candidates found in response."

            except Exception as e:
                # Log the error and display a fallback message
                print(f"Error during API call or response processing: {str(e)}")
                bot_message = f"Error extracting bot message: {str(e)}"

        # Append user and bot messages to chat history
        session['chat_history'].append({'user': user_message, 'bot': bot_message})
        session.modified = True  # Mark session as modified to save changes

    # Render the chat page with updated history
    return render_template('chat.html', chat_history=session['chat_history'])


if __name__ == '__main__':
    app.run(debug=True)
