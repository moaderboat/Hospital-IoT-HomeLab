# this is a script to encrypt and save patient temp every 5 seconds.

import os, time, sys, base64
from datetime import datetime, timezone
from sense_hat import SenseHat

# encryption Fernet symmetric
try:
	from cryptography.fernet import Fernet
except ImportError:
	print("Missing 'cryptography' package. install with python3 -m pip install --user cryptography")
	sys.exit(1)

KEY_PATH = "/home/username/.keys/patient_zero.key"
LOG_DIR = "/home/username/.logs/encrypted_logs"
BASE_NAME = "patient_zero_temperature_C"

def get_or_create_key(path = KEY_PATH):
	if os.path.exists(path):
		with open(path, "rb") as f:
			key = f.read().strip()
	else:
		key = Fernet.generate_key()
		os.makedirs(os.path.dirname(path), exist_ok = True)
		# Restrict permission so only your user can read it
		with open(path, "wb") as f:
			f.write(key)
		os.chmod(path, 0o600)
	return key

def next_logfile(log_dir, base):
	os.makedirs(log_dir, exist_ok=True)
	n = 1
	while True:
		candidate = os.path.join(log_dir, f"{base}_{n}.txt")
		if not os.path.exists(candidate):
			return candidate
		n += 1

def encrypt_line(fernet, text: str) -> str:
	# return base64 text (fernet token)
	# so we can store it in a .txt cleanly
	token = fernet.encrypt(text.encode("utf-8"))
	return token.decode("utf-8")

def main():
	key = get_or_create_key()
	fernet = Fernet(key)
	sense = SenseHat()

	log_path = next_logfile(LOG_DIR, BASE_NAME)
	os.chmod(LOG_DIR, 0o700)
	print(f"Logging file...")
	
	# Open output in append mode: create if missing
	with open(log_path, "w", buffering = 1) as out_f:
		# making logs only readable by me
		os.chmod(log_path, 0o600)
		try:
			print("Logging encrypted temperature every 30s. Ctrl+C to stop.")
			while True:
				
				# ISO 8601 UTC timestamp for clarity
				ts = datetime.now(timezone.utc).isoformat(timespec = "seconds")
				temp_c = round(sense.get_temperature(), 2)

				# plain record will be encrypted
				record = f"{ts}, {temp_c} C"
				
				# encrypt and write one token per line
				enc_line = encrypt_line(fernet, record)
				out_f.write(enc_line + "\n")
				out_f.flush()
				os.fsync(out_f.fileno())
				time.sleep(30)
		except KeyboardInterrupt:
			print("\nStopped.")
		except Exception as e:
			print(f"\nError: {e}")
			sys.exit(1)

if __name__ == "__main__":
	main()
