import telegram
import psutil
import time
import json
from telegram.ext import CommandHandler, Updater

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['bot_token']
INTERFACE = config['interface']
TCP_PORT = config['tcp_port']
UDP_PORT = config['udp_port']

bot = telegram.Bot(token=TOKEN)

print("Jitskis Dstat Bot Started.")

# Get the initial network I/O counters for the chosen interface
initial_net_io_counters = psutil.net_io_counters(pernic=True)[INTERFACE]

last_net_io_counters = initial_net_io_counters
last_time = time.time()

def stats(update, context):
    global last_net_io_counters, last_time
    current_time = time.time()
    current_net_io_counters = psutil.net_io_counters(pernic=True)[INTERFACE]
    incoming_bytes = current_net_io_counters.bytes_recv - last_net_io_counters.bytes_recv
    outgoing_bytes = current_net_io_counters.bytes_sent - last_net_io_counters.bytes_sent
    elapsed_time = current_time - last_time
    incoming_mbps = round(incoming_bytes / 1024 / 1024 / elapsed_time, 2)
    outgoing_mbps = round(outgoing_bytes / 1024 / 1024 / elapsed_time, 2)
    pps = (current_net_io_counters.packets_recv + current_net_io_counters.packets_sent - 
           last_net_io_counters.packets_recv - last_net_io_counters.packets_sent) / elapsed_time

    last_net_io_counters = current_net_io_counters
    last_time = current_time

    # Get system statistics
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent

    # Send statistics to user
    for i in range(5): # Send the message 5 times
        message = f"Incoming MBPS: {incoming_mbps}\n"
        message += f"Outgoing MBPS: {outgoing_mbps}\n"
        message += f"PPS: {pps}\n"
        message += f"CPU usage: {cpu_percent}%\n"
        message += f"RAM usage: {ram_percent}%"
        update.message.reply_text(message)
        time.sleep(5) # Wait 5 seconds before sending message again

def target(update, context):
    message = f"Host: {config['server_ip']}\n"
    message += f"Port: {TCP_PORT}/TCP {UDP_PORT}/UDP"
    update.message.reply_text(message)

# Create an updater object and add the handlers
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
stats_handler = CommandHandler('stats', stats)
dispatcher.add_handler(stats_handler)
target_handler = CommandHandler('target', target)
dispatcher.add_handler(target_handler)

# Start the bot
updater.start_polling()
updater.idle()
