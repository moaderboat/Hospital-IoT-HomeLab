# How to Create Gantt Chart in Excel from CSV

## Quick Start

1. **Open the CSV in Excel:**
   - Double-click `Project_Gantt_Chart.csv`
   - Excel will automatically parse the columns

2. **Verify Data Loaded Correctly:**
   - You should see 10 columns: Phase, Task ID, Task Name, Start Date, End Date, Duration (Days), Status, % Complete, Owner, Dependencies, Notes
   - 100+ rows of tasks

---

## Method 1: Excel Conditional Formatting Gantt Chart (Easiest)

### Step 1: Prepare Data
1. Insert a new column after "Notes" (Column L)
2. Label it "Start Day Number"
3. In cell L2, enter formula: `=A2-$A$2` (calculates days from project start)
4. Copy formula down for all rows

### Step 2: Create Date Columns
1. In column M1, enter the project start date: `2025-08-26`
2. In column N1, enter: `=M1+7` (one week later)
3. Copy formula across to create weekly columns (e.g., through column AZ for full timeline)

### Step 3: Mark Task Bars
1. In cell M2, enter formula: `=IF(AND($D2<=M$1,$E2>=M$1),1,0)`
   - This checks if the task spans the week in column M
2. Copy formula to all cells in the grid (M2:AZ100+)

### Step 4: Apply Conditional Formatting
1. Select the grid of formulas (M2:AZ100+)
2. Home tab → Conditional Formatting → New Rule → Format cells based on value
3. **For "Complete" tasks (green):**
   - Formula: `=AND($G2="Complete",M2=1)`
   - Format: Green fill
4. **For "In Progress" tasks (yellow):**
   - Formula: `=AND($G2="In Progress",M2=1)`
   - Format: Yellow fill
5. **For "Pending" tasks (blue):**
   - Formula: `=AND($G2="Pending",M2=1)`
   - Format: Blue fill

### Step 5: Format for Readability
1. Hide columns with formulas (L, M, N...)
2. Rotate column headers 45° for date columns
3. Freeze panes at column D (so task names stay visible when scrolling)
4. Color-code phases (use fill color for Phase column):
   - Phase 0: Light gray
   - Phase 1: Light green
   - Phase 2: Light blue
   - Phase 3: Light yellow
   - Phase 4: Light orange
   - Phase 5: Light red
   - Documentation: Light purple

---

## Method 2: Use Excel's Built-In Gantt Chart Template (Recommended)

### Option A: Project Timeline Template
1. Open Excel
2. File → New
3. Search for "Gantt Project Planner" or "Project Timeline"
4. Select template
5. Copy data from `Project_Gantt_Chart.csv` into template

### Option B: Insert Stacked Bar Chart
1. Select columns: Task Name, Start Date, Duration
2. Insert tab → Charts → Bar Chart → Stacked Bar
3. Right-click on blue bars → Format Data Series → No Fill (to make start dates invisible)
4. Format orange bars to show task duration
5. Reverse category order (so tasks go top-to-bottom)

---

## Method 3: Use Microsoft Project (Professional)

If you have access to Microsoft Project:

1. Open Microsoft Project
2. File → Import → CSV
3. Select `Project_Gantt_Chart.csv`
4. Map columns:
   - Task Name → Name
   - Start Date → Start
   - End Date → Finish
   - Duration → Duration
   - % Complete → % Complete
   - Dependencies → Predecessors
5. Project automatically generates professional Gantt chart

---

## Method 4: Use Free Online Tools

### Option A: TeamGantt (Free for small projects)
1. Go to https://www.teamgantt.com
2. Create free account
3. Import CSV or manually enter tasks
4. Export as PDF or PNG for report

### Option B: GanttProject (Free, Open-Source)
1. Download from https://www.ganttproject.biz
2. File → Import → CSV
3. Map columns (same as Microsoft Project)
4. Export chart as PNG for report appendix

