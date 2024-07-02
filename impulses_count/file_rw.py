def read_counter_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return int(file.read())
    except (OSError, ValueError) as e:
        print(f"Failed to read from {filename}. Creating file...")
        write_counter_to_file(filename, 0)  # Create file if it doesn't exist
        return 0

def write_counter_to_file(filename, counter):
    try:
        with open(filename, 'w') as file:
            file.write(str(counter))
    except OSError as e:
        print(f"Failed to write to {filename}: {e}")
