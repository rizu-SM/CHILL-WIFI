# dont-bruteforce-sa7bi

A fun script to list and reveal saved Wi-Fi passwords on your Windows machine. No brute-forcing, just friendly Wi-Fi info!

## Features
- Lists all saved Wi-Fi networks
- Shows their passwords (if available)
- Outputs to a file for easy access

## How It Works
This script uses Windows command-line tools to fetch Wi-Fi profiles and their passwords, then parses and displays them. No hacking, just reading what your system already knows!

## Requirements
- Windows OS
- Python 3.x

## Dependencies
No external Python packages required. Uses only the Python standard library and Windows built-in commands.

## How to Run
1. Download or clone this repository.
2. Open a terminal (PowerShell or CMD) as administrator in the project folder.
3. Run the script:
   ```
   python script.py
   ```


## Usage Note
There is a `passwords.txt` file included by default, but it only contains a sample password (`12356789`).
To check other Wi-Fi passwords, you should open `passwords.txt` and add your own passwords (one per line). The script will use whatever passwords you put in this file.

After running the script, check the output files (e.g., `working_networks.txt`).


