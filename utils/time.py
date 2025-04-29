from datetime import datetime


def extract_timestamp(url):
    timestamp_str = url.split('_')[0]  # Extract the timestamp part (e.g., '20241124-205115')
    date = timestamp_str.split('-')[1] + "-" + timestamp_str.split('-')[2]
    return datetime.strptime(date, "%Y%m%d-%H%M%S")