# PNEUMATIC ASSEMBLY GUIDE - Pi #7 VULNERABLE SYSTEM
## STEP-BY-STEP FABRICATION INSTRUCTIONS

**SAFETY FIRST:** This guide covers pneumatic (air) assembly ONLY. Electrical wiring is in a separate document with detailed safety procedures.

**Last Updated:** 2026-02-11
**System:** Pi #7 - Vulnerable Balloon Demo (192.168.50.100)

---

## TOOL & MATERIAL CHECKLIST

### Required Tools:
- [ ] Adjustable wrench (6" or 8")
- [ ] Scissors (for cutting tubing)
- [ ] Ruler or measuring tape
- [ ] Marker (permanent, for labeling stages)
- [ ] Safety glasses (for pressure testing)

### Required Materials (ONE complete system):
- [ ] 7× Brass tees (1/4" NPT Female×Female×Female)
- [ ] 3× Solenoid valves (12V NC, 1/4" NPT)
- [ ] 2× Ball valves (1/4" NPT brass)
- [ ] 1× DataQ pressure sensor (30 PSI, model 2000361-30H)
- [ ] 1× DataQ pressure sensor (15 PSI, model 2000361-15H)
- [ ] 2× NPT reducers (1/4" Female to 1/8" Male)
- [ ] 1× Analog pressure gauge (0-15 PSI, 1/4" NPT)
- [ ] 1× Air pump (HEALiNK 120W, 12V DC)
- [ ] 20× Brass barb fittings (1/4" NPT male to 1/4" barb)
- [ ] 100 ft clear polyurethane tubing (1/4" ID, 3/8" OD)
- [ ] 1 roll Teflon tape (PTFE, white)
- [ ] 6" silicone tubing (for balloon attachment)
- [ ] 10× Wide zip ties (6mm or wider)

---

## ASSEMBLY OVERVIEW - STAGE NUMBERING

```
Stage 0: Air Pump
Stage 1: T-Joint #1 + Ball Valve #1 (emergency bleed A)
Stage 2: T-Joint #2 + 30 PSI Sensor (high-pressure monitoring)
Stage 3: T-Joint #3 + Solenoid #3 (automated upstream vent)
Stage 4: Solenoid #1 (main inlet control)
Stage 5: T-Joint #4 + Ball Valve #2 (emergency bleed B)
Stage 6: T-Joint #5 + 15 PSI Sensor (low-pressure monitoring)
Stage 7: T-Joint #6 + Solenoid #2 (balloon deflate)
Stage 8: T-Joint #7 + Analog Gauge (visual confirmation)
Stage 9: Quick-connect + Balloon attachment
```

**IMPORTANT:** We will build this in ORDER from Stage 0 → Stage 9. Do NOT skip stages.

---

## PHASE 1: TEFLON TAPE APPLICATION

### What is Teflon Tape?
- White PTFE tape that wraps around male NPT threads
- Creates airtight seal when screwed into female threads
- **Direction matters:** Wrap CLOCKWISE when looking at the end of the male thread

### How to Apply Teflon Tape:

1. **Identify male threads:** These are the threads on the OUTSIDE of a fitting
2. **Start 2 threads from the end** (not at the very tip)
3. **Wrap CLOCKWISE** 3-4 times around the threads
4. **Overlap by 50%** on each wrap
5. **Press tape into threads** with your thumb
6. **Tear tape** (don't cut) - it leaves a cleaner edge

### ⚠️ CRITICAL RULE:
**ONLY apply Teflon tape to MALE threads.**
**NEVER apply to female threads (holes).**

---

## PHASE 2: STAGE-BY-STAGE ASSEMBLY

### STAGE 0: AIR PUMP

**Components:**
- 1× Air pump (HEALiNK 120W, 12V DC)
- 1× Brass barb fitting (1/4" NPT male → 1/4" barb)

**Steps:**
1. Locate the air pump outlet port (should be labeled "OUT" or have arrow pointing outward)
2. Apply Teflon tape to brass barb fitting (male NPT end only)
3. Hand-tighten brass barb into pump outlet port
4. Use adjustable wrench to tighten 1.5 turns past hand-tight (do NOT overtighten)
5. **Mark this fitting with marker:** Write "STAGE 0 OUT"

**Result:** Pump now has barb fitting ready for tubing connection.

---

### STAGE 1: T-JOINT #1 + BALL VALVE #1

**Components:**
- 1× Brass tee (F×F×F)
- 1× Ball valve (1/4" NPT)
- 2× Brass barb fittings
- 12" clear tubing (cut from 100 ft roll)
- 4" clear tubing (for ball valve tap)

**Steps:**

1. **Prepare T-Joint #1:**
   - Identify the 3 openings: 2 in-line (main flow) + 1 perpendicular (POST/tail)
   - Apply Teflon tape to 2× brass barb fittings (male NPT ends)
   - Screw barbs into the 2 IN-LINE openings (hand-tight + 1.5 turns with wrench)
   - Mark one barb "INLET" and the other "OUTLET"

2. **Attach Ball Valve #1 to POST:**
   - Apply Teflon tape to ball valve male threads
   - Screw ball valve into the PERPENDICULAR opening (POST) of T-Joint #1
   - Tighten with wrench (1.5 turns past hand-tight)
   - **Verify:** Ball valve handle can turn 90° (quarter-turn)
   - **Mark with marker:** "EMERGENCY BLEED A"

3. **Connect to Stage 0:**
   - Cut 12" of clear tubing
   - Push one end onto Stage 0 barb (pump outlet) - push HARD until it bottoms out
   - Push other end onto T-Joint #1 "INLET" barb
   - **Tug test:** Pull on tubing - it should NOT come off

4. **Optional Vent Tube on Ball Valve:**
   - Cut 4" of clear tubing
   - Push onto ball valve outlet
   - This will direct vented air downward (away from your face during testing)

**Result:** Air flows from Pump → Tee #1. Ball valve is closed (handle perpendicular to flow).

---

### STAGE 2: T-JOINT #2 + 30 PSI SENSOR

**Components:**
- 1× Brass tee (F×F×F)
- 1× DataQ sensor (30 PSI, model 2000361-30H)
- 1× NPT reducer (1/4" F → 1/8" M)
- 2× Brass barb fittings
- 6" clear tubing (main flow)
- 6" clear tubing (sensor tap)

**Steps:**

1. **Prepare T-Joint #2:**
   - Apply Teflon tape to 2× brass barb fittings
   - Screw barbs into 2 IN-LINE openings of tee
   - Mark one "INLET" and other "OUTLET"

2. **Prepare Sensor Connection:**
   - Apply Teflon tape to NPT reducer (1/8" male end only)
   - Screw reducer into T-Joint #2 POST opening (perpendicular port)
   - Apply Teflon tape to DataQ sensor threads (1/8-27 NPT male)
   - Screw sensor into reducer (hand-tight only - sensors are delicate!)
   - **IMPORTANT:** Sensor pigtail cable should point DOWNWARD (not under stress)

3. **Connect to Stage 1:**
   - Cut 6" of clear tubing
   - Connect T-Joint #1 "OUTLET" barb → T-Joint #2 "INLET" barb
   - **Mark sensor with tape:** "30 PSI - HIGH RANGE - CH0"

**Result:** Air flows through Tee #2, sensor taps pressure via POST.

---

### STAGE 3: T-JOINT #3 + SOLENOID #3 (HIGH-PRESSURE RELIEF)

**Components:**
- 1× Brass tee (F×F×F)
- 1× Solenoid valve #3 (12V NC)
- 2× Brass barb fittings (for tee in-line ports)
- 2× Brass barb fittings (for solenoid ports)
- 6" clear tubing (main flow)
- 4" clear tubing (solenoid vent)

**Steps:**

1. **Prepare T-Joint #3:**
   - Apply Teflon tape to 2× brass barb fittings
   - Screw into tee's IN-LINE openings
   - Mark "INLET" and "OUTLET"

2. **Prepare Solenoid #3:**
   - **IMPORTANT:** Solenoid has arrow showing flow direction - note this!
   - Apply Teflon tape to 2× brass barb fittings
   - Screw barbs into solenoid's 2 ports (female NPT)
   - Solenoid inlet barb goes to tee POST
   - Solenoid outlet barb will vent to atmosphere

3. **Connect Solenoid to T-Joint POST:**
   - Apply Teflon tape to brass barb fitting
   - Screw into T-Joint #3 POST
   - Cut 4" tubing, connect POST barb → Solenoid inlet barb
   - Cut 4" tubing for solenoid outlet (this will vent air)
   - **Mark solenoid:** "SOL #3 - HIGH-PRESSURE RELIEF - RELAY #4"

4. **Connect to Stage 2:**
   - Cut 6" tubing
   - Connect T-Joint #2 "OUTLET" → T-Joint #3 "INLET"

**Result:** Automated upstream vent ready (will open if 30 PSI sensor detects >25 PSI).

---

### STAGE 4: SOLENOID #1 (MAIN INLET CONTROL)

**Components:**
- 1× Solenoid valve #1 (12V NC)
- 2× Brass barb fittings
- 6" clear tubing

**Steps:**

1. **Prepare Solenoid #1:**
   - Note flow direction arrow on solenoid body
   - Apply Teflon tape to 2× brass barb fittings
   - Screw barbs into solenoid's 2 female NPT ports
   - **Mark solenoid:** "SOL #1 - MAIN INLET - RELAY #2"

2. **Connect to Stage 3:**
   - Cut 6" tubing
   - Connect T-Joint #3 "OUTLET" → Solenoid #1 inlet barb
   - **Verify:** Arrow on solenoid points AWAY from tee (toward downstream)

**Result:** Main pressure control valve installed.

---

### STAGE 5: T-JOINT #4 + BALL VALVE #2

**Components:**
- 1× Brass tee (F×F×F)
- 1× Ball valve #2
- 2× Brass barb fittings (for tee in-line)
- 6" clear tubing (main flow)
- 4" clear tubing (ball valve vent)

**Steps:**

1. **Prepare T-Joint #4:**
   - Apply Teflon tape to 2× brass barb fittings
   - Screw into IN-LINE openings
   - Mark "INLET" and "OUTLET"

2. **Attach Ball Valve #2 to POST:**
   - Apply Teflon tape to ball valve threads
   - Screw into T-Joint #4 POST
   - **Mark:** "EMERGENCY BLEED B"

3. **Connect to Stage 4:**
   - Cut 6" tubing
   - Connect Solenoid #1 outlet → T-Joint #4 "INLET"
   - Cut 4" tubing for ball valve outlet (vent tube)

**Result:** Second emergency manual bleed installed downstream of main solenoid.

---

### STAGE 6: T-JOINT #5 + 15 PSI SENSOR

**Components:**
- 1× Brass tee (F×F×F)
- 1× DataQ sensor (15 PSI, model 2000361-15H)
- 1× NPT reducer (1/4" F → 1/8" M)
- 2× Brass barb fittings
- 6" clear tubing (main flow)

**Steps:**

1. **Prepare T-Joint #5:**
   - Apply Teflon tape to 2× brass barb fittings
   - Screw into IN-LINE openings
   - Mark "INLET" and "OUTLET"

2. **Install Sensor:**
   - Apply Teflon tape to NPT reducer (1/8" M end)
   - Screw reducer into T-Joint #5 POST
   - Apply Teflon tape to sensor threads
   - Screw 15 PSI sensor into reducer (hand-tight only)
   - **Mark sensor:** "15 PSI - LOW RANGE - CH1 - PRIMARY CONTROL"

3. **Connect to Stage 5:**
   - Cut 6" tubing
   - Connect T-Joint #4 "OUTLET" → T-Joint #5 "INLET"

**Result:** Primary balloon pressure sensor installed.

---

### STAGE 7: T-JOINT #6 + SOLENOID #2 (BALLOON DEFLATE)

**Components:**
- 1× Brass tee (F×F×F)
- 1× Solenoid valve #2 (12V NC)
- 2× Brass barb fittings (tee in-line)
- 2× Brass barb fittings (solenoid)
- 6" clear tubing (main flow)
- 4" clear tubing (solenoid vent)

**Steps:**

1. **Prepare T-Joint #6:**
   - Apply Teflon tape to 2× brass barb fittings
   - Screw into IN-LINE openings
   - Mark "INLET" and "OUTLET"

2. **Prepare Solenoid #2:**
   - Apply Teflon tape to 2× brass barb fittings
   - Screw into solenoid's 2 ports
   - **Mark:** "SOL #2 - BALLOON DEFLATE - RELAY #3"

3. **Connect to T-Joint POST:**
   - Apply Teflon tape to brass barb
   - Screw into T-Joint #6 POST
   - Cut 4" tubing, connect POST → Solenoid #2 inlet
   - Cut 4" tubing for solenoid outlet (vents to atmosphere)

4. **Connect to Stage 6:**
   - Cut 6" tubing
   - Connect T-Joint #5 "OUTLET" → T-Joint #6 "INLET"

**Result:** Automated balloon deflation valve installed.

---

### STAGE 8: T-JOINT #7 + ANALOG GAUGE

**Components:**
- 1× Brass tee (F×F×F)
- 1× Analog pressure gauge (0-15 PSI, 1/4" NPT)
- 2× Brass barb fittings
- 6" clear tubing (main flow)

**Steps:**

1. **Prepare T-Joint #7:**
   - Apply Teflon tape to 2× brass barb fittings
   - Screw into IN-LINE openings
   - Mark "INLET" and "OUTLET"

2. **Install Gauge:**
   - Apply Teflon tape to gauge threads (1/4" NPT male)
   - Screw gauge into T-Joint #7 POST
   - **Orient gauge face** toward front (where you can see it)
   - Tighten with wrench (1 turn past hand-tight)

3. **Connect to Stage 7:**
   - Cut 6" tubing
   - Connect T-Joint #6 "OUTLET" → T-Joint #7 "INLET"

**Result:** Visual pressure gauge installed for real-time monitoring.

---

### STAGE 9: QUICK-CONNECT + BALLOON ATTACHMENT

**Components:**
- 1× Brass barb fitting (1/4" NPT M → 1/4" barb)
- 6" silicone tubing (softer/more flexible than clear poly)
- 3× Wide zip ties (6mm or wider)
- 1× 18" punch balloon

**Steps:**

1. **Install Final Barb:**
   - Apply Teflon tape to brass barb fitting
   - Screw into T-Joint #7 "OUTLET"
   - This is the final connection point

2. **Attach Silicone Tubing:**
   - Cut 6" of silicone tubing (NOT the clear poly - use softer silicone)
   - Push silicone tubing onto barb (push hard until bottomed out)
   - This creates the "quick-connect" - balloons push over the other end

3. **Balloon Attachment (when ready to test):**
   - Stretch balloon neck over free end of silicone tubing
   - Push balloon neck down 2-3 inches onto tubing
   - Wrap first wide zip tie around balloon neck (1/2" from end)
   - Tighten zip tie GENTLY - just enough to grip (don't cut balloon)
   - Wrap second zip tie 1" down from first
   - Wrap third zip tie 1.5" down from second
   - **DO NOT overtighten** - latex tears easily

4. **Balloon Removal (after demo):**
   - Cut zip ties with scissors
   - Pull balloon off silicone tubing
   - Push new balloon on, repeat zip tie process

**Result:** Complete pneumatic assembly from pump to balloon!

---

## PHASE 3: LEAK TESTING (NO POWER YET)

⚠️ **SAFETY GLASSES REQUIRED FOR THIS PHASE**

### Test 1: Visual Inspection
- [ ] Check every fitting for Teflon tape visible in threads
- [ ] Verify all barbs have tubing pushed fully on
- [ ] Confirm no tubing is kinked or bent sharply
- [ ] Verify ball valves are CLOSED (handle perpendicular to flow)

### Test 2: Low-Pressure Test (Manual Pump)
**DO NOT use electric pump yet!**

1. Close both ball valves (handles perpendicular)
2. Manually blow air into Stage 0 (pump inlet) OR use bicycle pump if available
3. Watch analog gauge - should rise to ~1 PSI from lung power
4. Listen for hissing sounds (indicates leak)
5. If leak found:
   - Mark location with marker
   - Depressurize (open ball valve)
   - Tighten fitting 1/4 turn
   - Repeat test

### Test 3: Final Assembly Check
- [ ] All 7 tees installed with correct orientation
- [ ] 3 solenoids marked with relay numbers
- [ ] 2 ball valves marked as emergency bleeds
- [ ] 2 sensors marked with PSI range and channel
- [ ] 1 gauge visible and readable
- [ ] Balloon attachment point ready

---

## PHASE 4: SAFETY BRIEFING BEFORE ELECTRICAL CONNECTION

🛑 **STOP - DO NOT PROCEED TO ELECTRICAL WIRING YET**

Before connecting power:
1. ✅ Complete pneumatic assembly (this document)
2. ✅ Pass leak testing (above)
3. ✅ Read ELECTRICAL_WIRING_GUIDE_VULNERABLE.md (next document)
4. ✅ Have advisor or EE student review your wiring plan
5. ✅ Test with multimeter BEFORE applying power

**Next Document:** `ELECTRICAL_WIRING_GUIDE_VULNERABLE.md`

---

## TROUBLESHOOTING

### Problem: Fitting won't tighten
- **Cause:** Cross-threaded
- **Fix:** Unscrew completely, align threads, start hand-tight first

### Problem: Tubing won't stay on barb
- **Cause:** Barb too small or tubing too large
- **Fix:** Verify 1/4" ID tubing on 1/4" barb. Push HARD until it bottoms out.

### Problem: Air leaking at fitting
- **Cause:** Insufficient Teflon tape or under-tightened
- **Fix:** Add more tape (5-6 wraps) or tighten 1/4 turn more

### Problem: Sensor threads stripping
- **Cause:** Over-tightening delicate sensor
- **Fix:** Sensors are HAND-TIGHT ONLY. Do not use wrench on sensor body.

---

## PARTS REMAINING AFTER ASSEMBLY

After building ONE complete system, you should have LEFT OVER:
- Brass tees: 0 (used all 7)
- Solenoids: 1 (need 3, have 4 total for both systems)
- Ball valves: 0 (used both)
- Sensors: 2 (15 PSI and 30 PSI for second system)
- Barb fittings: ~14 remaining (started with 34)
- Tubing: ~92 ft remaining (started with 100 ft)

**For Second System (Pi #6 Secure):** You'll need to order 7 more tees, 2 more ball valves, 1 more solenoid.

---

**Document Version:** 1.0
**Created:** 2026-02-11
**Author:** Claude + David (Team 41)
**Review Status:** ⚠️ PENDING ADVISOR REVIEW BEFORE ELECTRICAL WIRING
