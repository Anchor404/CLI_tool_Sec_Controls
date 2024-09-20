import os
import json
import shutil
from cryptography.fernet import Fernet

KEY_FILE = "encryption_key.key"
FILE = "tasks.json"

# Generate and save encryption key
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    print(f"Encryption key created: {KEY_FILE}")

# Load encryption key
def load_key():
    if not os.path.exists(KEY_FILE):
        print("Encryption key not found. Generating new key...")
        generate_key()
    else:
        print(f"Encryption key loaded from {KEY_FILE}")
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

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
        os.umask(0o177)  # Only the owner can read/write
        with open(filepath, 'wb') as file:
            file.write(encrypt_data(json.dumps([])))  # Write empty encrypted file

# Backup tasks.json before making changes (backing up the encrypted file)
def backup_tasks_file():
    if os.path.exists(FILE):
        backup_file = FILE + ".bak"
        shutil.copy(FILE, backup_file)
        print(f"Encrypted backup created: {backup_file}")

# Load tasks from JSON file (decrypt the data)
def load_tasks():
    secure_file_creation(FILE)
    with open(FILE, 'rb') as file:
        encrypted_data = file.read()
        if not encrypted_data:
            return []
        decrypted_data = decrypt_data(encrypted_data)
        return json.loads(decrypted_data)

# Save tasks to JSON file (encrypt the data)
def save_tasks(tasks):
    backup_tasks_file()
    with open(FILE, 'wb') as file:
        data = json.dumps(tasks)
        encrypted_data = encrypt_data(data)
        file.write(encrypted_data)

# Add a new task with input validation     
def add_task():
    title = input("Enter task title: ").strip()
    if not title:
        print("Error: Task title cannot be empty.")
        return

    description = input("Enter task description: ").strip()
    if not description:
        print("Error: Task description cannot be empty.")
        return

    tasks = load_tasks()
    task = {"id": len(tasks) + 1, "title": title, "description": description, "status": "not done"}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task '{title}' added.")

# Display existing tasks
def display_tasks():
    tasks = load_tasks()
    if not tasks:
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
                print(f"Error: Task ID {task_id} does not exist.")
            else:
                return task_id
        except ValueError:
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
            print("Error: Invalid choice. Please enter 1 or 2.")
    
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            save_tasks(tasks)
            print(f"Task ID {task_id} status updated to '{new_status}'.")

# Update task title with input validation
def update_task_title():
    task_id = get_valid_task_id()
    new_title = input("Enter new task title: ").strip()
    if not new_title:
        print("Error: Task title cannot be empty.")
        return

    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = new_title
            save_tasks(tasks)
            print(f"Task ID {task_id} title updated to '{new_title}'.")

# Update task description with input validation
def update_task_description():
    task_id = get_valid_task_id()
    new_description = input("Enter new task description: ").strip()
    if not new_description:
        print("Error: Task description cannot be empty.")
        return

    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['description'] = new_description
            save_tasks(tasks)
            print(f"Task ID {task_id} description updated.")

# Main function to handle user prompts and actions
def main():
    while True:
        # Display existing tasks
        display_tasks()

        # Present menu options to the user
        print("\nChoose an action:")
        print("1. Add a new task")
        print("2. Update task status (In progress / Done)")
        print("3. Change the title of a task")
        print("4. Change the description of a task")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        # Option 1: Add a new task
        if choice == '1':
            add_task()

        # Option 2: Update task status
        elif choice == '2':
            update_task_status()

        # Option 3: Change the title of a task
        elif choice == '3':
            update_task_title()

        # Option 4: Change the description of a task
        elif choice == '4':
            update_task_description()

        # Option 5: Exit the program
        elif choice == '5':
            print("Exiting Task Tracker. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
