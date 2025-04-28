# honeypot
 This script will monitor specific files (honeypots). 


This script will monitor specific files (honeypots). If they don't exist, it will create them. It will then store their initial cryptographic hashes. On subsequent runs, it will compare the current hashes with the stored ones and set a variable changes_detected to True if any file has been modified.

Here's an overview of the steps involved:

Configuration: Define the list of honeypot files and the file to store the hashes.
Hashing Function: Create a function to calculate the SHA-256 hash of a file reliably.
Initialization/Verification:
Load previously saved hashes if the storage file exists.
Iterate through the configured honeypot files.
If a file doesn't exist, create it with some default content.
Calculate the hash of each file.
Compare the current hash with the stored hash (if one exists).
If it's the first time seeing the file or if the hash differs from the stored one (which shouldn't happen during initialization but is good practice), store the initial hash.
Change Detection: Compare the current hash with the stored initial hash. If any differ, flag that changes have occurred.
Saving Hashes: Save the initial hashes back to the storage file.


Explanation:

Configuration:

HONEYPOT_FILES: Modify this list to include the full paths to the files you want to monitor. Using os.path.join(os.getcwd(), 'filename') creates the file in the same directory as the script, which is useful for testing. For real-world use, specify absolute paths like '/var/log/honeypot.log' or 'C:\\Users\\Admin\\Documents\\decoy.doc'.
HASH_STORAGE_FILE: This file will store the known "good" hashes in JSON format. Keep this file secure, as modifying it would defeat the purpose of the check.
DEFAULT_HONEYPOT_CONTENT: Basic content written into honeypot files when they are first created. Including the timestamp helps make each initial file slightly different.
changes_detected: The boolean variable you requested. It starts as False and is set to True if any hash mismatch is found.
calculate_sha256(filepath):

Takes a file path as input.
Opens the file in binary read mode ("rb").
Reads the file in chunks (4096 bytes) to handle potentially large files without using too much memory.
Updates the SHA-256 hash object with each chunk.
Returns the final hash as a hexadecimal string.
Includes basic error handling for FileNotFoundError and other exceptions.
load_hashes(storage_file):

Checks if the HASH_STORAGE_FILE exists.
If it exists, it tries to load the JSON data into a Python dictionary.
Handles potential errors during file reading or JSON parsing.
Returns an empty dictionary if the file doesn't exist or if there's an error.
save_hashes(storage_file, hashes):

Takes the storage file path and the dictionary of hashes to save.
Opens the file in write mode ('w'), overwriting the previous content.
Uses json.dump() to write the dictionary to the file in a readable JSON format (indent=4).
Includes basic error handling.
Main Logic:

Loads any previously stored hashes.
Loops through each filepath in the HONEYPOT_FILES list.
File Creation: If a file doesn't exist, it creates it, calculates its hash, and adds the filepath and hash to the initial_hashes_to_save dictionary.
Hash Comparison: If the file does exist, it calculates the current_hash. It then looks up the stored_initial_hash for that file from the stored_hashes loaded at the beginning.
If a stored_initial_hash exists, it compares it to the current_hash. If they differ, it prints a warning and sets changes_detected = True.
If no stored_initial_hash exists (e.g., the script is run for the first time after the file was manually created, or the storage file was lost), it stores the current_hash as the initial hash in initial_hashes_to_save.
After checking all files, it saves the potentially updated initial_hashes_to_save back to the storage file. This ensures newly created files have their initial hashes recorded for future checks.
Finally, it prints a summary message indicating whether changes were detected and shows the final value of the changes_detected variable.
How to Implement and Run Daily:

Save the code: Save the script as a Python file (e.g., honeypot_checker.py).
Modify Configuration: Update the HONEYPOT_FILES list with the actual paths you want to monitor. Decide where to store honeypot_hashes.json.
Run Initially: Run the script once (python honeypot_checker.py) to create the honeypot files (if they don't exist) and the initial honeypot_hashes.json file.
Schedule Daily Execution: You need an external scheduler to run this script automatically every day.
Linux/macOS: Use cron.
Open the crontab editor: crontab -e
Add a line like this to run the script daily at, for example, 2:00 AM:
Bash

0 2 * * * /usr/bin/python3 /path/to/your/honeypot_checker.py >> /path/to/your/honeypot_log.log 2>&1
(Adjust the python path and script path. >> ... 2>&1 redirects output and errors to a log file).
Windows: Use Task Scheduler.
Open Task Scheduler.
Create a new Basic Task.
Set the trigger to "Daily" and choose a time.
Set the action to "Start a program".
Program/script: C:\Python3x\python.exe (or your Python path)
Add arguments: C:\path\to\your\honeypot_checker.py (your script path)
Start in (optional): C:\path\to\your\ (the directory containing the script)
Now, the script will run daily, check your specified files, and the changes_detected variable within the script's execution context will be set to True if any modifications occur compared to their initial state. Remember to add actual alerting or logging mechanisms based on the changes_detected variable's value if you need notifications.
