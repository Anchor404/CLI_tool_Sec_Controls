import os
import json
import shutil
import hashlib
import logging
from datetime import datetime
from cryptography.fernet import Fernet

# Setup logging configuration
LOG_FILE = "task_tracker.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

KEY_FILE = "encryption_key.key"
FILE = "tasks.json"
HASH_FILE = "tasks_hash.sha256"
BACKUP_FOLDER = "backups/"

# Generate and save encryption key
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    logging.info(f"Encryption key created: {KEY_FILE}")

# Load encryption key from environment variable
def load_key():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable not set")
    return key.encode()  # Convert to bytes for Fernet

# Encrypt data before saving
def encrypt_data(data):
    key = load_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return encrypted

# Decrypt data after loading
def decrypt_data(encrypted_data):
    key = load_key()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_data).decode()
    return decrypted

# Secure file creation with restrictive permissions
def secure_file_creation(filepath):
    if not os.path.exists(filepath):
        os.umask(0o177)
        with open(filepath, 'wb') as file:
            file.write(encrypt_data(json.dumps([])))  # Write empty encrypted file
        logging.info(f"File created with secure permissions: {filepath}")

# Create a timestamped backup of the tasks.json file
def create_backup():
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_FOLDER, f"tasks_{timestamp}.json")
    shutil.copy(FILE, backup_file)
    logging.info(f"Backup created: {backup_file}")

# Calculate SHA-256 hash of data
def calculate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Save hash to a file
def save_hash(hash_value):
    with open(HASH_FILE, 'w') as hash_file:
        hash_file.write(hash_value)

# Verify the integrity of the tasks data using the hash
def verify_integrity(data):
    if not os.path.exists(HASH_FILE):
        logging.warning("Hash file not found. Integrity check skipped.")
        return True
    with open(HASH_FILE, 'r') as hash_file:
        stored_hash = hash_file.read()
    calculated_hash = calculate_hash(data)
    if stored_hash == calculated_hash:
        logging.info("Data integrity verified.")
        return True
    else:
        logging.error("Data integrity check failed! Possible tampering detected.")
        return False

# Load tasks from JSON file (decrypt and verify integrity)
def load_tasks():
    secure_file_creation(FILE)
    with open(FILE, 'rb') as file:
        encrypted_data = file.read()
        if not encrypted_data:
            return []
        decrypted_data = decrypt_data(encrypted_data)
        if verify_integrity(decrypted_data):
            return json.loads(decrypted_data)
        else:
            logging.error("Data integrity verification failed. Returning empty task list.")
            return []

# Save tasks to JSON file (encrypt, backup, and save hash)
def save_tasks(tasks):
    create_backup()
    data = json.dumps(tasks)
    encrypted_data = encrypt_data(data)
    with open(FILE, 'wb') as file:
        file.write(encrypted_data)
    hash_value = calculate_hash(data)
    save_hash(hash_value)
    logging.info("Tasks successfully saved, encrypted, and integrity hash updated.")

# Add a new task with input validation
def add_task():
    title = input("Enter task title: ").strip()
    if not title:
        logging.error("Task title cannot be empty")
        print("Error: Task title cannot be empty.")
        return

    description = input("Enter task description: ").strip()
    if not description:
        logging.error("Task description cannot be empty")
        print("Error: Task description cannot be empty.")
        return

    tasks = load_tasks()
    task = {"id": len(tasks) + 1, "title": title, "description": description, "status": "not done"}
    tasks.append(task)
    save_tasks(tasks)
    logging.info(f"Task '{title}' added with ID {task['id']}")
    print(f"Task '{title}' added.")

# Display existing tasks
def display_tasks():
    tasks = load_tasks()
    if not tasks:
        logging.info("No tasks available to display.")
        print("No tasks available.")
        return
    print("\nExisting Tasks:")
    for task in tasks:
        description = task.get('description', 'No description available')
        print(f"ID: {task['id']}, Title: {task['title']}, Description: {description}, Status: {task['status']}")

# Validate task ID input
def get_valid_task_id():
    tasks = load_tasks()
    while True:
        try:
            task_id = int(input("Enter task ID: ").strip())
            if not any(task['id'] == task_id for task in tasks):
                logging.error(f"Task ID {task_id} not found.")
                print(f"Error: Task ID {task_id} does not exist.")
            else:
                return task_id
        except ValueError:
            logging.error("Invalid input for task ID. Numeric value required.")
            print("Error: Please enter a valid numeric task ID.")

# Update task status with input validation
def update_task_status():
    task_id = get_valid_task_id()
    print(f"Is the task (ID {task_id}) 1. In progress 2. Done")
    while True:
        status_choice = input("Enter your choice (1 or 2): ").strip()
        if status_choice == '1':
            new_status = 'in progress'
            break
        elif status_choice == '2':
            new_status = 'done'
            break
        else:
            logging.error(f"Invalid choice for task status: {status_choice}")
            print("Error: Invalid choice. Please enter 1 or 2.")
    
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            save_tasks(tasks)
            logging.info(f"Task ID {task_id} status updated to '{new_status}'")
            print(f"Task ID {task_id} status updated to '{new_status}'.")

# Update task title with input validation
def update_task_title():
    task_id = get_valid_task_id()
    new_title = input("Enter new task title: ").strip()
    if not new_title:
        logging.error("Task title cannot be empty")
        print("Error: Task title cannot be empty.")
        return

    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = new_title
            save_tasks(tasks)
            logging.info(f"Task ID {task_id} title updated to '{new_title}'")
            print(f"Task ID {task_id} title updated to '{new_title}'.")

# Update task description with input validation
def update_task_description():
    task_id = get_valid_task_id()
    new_description = input("Enter new task description: ").strip()
    if not new_description:
        logging.error("Task description cannot be empty")
        print("Error: Task description cannot be empty.")
        return

    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['description'] = new_description
            save_tasks(tasks)
            logging.info(f"Task ID {task_id} description updated")
            print(f"Task ID {task_id} description updated.")

# Main function to handle user prompts and actions
def main():
    while True:
        display_tasks()

        print("\nChoose an action:")
        print("1. Add a new task")
        print("2. Update task status (In progress / Done)")
        print("3. Change the title of a task")
        print("4. Change the description of a task")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            add_task()

        elif choice == '2':
            update_task_status()

        elif choice == '3':
            update_task_title()

        elif choice == '4':
            update_task_description()

        elif choice == '5':
            logging.info("User exited the task tracker")
            print("Exiting Task Tracker. Goodbye!")
            break

        else:
            logging.warning(f"Invalid choice: {choice}")
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    logging.info("Task Tracker started")
    main()