#!/Users/khimichvladyslav/rd_homework/venv/bin/python3

import os
import subprocess
from datetime import datetime, timedelta
import random


def ensure_permissions():
    command = f"echo sudo chmod -R u+rwx dz1"
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    print(f"Using support command of changing perms {result.stdout.strip()}")


def get_current_user():
    """Get the current user."""
    result = subprocess.run(['whoami'], capture_output=True, text=True)
    current_user = result.stdout.strip()
    print(f"Current user: {current_user}")
    return current_user


def get_current_directory():
    """Get the current working directory."""
    result = subprocess.run(['pwd'], capture_output=True, text=True)
    current_directory = result.stdout.strip()
    print(f"Current directory: {current_directory}")
    return current_directory


def create_dz1_folder(current_directory):
    """Create the dz1 folder."""
    dz1_path = os.path.join(current_directory, 'dz1')
    ensure_permissions()
    subprocess.run(['mkdir', '-p', dz1_path], check=True)
    print(f"Folder '{dz1_path}' has been created.")
    return dz1_path


def create_log_files(dz1_path):
    """Create log files for each day of the current month."""
    today = datetime.now()
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    start_of_month = today.replace(day=1)
    days_in_month = (next_month - start_of_month).days

    file_names = (
        f"{dz1_path}/{(start_of_month + timedelta(days=i)).strftime('%d-%m-%Y')}.log"
        for i in range(days_in_month)
    )

    ensure_permissions()
    for file_name in file_names:
        open(file_name, 'w').close()

    print(f"Files for {days_in_month} days of the month have been created in '{dz1_path}'.")


# def change_owner_to_root_with_password(dz1_path, password):
#     command = ['sudo', '-S', 'chown', '-R', 'root:wheel', dz1_path]
#     process = subprocess.run(command, input=f"{password}\n", text=True, check=True)
#     print("Owner changed to root successfully.")


def delete_random_files(dz1_path, num_files_to_delete=5):
    """Delete a specified number of random files from the dz1 folder."""
    print(f"Deleting {num_files_to_delete} random files...")
    files = [f for f in os.listdir(dz1_path) if os.path.isfile(os.path.join(dz1_path, f))]
    if len(files) < num_files_to_delete:
        print("Not enough files to delete.")
        return

    files_to_delete = random.sample(files, num_files_to_delete)
    for file in files_to_delete:
        file_path = os.path.join(dz1_path, file)
        os.remove(file_path)
        print(f"Deleted file: {file_path}")


def main():
    get_current_user()
    current_directory = get_current_directory()
    dz1_path = create_dz1_folder(current_directory)
    create_log_files(dz1_path)
    # change_owner_to_root_with_password(dz1_path, 'pass')
    delete_random_files(dz1_path)


if __name__ == "__main__":
    main()
