from telegram import send_text_to_telegram

# Function to read counter from file
def read_counter_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return int(file.read())
    except (OSError, ValueError) as e:
        print(f"Failed to read from {filename}. Creating file...")
        write_counter_to_file(filename, 0)  # Create file if it doesn't exist
        return 0

# Function to write counter to file
def write_counter_to_file(filename, counter):
    try:
        with open(filename, 'w') as file:
            file.write(str(counter))
    except OSError as e:
        print(f"Failed to write to {filename}: {e}")

# Function to calculate consumption and send report
def send_report(bot_token, chat_ids, period):
    if period not in ['daily', 'monthly']:
        raise ValueError("Invalid period. Use 'daily' or 'monthly'.")

    hot_last_period = read_counter_from_file(f'hot_last_{period}')
    hot_total = read_counter_from_file('hot')
    cold_last_period = read_counter_from_file(f'cold_last_{period}')
    cold_total = read_counter_from_file('cold')

    hot_this_period = hot_total - hot_last_period
    cold_this_period = cold_total - cold_last_period

    write_counter_to_file(f'hot_last_{period}', hot_total)
    write_counter_to_file(f'cold_last_{period}', cold_total)

    message = f"{period} report: {hot_this_period}0 liters of hot water and {cold_this_period}0 liters of cold water"
    send_text_to_telegram(bot_token, chat_ids, message)
    print(message)
