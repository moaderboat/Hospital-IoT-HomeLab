"""
Decrypts the encrypted log

Defaults:
	key -> /home/username/.keys/patient_zero.key
	log -> /home/username/.logs/patient_zero_temperature_C.txt
	out -> (optional) plaintext output file path
"""

import os
import sys
import argparse
from cryptography.fernet import Fernet

KEY_PATH = "/home/username/.keys/patient_zero.key"
LOG_DIR = "/home/username/.logs/encrypted_logs"
BASE_NAME = "patient_zero_temperature_C"
DECRYPT_DIR = "/home/username/.logs/decrypted_logs"
OUTPUT_SUFFIX = "_decrypted.txt"


def die(msg):
	print(f"{msg}", file = sys.stderr); sys.exit(1)

def main():
	p = argparse.ArgumentParser(description = "Decrypting specified temperature log file")
	p.add_argument("number", type = int, help = "Log Number, e.g. 6 --> *_6.txt")
	args = p.parse_args()

	enc_path = os.path.join(LOG_DIR, f"{BASE_NAME}_{args.number}.txt")
	key_path = KEY_PATH
	out_path = os.path.join(DECRYPT_DIR, f"{BASE_NAME}_{args.number}{OUTPUT_SUFFIX}")

	# delete when done testing
	# print(f"Key: {key_path}")
	# print(f"Encrypted: {enc_path}")
	# print(f"Decrypted: {out_path}")

	# checking if paths exist

	if not os.path.exists(key_path): die(f"Key Not Found: {key_path}")
	if not os.path.exists(enc_path): die(f"Encrypted Log Not Found: {enc_path}")
	if os.path.exists(out_path): die(f"File has already been decrypted: {out_path}")
	
	try:
		os.makedirs(DECRYPT_DIR, exist_ok = True)
		try: os.chmod(DECRYPT_DIR, 0o700)
		except PermissionError: pass
	except Exception as e:
		die(f"Cannot create decrypted_logs dir: {e}")
		
	# try and load the key
	try:
		key = open(key_path, "rb").read().strip()
		fernet = Fernet(key)
	except Exception as e:
		sys.exit(f"FAILED TO LOAD KEY: {e}")
	
	bad = 0; total = 0
	try:
		with open(enc_path, "r", encoding = "utf-8") as fin, \
			open(out_path, "w", encoding = "utf-8") as fout:
			print("Decrypting...")
			for line in fin:
				token = line.strip()
				if not token: continue
				total += 1
				try:
					plain = fernet.decrypt(token.encode("utf-8")).decode("utf-8")
					fout.write(plain + "\n")
				except Exception as e:
					bad += 1
					print(f"[bad line] {e}", file = sys.stderr)
			fout.flush()
			os.fsync(fout.fileno())
		try: os.chmod(out_path, 0o600)
		except PermissionError: pass
	except Exception as e:
		die(f"IO ERROR DURING DECRYPT: {e}")
	print(f"DONE!")
	if bad:
		print(f"{bad}/{total} LINES FAILED TO DECRYPT.", file = sys.stderr)
			
		
				
if __name__ == "__main__":
	main()
		
