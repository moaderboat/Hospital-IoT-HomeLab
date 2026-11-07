# Pressure Chamber - Additional Shopping List

**Date:** 2026-02-05
**Purpose:** BMP388 sensor pressure chambers for balloon demo

---

## ITEMS TO PURCHASE

### 🏪 LOCAL PICKUP (Today/This Week)

**Walmart / Target / Grocery Store:**
- [ ] **Ball 4oz Quilted Crystal Jelly Jars** (12-pack with metal lids)
  - Need: 2 jars (buy 12-pack for spares)
  - Cost: ~$10-15
  - Link: https://www.walmart.com/ip/Ball-Regular-Mouth-4oz-Quilted-Pint-Mason-Jars-12-Count/17203435

**Home Depot / Lowe's:**
- [ ] **Clear Silicone Sealant** (100% silicone, waterproof)
  - Recommended: GE Silicone II or DAP Aquarium Sealant
  - Need: 1 tube
  - Cost: ~$5-8
  - Note: Must be 100% silicone (cures airtight)

---

### 📦 AMAZON ORDER (2-3 day shipping)

- [ ] **Female-to-Female DuPont Jumper Wires Kit** (30cm length, 120pcs)
  - Product: Breadboard jumper wire kit with F-F wires
  - Need: 8 wires total (4 per sensor), kit includes 40 F-F
  - Cost: ~$7-8
  - Links:
    - Option 1: https://www.amazon.com/SIM-NAT-Breadboard-Arduino-Raspberry/dp/B06XRV92ZB (30cm)
    - Option 2: https://www.amazon.com/Kuman-Breadboard-Arduino-Raspberry-Multicolored/dp/B01BV3Z342 (20cm - also works)

---

## TOTAL ADDITIONAL COST: ~$22-31

---

## TOOLS NEEDED (Already Have)

From existing tools/BOM:
- ✅ Drill with bits (5/16" and 3/16")
- ✅ M2.5 brass standoffs (from Electronics-Salon kit - arrived 2026-02-05)
- ✅ Hot glue gun (alternative to silicone for wire hole)
- ✅ Teflon tape (from BOM - arrived 2026-02-03)

---

## CONSTRUCTION CHECKLIST

### Per Pressure Chamber (need 2 total):

**Lid Preparation:**
- [ ] Drill 5/16" hole in metal lid (for 1/4" NPT barb fitting)
- [ ] Drill 3/16" hole in metal lid (for 4× I²C wires)
- [ ] Install brass barb fitting through air hole
- [ ] Apply silicone sealant around barb fitting threads
- [ ] Let cure 24 hours

**Sensor Mounting:**
- [ ] Glue 2× M2.5 standoffs to bottom of glass jar (use epoxy or super glue)
- [ ] Wait for glue to cure
- [ ] Mount BMP388 sensor on standoffs

**Wiring:**
- [ ] Cut 4× female-to-female jumper wires to desired length (~30cm recommended)
- [ ] Connect to BMP388 sensor:
  - Red wire → VIN (3.3V)
  - Black wire → GND
  - Yellow wire → SCL (I²C clock)
  - Blue wire → SDA (I²C data)
- [ ] Thread wires through lid hole
- [ ] Seal wire hole with silicone sealant or hot glue
- [ ] Let cure

**Assembly:**
- [ ] Screw metal lid onto jar (rubber gasket seals automatically)
- [ ] Connect air tube from brass tee to barb fitting on lid
- [ ] Connect I²C wires to Raspberry Pi GPIO:
  - VIN → Pin 1 (3.3V Power)
  - GND → Pin 6 (Ground)
  - SCL → Pin 5 (GPIO 3)
  - SDA → Pin 3 (GPIO 2)

**Testing:**
- [ ] Power on Raspberry Pi
- [ ] Run `i2cdetect -y 1` to verify sensor detected at 0x77
- [ ] Read pressure values with Python test script
- [ ] Verify air-tight seal (gently blow into air tube, pressure should register)

---

## PRIORITY

**HIGH PRIORITY:**
These items are needed before hardware assembly can begin.

**Timeline:**
- Local pickup: Today or this weekend
- Amazon order: Place ASAP for delivery in 2-3 days
- Construction: Can begin once all items arrive + relay HATs arrive

**Current Status:**
- ✅ Design finalized
- ⏳ Waiting for additional materials
- ⏳ Waiting for Sequent 8-RELAYS HAT (main blocker)

---

## NOTES

**Why Mason Jars:**
- Glass is 100% airtight (no porosity)
- Metal lid with rubber gasket = proven pressure seal
- Designed for canning = holds vacuum/pressure
- Clear glass = can see sensor during demo
- Cheap, available locally, professional appearance

**Wire Length:**
- 30cm (12") recommended for mounting flexibility
- 20cm (8") also works if pressure chamber is close to Pi
- I²C works reliably up to 1 meter at standard speed (100kHz)

**Alternative to Silicone:**
- Marine epoxy (JB Weld) also works
- Hot glue is less reliable but acceptable for low pressure (0-5 PSI)
- Must be fully cured before pressure testing
