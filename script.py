import subprocess  # Lets Python run system commands (netsh, ping, etc.)
import time       # For delays/waiting
import os         # File operations (delete temp files)
import sys        # System-specific parameters
import requests   # HTTP library for internet checks
import tempfile   # Creates temporary files (WiFi profiles)
import ctypes     # Windows API calls (admin check)
import socket     # Network/low-level operations (DNS checks)

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_available_networks():
    """Get list of available WiFi networks"""
    networks = []
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        lines = result.stdout.split('\n')
        for line in lines:
            if 'SSID' in line and 'BSSID' not in line and ':' in line:
                ssid = line.split(':', 1)[1].strip()
                if ssid and ssid not in networks:
                    networks.append(ssid)
        return networks
    except:
        return []

def get_current_connection():
    """Get current connected WiFi network"""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        lines = result.stdout.split('\n')
        for line in lines:
            if 'SSID' in line and 'BSSID' not in line and ':' in line:
                return line.split(':', 1)[1].strip()
        return None
    except:
        return None

def check_internet_simple():
    """Simple internet check using ping and HTTP"""
    # Try ping first (fastest)
    try:
        result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                              capture_output=True, text=True, timeout=2)
        if 'Reply from' in result.stdout:
            return True
    except:
        pass
    
    # Try DNS resolution
    try:
        socket.gethostbyname('google.com')
        return True
    except:
        pass
    
    # Try HTTP request
    try:
        response = requests.get('http://www.google.com', timeout=5)
        return response.status_code == 200
    except:
        return False

def connect_to_wifi(ssid, password):
    """Connect to WiFi network"""
    try:
        # Delete old profile
        subprocess.run(['netsh', 'wlan', 'delete', 'profile', f'name={ssid}'], 
                      capture_output=True, text=True, shell=True)
        time.sleep(1)
        
        # Create profile XML
        profile_xml = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
            f.write(profile_xml)
            temp_file = f.name
        
        # Add profile
        subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={temp_file}'], 
                      capture_output=True, text=True, shell=True)
        
        # Connect
        result = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'], 
                               capture_output=True, text=True, shell=True)
        
        # Clean up
        os.unlink(temp_file)
        
        return True
        
    except:
        return False

def disconnect_wifi():
    """Disconnect from WiFi"""
    try:
        subprocess.run(['netsh', 'wlan', 'disconnect'], shell=True)
        time.sleep(2)
        return True
    except:
        return False

def wait_for_connection(ssid, timeout=30):
    """Wait for connection to establish"""
    for i in range(timeout):
        current = get_current_connection()
        if current == ssid:
            return True
        time.sleep(1)
    return False

