import os
import hashlib
import json
import datetime

# --- Configuration ---
# List of files to monitor (use absolute paths for reliability)
# Example: HONEYPOT_FILES = ['/path/to/your/honeypot1.txt', '/path/to/sensitive/config.ini.backup']
HONEYPOT_FILES = [
    os.path.join(os.getcwd(), 'honeypot_file_1.txt'), # Creates file in the script's directory
    os.path.join(os.getcwd(), 'decoy_config.ini')     # Creates another file
]

# File to store the initial hashes (JSON format)
HASH_STORAGE_FILE = os.path.join(os.getcwd(), 'honeypot_hashes.json')

# Default content for newly created honeypot files
DEFAULT_HONEYPOT_CONTENT = "This is a honeypot file. Do not modify or delete.\n" + str(datetime.datetime.now())

# Variable to track changes
changes_detected = False

# --- Helper Functions ---

def calculate_sha256(filepath):
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read the file in chunks to handle large files efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Warning: File not found during hash calculation: {filepath}")
        return None
    except Exception as e:
        print(f"Error calculating hash for {filepath}: {e}")
        return None

def load_hashes(storage_file):
    """Loads hashes from the storage file."""
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Hash storage file '{storage_file}' is corrupted. Starting fresh.")
            return {}
        except Exception as e:
            print(f"Error loading hashes from {storage_file}: {e}")
            return {} # Return empty dict on error
    else:
        return {} # Return empty dict if file doesn't exist

def save_hashes(storage_file, hashes):
    """Saves hashes to the storage file."""
    try:
        with open(storage_file, 'w') as f:
            json.dump(hashes, f, indent=4)
    except Exception as e:
        print(f"Error saving hashes to {storage_file}: {e}")

# --- Main Logic ---

print("Starting honeypot check...")

# 1. Load stored hashes
# These are the hashes recorded when the script *first* saw the file
# or the last time it was initialized.
stored_hashes = load_hashes(HASH_STORAGE_FILE)
initial_hashes_to_save = stored_hashes.copy() # Work with a copy

# 2. Iterate through specified honeypot files
for filepath in HONEYPOT_FILES:
    print(f"\nChecking file: {filepath}")

    # 2a. Check if file exists, create if not
    if not os.path.exists(filepath):
        print(f"File not found. Creating honeypot file: {filepath}")
        try:
            with open(filepath, 'w') as f:
                f.write(DEFAULT_HONEYPOT_CONTENT)
            print("File created successfully.")
            # Since it's newly created, calculate its hash and store it as the initial hash
            current_hash = calculate_sha256(filepath)
            if current_hash:
                print(f"Initial hash for new file: {current_hash}")
                initial_hashes_to_save[filepath] = current_hash
                # A newly created file doesn't count as a *change* from a previous state
        except Exception as e:
            print(f"Error creating file {filepath}: {e}")
            continue # Skip to the next file if creation fails

    else:
        # 2b. File exists, calculate its current hash
        print("File found. Calculating current hash...")
        current_hash = calculate_sha256(filepath)

        if not current_hash:
            print("Could not calculate current hash. Skipping checks for this file.")
            continue

        print(f"Current hash: {current_hash}")

        # 2c. Check against stored hash
        stored_initial_hash = stored_hashes.get(filepath)

        if stored_initial_hash:
            print(f"Stored hash:  {stored_initial_hash}")
            if current_hash != stored_initial_hash:
                print(f"!!! CHANGE DETECTED !!! Hash mismatch for file: {filepath}")
                changes_detected = True
                # Optional: Update the stored hash to the new one if you want to track
                # the *last known* state instead of the *initial* state.
                # For true honeypot behavior (detecting any change from original),
                # DO NOT update the initial_hashes_to_save here.
            else:
                print("Hashes match. No changes detected for this file.")
        else:
            # File exists but wasn't in storage - treat this as the initial state
            print(f"No stored hash found for existing file. Storing current hash as initial: {current_hash}")
            initial_hashes_to_save[filepath] = current_hash


# 3. Save the initial hashes (only updates if new files were found/created)
save_hashes(HASH_STORAGE_FILE, initial_hashes_to_save)

# 4. Final Result
print("\n--- Honeypot Check Summary ---")
if changes_detected:
    print("Result: Changes WERE detected in one or more honeypot files.")
else:
    print("Result: No changes detected in any honeypot files.")

# The 'changes_detected' variable holds the final state (True or False)
print(f"Value of 'changes_detected': {changes_detected}")
print("-----------------------------")


# --- How to use the changes_detected variable ---
# You can now use this boolean variable to trigger other actions, e.g.:
# if changes_detected:
#     send_alert_email()
#     log_warning_message()
#     trigger_further_investigation_script()
