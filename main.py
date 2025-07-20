import os, json, time
from utils import generate_key, encrypt_file, compute_hash
from config import PASSWORD, LEDGER_FILE, STORAGE_FOLDER
from utils import decrypt_file,hash_dict
import json

key = generate_key(PASSWORD)
"""
def save_file(filename: str, content: bytes):
    file_hash = compute_hash(content)
    encrypted = encrypt_file(content, key)
    
    # Save file
    storage_path = os.path.join(STORAGE_FOLDER, file_hash + "_" + filename)
    with open(storage_path, "wb") as f:
        f.write(encrypted)
    
    # Add to ledger
    entry = {
        "filename": filename,
        "hash": file_hash,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, "r") as f:
                ledger = json.load(f)
        except json.JSONDecodeError:
            ledger = []
    else:
        ledger = []

    ledger.append(entry)

    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

    print("✅ File saved and logged:", entry)
"""
def validate_chain():
    if not os.path.exists(LEDGER_FILE):
        print("❌ Ledger not found.")
        return

    with open(LEDGER_FILE, "r") as f:
        try:
            ledger = json.load(f)
        except:
            print("❌ Ledger is corrupted.")
            return

    print("🔎 Validating chain...")

    for i in range(1, len(ledger)):
        prev = ledger[i - 1]
        curr = ledger[i]
        expected = hash_dict(prev)
        if curr['prev_hash'] != expected:
            print(f"❌ Chain broken at entry #{i + 1}: {curr['filename']}")
            print(f"    Expected prev_hash: {expected}")
            print(f"    Found: {curr['prev_hash']}")
            return

    print("✅ Chain is valid! All entries are consistent.")



"""  """
def save_file(filename: str, content: bytes):
    file_hash = compute_hash(content)
    encrypted = encrypt_file(content, key)

    # Save encrypted file
    storage_path = os.path.join(STORAGE_FOLDER, file_hash + "_" + filename)
    with open(storage_path, "wb") as f:
        f.write(encrypted)

    # Load existing ledger
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            try:
                ledger = json.load(f)
            except json.JSONDecodeError:
                ledger = []
    else:
        ledger = []

    # Get previous hash
    prev_hash = hash_dict(ledger[-1]) if ledger else "0"*64

    # Create new entry
    entry = {
        "filename": filename,
        "hash": file_hash,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prev_hash": prev_hash
    }

    # Append and save
    ledger.append(entry)
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

    print("✅ File saved and chained to ledger.")


#
##
####
#####
#file download and verification 
def list_files():
    if not os.path.exists(LEDGER_FILE):
        print("No ledger found.")
        return []
    with open(LEDGER_FILE, "r") as f:
        try:
            ledger = json.load(f)
        except:
            print("Ledger is corrupted.")
            return []
    for i, entry in enumerate(ledger):
        print(f"{i+1}. {entry['filename']}  |  Hash: {entry['hash']}  |  Time: {entry['time']}")
    return ledger

def verify_and_decrypt():
    ledger = list_files()
    if not ledger:
        return
    choice = int(input("Enter the number of the file to verify & decrypt: ")) - 1
    if choice < 0 or choice >= len(ledger):
        print("Invalid choice.")
        return

    entry = ledger[choice]
    fname = entry['filename']
    hash_stored = entry['hash']

    encrypted_path = os.path.join(STORAGE_FOLDER, f"{hash_stored}_{fname}")
    if not os.path.exists(encrypted_path):
        print("❌ File not found.")
        return

    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted = decrypt_file(encrypted_data, key)
    except:
        print("❌ Decryption failed.")
        return

    hash_now = compute_hash(decrypted)
    if hash_now == hash_stored:
        print("✅ Hash match! File is verified.")
        save_path = input("Enter path to save the decrypted file: ").strip()
        with open(save_path, "wb") as f:
            f.write(decrypted)
        print("✅ File decrypted and saved.")
    else:
        print("⚠️ Hash mismatch! File may have been tampered with.")


if __name__ == "__main__":
    while True:
        print("\n1. Upload File")
        print("2. List + Verify + Decrypt File")
        print("3. Validating Ledger chain")
        print("4. Exit")
        choice = input("Enter choice: ").strip()
        if choice == '1':
            fname = input("Enter path of file to upload: ").strip()
            if not os.path.exists(fname):
                print("❌ File doesn't exist.")
                continue
            with open(fname, "rb") as f:
                data = f.read()
            save_file(os.path.basename(fname), data)
        elif choice == '2':
            verify_and_decrypt()
        elif choice == '3':
            validate_chain()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