def test_network_with_password(ssid, password, attempt_num):
    """Test a specific network with a password"""
    print(f"\n{'='*60}")
    print(f"TEST #{attempt_num}: {ssid}")
    print(f"Password: {'*' * len(password)}")
    print(f"{'='*60}")
    
    # Disconnect first
    disconnect_wifi()
    time.sleep(3)
    
    # Try to connect
    print(f"Connecting to {ssid}...")
    if not connect_to_wifi(ssid, password):
        print("❌ Connection failed")
        return False
    
    # Wait for connection
    print("Waiting for connection (10 seconds)...")
    time.sleep(10)
    
    # Check if connected
    current = get_current_connection()
    if current != ssid:
        print(f"❌ Not connected. Current: {current}")
        return False
    
    print(f"✓ Connected to {ssid}")
    
    # Give network time to stabilize
    print("Waiting 5 seconds for network...")
    time.sleep(5)
    
    # Check internet
    print("Checking internet access...")
    
    # Try multiple times
    for check_num in range(1, 4):
        print(f"  Internet check {check_num}/3...")
        if check_internet_simple():
            print(f"\n{'#'*70}")
            print(f"🎉 SUCCESS! INTERNET FOUND!")
            print(f"Network: {ssid}")
            print(f"Password: {password}")
            print(f"{'#'*70}")
            return True
        else:
            if check_num < 3:
                wait_time = check_num * 5
                print(f"  No internet yet. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
    
    print("⚠ Connected but no internet access")
    return False

def scan_and_connect_all():
    """Main function: Scan all networks and try passwords"""
    print("="*70)
    print("WIFI NETWORK SCANNER + PASSWORD TESTER")
    print("Finds working WiFi networks with internet access")
    print("="*70)
    
    # Check admin
    if not is_admin():
        print("❌ Run as Administrator! (Right-click -> Run as Administrator)")
        input("Press Enter to exit...")
        return
    
    # Load passwords
    try:
        with open("passwords.txt", "r") as f:
            passwords = [line.strip() for line in f if line.strip()]
        
        if not passwords:
            print("❌ No passwords in passwords.txt")
            print("Create passwords.txt with one password per line")
            input("Press Enter to exit...")
            return
        
        print(f"✓ Loaded {len(passwords)} password(s)")
    except:
        print("❌ Error reading passwords.txt")
        input("Press Enter to exit...")
        return
    
    attempt_counter = 1
    working_networks = []
    
    while True:
        print(f"\n{'='*70}")
        print(f"SCAN CYCLE #{len(working_networks) + 1}")
        print(f"{'='*70}")
        
        # Scan for networks
        print("\n📡 Scanning for WiFi networks...")
        networks = get_available_networks()
        
        if not networks:
            print("No networks found. Waiting 10 seconds...")
            time.sleep(10)
            continue
        
        print(f"Found {len(networks)} networks:")
        for i, net in enumerate(networks, 1):
            print(f"  {i}. {net}")
        
        # Skip already working networks
        networks_to_try = [net for net in networks if net not in working_networks]
        
        if not networks_to_try:
            print("\nAll available networks have been tested.")
            print(f"Found {len(working_networks)} working network(s).")
            break
        
        # Try each network
        for ssid in networks_to_try:
            print(f"\n➡ Testing network: {ssid}")
            
            # Try each password
            for password in passwords:
                if test_network_with_password(ssid, password, attempt_counter):
                    # Success! Save to file
                    working_networks.append(ssid)
                    
                    with open("working_networks.txt", "a") as f:
                        f.write(f"{time.ctime()}\n")
                        f.write(f"SSID: {ssid}\n")
                        f.write(f"Password: {password}\n")
                        f.write("-"*40 + "\n")
                    
                    print(f"\n✅ Added {ssid} to working networks list!")
                    
                    # Ask user if they want to continue
                    print("\nOptions:")
                    print("1. Continue scanning for MORE networks")
                    print("2. Stop here and use current network")
                    print("3. Exit")
                    
                    choice = input("\nEnter choice (1-3): ").strip()
                    
                    if choice == "2":
                        print(f"\nStopping. Using network: {ssid}")
                        print("You're now connected to the internet!")
                        input("Press Enter to exit...")
                        return
                    elif choice == "3":
                        print("Exiting...")
                        return
                    else:
                        print("Continuing to scan for more networks...")
                        break  # Break out of password loop, continue with next network
                
                attempt_counter += 1
            
            # If we found a working network in this iteration, break to rescan
            if ssid in working_networks:
                break
        
        # Wait before next scan
        print(f"\n⏳ Waiting 15 seconds before next scan...")
        time.sleep(15)
    
    # Summary
    print(f"\n{'='*70}")
    print("SCAN COMPLETE")
    print(f"{'='*70}")
    
    if working_networks:
        print(f"Found {len(working_networks)} working network(s):")
        for network in working_networks:
            print(f"  ✓ {network}")
        print("\nDetails saved in: working_networks.txt")
    else:
        print("No working networks found.")
        print("Try adding more passwords to passwords.txt")
    
    input("\nPress Enter to exit...")

def main():
    print("="*70)
    print("AUTO WIFI CONNECTOR")
    print("="*70)
    print("Scans for WiFi networks and tests passwords until internet is found")
    print("="*70)
    
    # Check admin
    if not is_admin():
        print("\n⚠ WARNING: This script requires Administrator privileges!")
        print("\nTo run as Administrator:")
        print("1. Right-click on Command Prompt or PowerShell")
        print("2. Select 'Run as administrator'")
        print("3. Navigate to script folder")
        print("4. Run: python script.py")
        input("\nPress Enter to exit...")
        return
    
    # Check password file
    if not os.path.exists("passwords.txt"):
        print("\n⚠ passwords.txt not found!")
        print("Creating sample file...")
        with open("passwords.txt", "w") as f:
            f.write("password123\n")
            f.write("admin\n")
            f.write("12345678\n")
            f.write("wifipassword\n")
        print("Created passwords.txt with sample passwords.")
        print("Edit it with your actual passwords.")
        input("Press Enter after editing passwords.txt...")
    
    # Start scanning
    print("\nStarting WiFi scanner...")
    print("Press Ctrl+C to stop at any time\n")
    
    try:
        scan_and_connect_all()
    except KeyboardInterrupt:
        print("\n\n⚠ Scan stopped by user")
        current = get_current_connection()
        if current:
            print(f"Currently connected to: {current}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")