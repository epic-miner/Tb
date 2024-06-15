import telebot
import subprocess
import shlex

# Replace 'YOUR_TOKEN' with your actual bot token obtained from BotFather
TOKEN = '6306399777:AAGO0tUcRAL_jbApX45y8VwBqCCQ6gXa5uw'

# Maximum length of each message chunk
MAX_MESSAGE_LENGTH = 4000  # Slightly below Telegram's maximum for safety

# Create bot object
bot = telebot.TeleBot(TOKEN)

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
def send_long_message(chat_id, text):
    # Split text into chunks
    chunks = [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]
    
    # Send each chunk as a separate message
    for chunk in chunks:
        bot.send_message(chat_id, chunk, parse_mode='Markdown')

# Handler for /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hi! I'm your bot. Send me a command to execute on the server.")

# Handler for /exec command
@bot.message_handler(commands=['exec'])
def handle_execute(message):
    try:
        # Get the command sent by the user
        command = message.text.split(' ', 1)[1]
        
        # Execute the command securely
        output = execute_command(command)
        
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

# Error handling
@bot.message_handler(func=lambda message: True)
def handle_invalid(message):
    bot.send_message(message.chat.id, "Invalid command. Please use /exec <command> to execute a command.")

# Polling loop
bot.polling()
