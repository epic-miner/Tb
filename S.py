import telebot
import subprocess
import shlex

# Replace 'YOUR_TOKEN' with your actual bot token obtained from BotFather
TOKEN = '6306399777:AAGO0tUcRAL_jbApX45y8VwBqCCQ6gXa5uw'

# Create bot object
bot = telebot.TeleBot(TOKEN)

# Dictionary to store session information for each user
session_data = {}

# Function to execute shell commands securely
def execute_command(command):
    try:
        # Split the command safely using shlex
        cmd_parts = shlex.split(command)
        
        # Execute the command securely
        result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=60)
        
        # Return the command output
        return result.stdout.strip()
    
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out."
    except Exception as e:
        return f"Error: {str(e)}"

# Handler for /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hi! I'm your terminal-like bot. Send me a command to execute on the server.")

# Handler for user messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.chat.id
        
        # Check if the user has an active session
        if user_id not in session_data:
            session_data[user_id] = {'current_command': ''}
        
        # Retrieve the current command being constructed
        current_command = session_data[user_id]['current_command']
        
        # Concatenate the incoming message to the current command
        if message.text.startswith('/'):
            bot.send_message(user_id, "Invalid command. Please continue typing your current command or start a new one.")
        else:
            session_data[user_id]['current_command'] += message.text.strip() + ' '
            bot.send_message(user_id, f"Command in progress: `{session_data[user_id]['current_command']}`", parse_mode='Markdown')
    
    except Exception as e:
        bot.send_message(user_id, f"Error handling your message: {str(e)}")

# Handler for /exec command to execute the constructed command
@bot.message_handler(commands=['exec'])
def handle_execute(message):
    try:
        user_id = message.chat.id
        
        # Check if there is a command to execute
        if user_id in session_data and 'current_command' in session_data[user_id]:
            command = session_data[user_id]['current_command'].strip()
            
            # Execute the command securely
            output = execute_command(command)
            
            # Clear current command after execution
            session_data[user_id]['current_command'] = ''
            
            # Send the output of the command back to the user
            if output:
                if len(output) > 4000:
                    bot.send_message(user_id, f"Command: `{command}`\nOutput:\n```\n{output[:4000]}\n```", parse_mode='Markdown')
                else:
                    bot.send_message(user_id, f"Command: `{command}`\nOutput:\n```\n{output}\n```", parse_mode='Markdown')
            else:
                bot.send_message(user_id, f"No output returned for command: `{command}`", parse_mode='Markdown')
        
        else:
            bot.send_message(user_id, "No command to execute. Start typing a command or continue with your current command.")

    except Exception as e:
        bot.send_message(user_id, f"Error executing command: {str(e)}")

# Handler for /cancel command to cancel the current command
@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    try:
        user_id = message.chat.id
        
        # Check if there is a command in progress to cancel
        if user_id in session_data and 'current_command' in session_data[user_id]:
            session_data[user_id]['current_command'] = ''
            bot.send_message(user_id, "Current command cancelled. Start typing a new command.")
        else:
            bot.send_message(user_id, "No command in progress to cancel.")
    
    except Exception as e:
        bot.send_message(user_id, f"Error cancelling command: {str(e)}")

# Error handling
@bot.message_handler(func=lambda message: True)
def handle_invalid(message):
    bot.send_message(message.chat.id, "Invalid command. Please start a new command or continue typing your current command.")

# Polling loop
bot.polling()
