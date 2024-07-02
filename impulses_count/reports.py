from telegram import send_text_to_telegram
from file_rw import read_counter_from_file, write_counter_to_file

# Function to calculate consumption and send report
def send_report(bot_token, chat_ids, period):

#    print(f"Preparing to send {period} report.")  # Debugging line
#    print(f"Type of period: {type(period)}")
#    print(f"Period value: '{period}'")
    
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
