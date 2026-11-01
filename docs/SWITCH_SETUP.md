# Switch Console & Mattermost Setup Guide

This guide details how to configure the multi-agent studio in **Switch Console** and **Mattermost** for IDEAForge.

---

## 1. Prerequisites
- **Switch Console:** Downloaded and installed (Windows / macOS / Linux).
- **Docker:** Installed and running (required for Switch local server & bundled Mattermost).
- **Codex CLI:** Installed and authenticated (`codex login`).
- **Python:** Python 3.11+ installed in `C:\Projects\Switch`.

---

## 2. Server Startup & Mattermost Access
1. Open **Switch Console**.
2. Go to **Settings → Agent providers**.
   - Verify **Codex** shows status **Signed in**.
   - If not signed in, run `codex login` in PowerShell, then click **Recheck**.
3. In the sidebar, select **Add a server → Run a server on this computer**.
4. Click **Start**. Wait for Docker containers to download and report **Running locally**.
5. On the server home page, locate **Messaging apps → Mattermost**.
6. Click the menu (`...`) on the Mattermost row and select **Sign-in details...**.
7. Click **Open in Mattermost** and complete the sign-in with the provided credentials.

---

## 3. Option A: One-Click Template Deployment (Recommended)
You can deploy the entire IDEAForge studio in one step using the checked-in template:
1. In Switch Console, click **Templates → Import Template** (or drag and drop `ideaforge.template.yaml`).
2. Verify template parameters:
   - `provider`: `codex`
   - `bridge`: `mattermost`
3. Click **Deploy Template**.
4. Switch automatically creates:
   - All 4 agents (`forge-lead`, `evidence-scout`, `red-team`, `experiment-designer`)
   - Pre-configured addressing policies (`anyone` for public scouts/critics, `owner-agents` for lead/planner)
   - The collaboration room `ideaforge-demo` with full room rules
   - An automated kickoff welcome message in the room

---

## 4. Option B: Manual Agent & Room Creation (Step-by-Step)
If you prefer creating each component manually in the Console:

### Create the 4 Specialist Agents
In Switch Console, navigate to **Your Agents → Create Agent** for each of the four roles:

### Agent 1: `forge-lead`
- **Name:** `forge-lead`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Addressing:** Select **Owner & Owner's Agents** (`owner-agents`)
- **Agent Instructions:** Copy and paste the full contents of: `switch\agents\forge_lead.md`

### Agent 2: `evidence-scout`
- **Name:** `evidence-scout`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Addressing:** Select **Anyone** (`anyone`)
- **Agent Instructions:** Copy and paste the full contents of: `switch\agents\evidence_scout.md`

### Agent 3: `red-team`
- **Name:** `red-team`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Addressing:** Select **Anyone** (`anyone`)
- **Agent Instructions:** Copy and paste the full contents of: `switch\agents\red_team.md`

### Agent 4: `experiment-designer`
- **Name:** `experiment-designer`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Addressing:** Select **Owner & Owner's Agents** (`owner-agents`)
- **Agent Instructions:** Copy and paste the full contents of: `switch\agents\experiment_designer.md`

---

## 5. Room Isolation for Blind Review (Advanced Multi-Room Setup)
To eliminate anchoring bias between agents:
1. Create a second private room in Console named `ideaforge-blind-review`.
2. Add only **`@red-team`** and your user account (omit `@evidence-scout`).
3. In this room, `@red-team` evaluates the raw problem brief and reference sources in complete isolation from the scout's findings.
4. `@forge-lead` bridges the independent critique back into the primary room `ideaforge-demo` next to `@evidence-scout`'s report for unbiased reconciliation.

---

## 6. Create the Collaboration Room
1. In Switch Console, navigate to **Your Rooms → Create room**.
2. **Room name:** `ideaforge-demo`
3. **Add Agents:** Add `forge-lead`, `evidence-scout`, `red-team`, and `experiment-designer`.
4. **Room Instructions:** Copy and paste the full contents of:
  `switch\ROOM_INSTRUCTIONS.md`
5. Click **Create Room**.

---

## 7. Verify the Room in Mattermost
1. Open Mattermost in your browser.
2. Join the channel `ideaforge-demo`.
3. Test communication by mentioning:
   ```text
   @forge-lead Introduce yourself and state the IDEAForge room rules.
   ```
4. Confirm `forge-lead` replies with its role and adherence to room rules.
5. Ingest and attach the demo source pack from `examples\demo_case\sources\`.
6. Proceed through the demo script in `docs\DEMO_SCRIPT.md`.
