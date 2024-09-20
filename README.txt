# Task Manager CLI

This is a Command Line Interface (CLI) Task Manager application that allows users to manage tasks with encryption, logging, and data integrity checks. The application runs entirely from the command line, and tasks are stored in an encrypted JSON file for security.

## Features

- Add, update, and delete tasks.
- Mark tasks as in progress or done.
- List all tasks, tasks that are done, and tasks that are in progress.
- Automatic backups of task data with timestamped backups.
- Encrypted storage of task data using the `cryptography` library.
- SHA-256 hash integrity checks to ensure that the data has not been tampered with.
- Logging of important actions like task creation, updates, and status changes.
- Environment isolation using a Python virtual environment.
- Access control with secure file permissions and encryption key stored as an environment variable.

## Prerequisites

- Python 3.x
- A working terminal or command prompt

## Setup Instructions

1. **Clone the repository or download the files** to your local machine.
   
2. **Navigate to the project directory**:
   ```bash
   cd /path/to/your/project/directory
3. Create and activate a python virtual environment:
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
4. Install the required dependencies:
pip install -r requirements.txt

5. Set the encryption key (make sure the encryption_key.key file is in the project directory):
export ENCRYPTION_KEY=$(cat /path/to/your/project/directory/encryption_key.key)
Optionally, add this line to your .bashrc or .zshrc file to persist the key across terminal sessions.

6. Run the Task Manager

python3 TaskManager.py

