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

## 3. Create the 4 Specialist Agents
In Switch Console, navigate to **Your Agents → Create Agent** for each of the four roles:

### Agent 1: `forge-lead`
- **Name:** `forge-lead`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Agent Instructions:** Copy and paste the full contents of:
  `switch\agents\forge_lead.md`

### Agent 2: `evidence-scout`
- **Name:** `evidence-scout`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Agent Instructions:** Copy and paste the full contents of:
  `switch\agents\evidence_scout.md`

### Agent 3: `red-team`
- **Name:** `red-team`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Agent Instructions:** Copy and paste the full contents of:
  `switch\agents\red_team.md`

### Agent 4: `experiment-designer`
- **Name:** `experiment-designer`
- **Host:** Select **This computer**
- **Working Directory:** `C:\Projects\Switch`
- **Agent Provider:** Select **Codex**
- **Agent Instructions:** Copy and paste the full contents of:
  `switch\agents\experiment_designer.md`

---

## 4. Create the Room
1. In Switch Console, navigate to **Your Rooms → Create room**.
2. **Room name:** `ideaforge-demo`
3. **Add Agents:** Add `forge-lead`, `evidence-scout`, `red-team`, and `experiment-designer`.
4. **Room Instructions:** Copy and paste the full contents of:
  `switch\ROOM_INSTRUCTIONS.md`
5. Click **Create Room**.

---

## 5. Verify the Room in Mattermost
1. Open Mattermost in your browser.
2. Join the channel `ideaforge-demo`.
3. Test communication by mentioning:
   ```text
   @forge-lead Introduce yourself and state the IDEAForge room rules.
   ```
4. Confirm `forge-lead` replies with its role and adherence to room rules.
5. Ingest and attach the demo source pack from `examples\demo_case\sources\`.
6. Proceed through the demo script in `docs\DEMO_SCRIPT.md`.
