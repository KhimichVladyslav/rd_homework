import subprocess


def copy_file():
    """Copy dz1.py to dz1_run.py using subprocess."""
    source_file = 'dz2_1.py'
    destination_file = 'dz1_run.py'

    subprocess.run(['chmod', '666', source_file], check=True)

    subprocess.run(['cp', source_file, destination_file], check=True)
    print(f"File '{source_file}' copied to '{destination_file}'.")


def prepend_to_file():
    """Prepend text to the beginning of dz1_run.py."""
    text_to_prepend = "# This is a modified version of dz1.py\n"

    with open('dz1_run.py', 'r') as file:
        original_content = file.read()

    with open('dz1_run.py', 'w') as file:
        file.write(text_to_prepend + original_content)
    print(f"Text has been prepended to 'dz1_run.py'.")


# def change_file_permissions():
#     """Change permissions of dz1_run.py as per the requirement."""
#     subprocess.run(['sudo', 'chmod', '700', 'dz1_run.py'], check=True)
#     print("Permissions for 'dz1_run.py' have been set")


def run_file():
    """Run dz1_run.py."""
    subprocess.run(['python3', 'dz1_run.py'], check=True)
    print("File 'dz1_run.py' has been executed.")


def main():
    copy_file()
    prepend_to_file()
    # change_file_permissions()
    run_file()


if __name__ == "__main__":
    main()
