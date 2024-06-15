import telebot
import subprocess
import shlex
import asyncio

# Replace 'YOUR_TOKEN' with your actual bot token obtained from BotFather
TOKEN = '6306399777:AAGO0tUcRAL_jbApX45y8VwBqCCQ6gXa5uw'

# Maximum length of each message chunk
MAX_MESSAGE_LENGTH = 4000  # Slightly below Telegram's maximum for safety

# Create bot object
bot = telebot.TeleBot(TOKEN)

# Dictionary to store session information for pagination
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

# Function to send long messages by splitting into chunks
async def send_long_message(chat_id, text):
    # Split text into chunks
    chunks = [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]
    
    # Send each chunk as a separate message
    for chunk in chunks:
        await bot.send_message(chat_id, chunk, parse_mode='Markdown')

# Handler for /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hi! I'm your ultra-advanced bot. Send me a command to execute on the server.")

# Handler for /exec command
@bot.message_handler(commands=['exec'])
def handle_execute(message):
    try:
        # Get the command sent by the user
        command = message.text.split(' ', 1)[1]
        
        # Execute the command securely
        output = execute_command(command)
        
        # Store session data for pagination
        session_data[message.chat.id] = {'output': output}
        
        # Send the output of the command back to the user
        if output:
            if len(output) > MAX_MESSAGE_LENGTH:
                bot.send_message(message.chat.id, f"Command: `{command}`\nOutput:\n```\n{output[:MAX_MESSAGE_LENGTH]}\n```", parse_mode='Markdown')
                send_long_message(message.chat.id, output[MAX_MESSAGE_LENGTH:])
            else:
                bot.send_message(message.chat.id, f"Command: `{command}`\nOutput:\n```\n{output}\n```", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"No output returned for command: `{command}`", parse_mode='Markdown')
    
    except IndexError:
        bot.send_message(message.chat.id, "No command provided. Please use /exec <command>.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error executing command: {str(e)}")

# Handler for /next command to paginate long outputs
@bot.message_handler(commands=['next'])
def handle_next(message):
    try:
        # Get session data for the user
        if message.chat.id in session_data and 'output' in session_data[message.chat.id]:
            output = session_data[message.chat.id]['output']
            
            # Get the page number from session data or default to 1
            page_number = session_data[message.chat.id].get('page_number', 1)
            
            # Calculate start and end indexes for pagination
            start_index = (page_number - 1) * MAX_MESSAGE_LENGTH
            end_index = start_index + MAX_MESSAGE_LENGTH
            
            # Get the current page text
            current_page = output[start_index:end_index]
            
            # Send the current page
            bot.send_message(message.chat.id, f"Page {page_number}:\n```\n{current_page}\n```", parse_mode='Markdown')
            
            # Update page number for next /next command
            session_data[message.chat.id]['page_number'] = page_number + 1
        
        else:
            bot.send_message(message.chat.id, "No stored output found. Execute a command using /exec first.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error fetching next page: {str(e)}")

# Error handling
@bot.message_handler(func=lambda message: True)
def handle_invalid(message):
    bot.send_message(message.chat.id, "Invalid command. Please use /exec <command> to execute a command.")

# Polling loop
bot.polling()
