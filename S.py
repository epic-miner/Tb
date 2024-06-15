import telebot
import subprocess
import shlex
import os
import re

# Replace 'YOUR_TOKEN' with your actual bot token obtained from BotFather
TOKEN = '6306399777:AAGO0tUcRAL_jbApX45y8VwBqCCQ6gXa5uw'

# Create bot object
bot = telebot.TeleBot(TOKEN)

# Dictionary to store command history per user
command_history = {}

# Function to execute shell commands securely
def execute_command(command):
    try:
        # Split the command safely using shlex
        cmd_parts = shlex.split(command)
        
        # Execute the command securely
        result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)  # Timeout set to 30 seconds
        
        # Return the command output
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed with return code {e.returncode}. Output:\n{e.output.strip()}"
    except subprocess.TimeoutExpired:
        return "Command execution timed out."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to send long messages in chunks
def send_long_message(chat_id, text):
    max_message_length = 3000  # Telegram message length limit
    for i in range(0, len(text), max_message_length):
        bot.send_message(chat_id, text[i:i+max_message_length])

# Handler for /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hi! I'm your bot. Send me a command to execute on the server.")

# Handler for /exec command
@bot.message_handler(commands=['exec'])
def handle_execute(message):
    # Get the command sent by the user
    command = message.text.split(' ', 1)[1]
    
    # Execute the command securely
    output = execute_command(command)
    
    # Store command in history
    user_id = message.from_user.id
    if user_id not in command_history:
        command_history[user_id] = []
    command_history[user_id].append(f"Command: {command}\nOutput:\n{output}")
    
    # Send the output of the command back to the user
    if len(output) <= 4096:
        bot.send_message(message.chat.id, f"Command: `{command}`\nOutput:\n```\n{output}\n```", parse_mode='Markdown')
    else:
        bot.send_document(message.chat.id, data=output.encode('utf-8'), caption=f"Command: `{command}`", parse_mode='Markdown')

# Handler for /history command
@bot.message_handler(commands=['history'])
def handle_history(message):
    send_command_history(message.chat.id, message.from_user.id)

# Inline keyboard pagination for command history
@bot.callback_query_handler(func=lambda call: call.data.startswith('page'))
def callback_paging(call):
    user_id = call.from_user.id
    if user_id in command_history:
        history = command_history[user_id]
        if history:
            page_number = int(call.data.split('_')[1])
            start_index = (page_number - 1) * 5
            end_index = start_index + 5
            page_commands = history[start_index:end_index]
            send_long_message(call.message.chat.id, "\n".join(page_commands))
        else:
            bot.send_message(call.message.chat.id, "Command history is empty.")
    else:
        bot.send_message(call.message.chat.id, "Command history is empty.")

# Function to send command history in chunks
def send_command_history(chat_id, user_id):
    if user_id in command_history:
        history = command_history[user_id]
        if history:
            send_long_message(chat_id, "Command History:\n" + "\n".join(history))
        else:
            bot.send_message(chat_id, "Command history is empty.")
    else:
        bot.send_message(chat_id, "Command history is empty.")

# Error handling
@bot.message_handler(func=lambda message: True)
def handle_invalid(message):
    bot.send_message(message.chat.id, "Invalid command. Please use /exec <command> to execute a command.")

# Polling loop
bot.polling()
