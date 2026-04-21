# gcal-invite-push

Automatically invites your work email to every event on your family Google Calendar. Runs every 30 minutes via a Google Apps Script time-based trigger.

---

## How it works

1. The script fetches all upcoming events (next 180 days) from your family calendar.
2. For each event, it checks whether your work email is already a guest.
3. If not, it adds your work email as a guest.
4. A time-based trigger fires this sync every 30 minutes.

---

## Setup

### 1. Find your Family Calendar ID

1. Open [Google Calendar](https://calendar.google.com).
2. Hover over your family calendar in the left sidebar → click the three-dot menu → **Settings and sharing**.
3. Scroll to **Integrate calendar** and copy the **Calendar ID** (looks like `abc123@group.calendar.google.com` or an email address).

### 2. Create a new Apps Script project

1. Go to [script.google.com](https://script.google.com) and click **New project**.
2. Delete the placeholder code in `Code.gs`.

### 3. Add the script files

Copy the contents of `Code.gs` and `appsscript.json` from this repository into your Apps Script project:

- Paste `Code.gs` into the default `Code.gs` file.
- Open **Project Settings** (gear icon) → enable **Show "appsscript.json" manifest file in editor**, then paste the contents of `appsscript.json` into that file.

### 4. Configure your credentials

At the top of `Code.gs`, update the two constants:

```javascript
var FAMILY_CALENDAR_ID = 'your-family-calendar-id@group.calendar.google.com';
var WORK_EMAIL         = 'you@work.com';
```

### 5. Run the setup function

1. In the Apps Script editor, select `setupTrigger` from the function dropdown.
2. Click **Run**.
3. Approve the OAuth permissions when prompted (Calendar access + Triggers).

The trigger is now active. `syncFamilyToWork` will run every 30 minutes automatically.

### 6. Verify

- Select `syncFamilyToWork` and click **Run** once manually to confirm it works.
- Check **View → Logs** (or the **Executions** tab) to see output.

---

## Optional: deploy with clasp

[clasp](https://github.com/google/clasp) lets you manage the script from this repo via the CLI.

```bash
npm install -g @google/clasp
clasp login
```

Replace `YOUR_SCRIPT_ID_HERE` in `.clasp.json` with your script's ID (found in **Project Settings**), then:

```bash
clasp push   # upload local files to Apps Script
clasp pull   # download remote changes
```

---

## Utility functions

| Function | Purpose |
|---|---|
| `syncFamilyToWork()` | Run a sync immediately |
| `setupTrigger()` | Install (or reinstall) the 30-minute trigger |
| `removeTrigger()` | Delete the trigger without re-creating it |

---

## Adjusting the sync window

Change `DAYS_AHEAD` at the top of `Code.gs` to control how far into the future events are synced (default: 180 days).