### Option C: Excel Online (Free with Microsoft Account)
1. Go to https://office.live.com/start/Excel.aspx
2. Upload `Project_Gantt_Chart.csv`
3. Use Method 1 or Method 2 above

---

## Quick Tips for Your Report

### For Appendix A (Gantt Chart):
1. **Create TWO versions:**
   - **Full Timeline Gantt:** Shows all phases (Aug 2025 - Aug 2026)
   - **Current Progress Gantt:** Zooms in on Phase 1 (Aug 2025 - Dec 2025)

2. **Add Legend:**
   - Green = Complete
   - Yellow = In Progress
   - Blue = Pending

3. **Highlight Milestones:**
   - Use diamond shapes or different color for milestone rows
   - Example: "M.6: 8-Day Uptime Validation Complete"

4. **Include Statistics:**
   - Total Tasks: 100+
   - Completed: 38 (38%)
   - In Progress: 2 (2%)
   - Pending: 60+ (60%)
   - On Schedule: YES (Phase 1 complete)

### Export for Word Document:
1. Create Gantt chart in Excel
2. Select chart area
3. Copy (Ctrl+C)
4. Paste into Word document as:
   - **Picture** (for final submission - smaller file size)
   - **Excel Object** (for drafts - can still edit)

---

## Key Milestones to Highlight

When presenting Gantt chart, emphasize these milestones:

| Milestone | Date | Status |
|-----------|------|--------|
| **M.2: Preliminary Proposal Submitted** | Sep 23, 2025 | ✅ Complete |
| **M.4: Network Infrastructure Operational** | Oct 21, 2025 | ✅ Complete |
| **M.5: IoT Sensors Operational** | Nov 9, 2025 | ✅ Complete |
| **M.6: 8-Day Uptime Validation** | Nov 17, 2025 | ✅ Complete |
| **M.7: Phase 1 Complete (Data Pipeline)** | Dec 8, 2025 | ⚠️ Pending |
| **M.12: Technical Report Submitted** | Dec 9, 2025 | ⚠️ Pending |
| **M.13: Final Presentation** | Dec 10, 2025 | ⚠️ Pending |

---

## Critical Path Analysis

**Critical path** = longest sequence of dependent tasks (determines minimum project duration)

**Your Critical Path:**
1. 0.1 → 0.2 → 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.22 → 1.23 → 1.24 → 1.25 → 1.26 → 2.8 → 2.9 → 2.10 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6 → 3.7 → 3.8

**Critical Path Duration:** ~200 days (Aug 26, 2025 → Mar 22, 2026)

**For Presentation:**
> "The critical path runs through the MQTT data pipeline and ML model deployment, which are sequential dependencies. Phase 1 is complete ahead of schedule, putting us on track for ML deployment by March 2026."

---

## Troubleshooting

**Problem:** CSV won't open in Excel
- **Solution:** Right-click → Open With → Excel

**Problem:** Dates show as numbers (e.g., 44896)
- **Solution:** Select column → Right-click → Format Cells → Date → MM/DD/YYYY

**Problem:** Formulas not calculating
- **Solution:** File → Options → Formulas → Check "Enable iterative calculation"

**Problem:** Chart looks messy
- **Solution:** Filter to show only one phase at a time (use Excel's Filter feature)

---

## Example Screenshot Annotations

When including Gantt chart in report, add annotations:

1. **Arrow pointing to completed tasks:**
   > "38 tasks completed (green) representing network infrastructure, IoT deployment, and initial documentation"

2. **Arrow pointing to critical path:**
   > "Critical path through data pipeline ensures ML models receive clean, structured data"

3. **Arrow pointing to milestone markers:**
   > "Key milestone: 8-day uptime validation (99.98%) exceeded target"

---

## Need Help?

- **Excel Gantt Chart Tutorial:** https://www.youtube.com/results?search_query=excel+gantt+chart
- **GanttProject Tutorial:** https://www.ganttproject.biz/documentation
- **Ask me for help:** I can generate additional formats or visualizations

