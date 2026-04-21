# gcal-invite-push

Automatically invites your work email to every event on your family Google Calendar. Runs every 30 minutes via a Google Apps Script time-based trigger.

---

## How it works

1. The script fetches all upcoming events (next 180 days) from your family calendar.
2. For each event it checks whether your work email is already a guest.
3. If not, it adds your work email as a guest.
4. A time-based trigger fires this sync every 30 minutes.

Secrets (calendar ID and work email) are stored as **Script Properties** inside your Apps Script project — never in source files or this repository.

---

## Setup

### 1. Find your Family Calendar ID

1. Open [Google Calendar](https://calendar.google.com).
2. Hover over your family calendar in the left sidebar → click the **three-dot menu** → **Settings and sharing**.
3. Scroll down to **Integrate calendar** and copy the **Calendar ID** (looks like `abc123@group.calendar.google.com`).

### 2. Create a new Apps Script project

Go to [script.google.com](https://script.google.com) and click **New project**. Give it a name (e.g. "Calendar Sync").

### 3. Add Code.gs

Click on `Code.gs` in the left sidebar. Replace all existing content with the contents of `Code.gs` from this repo. Save with **Ctrl+S**.

### 4. Add config.gs

1. Click the **+** button next to "Files" → **Script**.
2. Name it `config` (just `config` — the editor automatically appends `.gs`, so typing `config.gs` would produce `config.gs.gs`).
3. Paste in the contents of `config.gs.example` from this repo.
4. Fill in your own values:

```javascript
FAMILY_CALENDAR_ID: 'your-family-calendar-id@group.calendar.google.com',
WORK_EMAIL:         'you@work.com'
```

Save with **Ctrl+S**.

### 5. Update appsscript.json

1. Click the **gear icon** (Project Settings) in the left sidebar.
2. Check **"Show appsscript.json manifest file in editor"**.
3. Go back to the Editor (`< >` icon), click `appsscript.json` in the file list.
4. Replace its contents with the contents of `appsscript.json` from this repo. Save.

### 6. Run configure()

1. Click `config.gs` in the file list so it's the active file.
2. In the toolbar, click the function dropdown (next to the ▶ Run button) and select **`configure`**.
3. Click **▶ Run**.
4. Approve the OAuth permissions when prompted.

This saves your calendar ID and work email as Script Properties on Google's servers. They are never stored in any file.

### 7. Install the trigger

1. In the function dropdown select **`setupTrigger`**.
2. Click **▶ Run**.

This installs a 30-minute recurring trigger. Re-running `setupTrigger` at any time is safe — it removes the old trigger before creating a new one.

### 8. Verify

1. Select **`syncFamilyToWork`** from the function dropdown and click **▶ Run**.
2. Click **Execution log** in the toolbar to see output. You should see something like:

```
Syncing 12 upcoming events to you@work.com
Invited: "Family dinner" on Sat Apr 25 2026 ...
Done — invited: 3, already present: 9, errors: 0
```

The script is now live. Check past runs anytime under the **Executions** tab (clock icon in the left sidebar).

---

## Files in this repo

| File | Purpose |
|---|---|
| `Code.gs` | Main sync logic and trigger management |
| `config.gs.example` | Template — copy to `config.gs` and fill in your values |
| `appsscript.json` | Apps Script manifest (OAuth scopes, runtime) |
| `.clasp.json` | Config template for optional clasp CLI deployment |

---

## Utility functions

| Function | Purpose |
|---|---|
| `configure()` | Save secrets to Script Properties (run once) |
| `syncFamilyToWork()` | Run a sync immediately |
| `setupTrigger()` | Install (or reinstall) the 30-minute trigger |
| `removeTrigger()` | Delete the trigger without re-creating it |

---

## Adjusting the sync window

Change `DAYS_AHEAD` at the top of `Code.gs` to control how far into the future events are synced (default: 180 days).

---

## Optional: deploy with clasp

[clasp](https://github.com/google/clasp) lets you manage the script from this repo via the CLI instead of copy-pasting files manually.

```bash
npm install -g @google/clasp
clasp login
```

Replace `YOUR_SCRIPT_ID_HERE` in `.clasp.json` with your script's ID (found in **Project Settings**), then:

```bash
clasp push   # upload local files → Apps Script
clasp pull   # download remote changes → local
```

`config.gs` is gitignored so it will never be committed to GitHub, but `clasp push` will still upload it to your Apps Script project (which is intentional — it's how `configure()` gets deployed).

---

## Security model

| What | Where it lives | In git? |
|---|---|---|
| Calendar ID & work email | Script Properties (Google's servers) | No |
| `config.gs` (sets the above) | Local only, gitignored | No |
| `config.gs.example` | Repo (placeholder values only) | Yes |
| All other source files | Repo | Yes |
