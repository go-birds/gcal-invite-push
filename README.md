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

### 1. Create a new Apps Script project

Go to [script.google.com](https://script.google.com) and click **New project**.

### 2. Copy the source files

Copy the contents of these files into your Apps Script project:

| Local file | Apps Script file |
|---|---|
| `Code.gs` | `Code.gs` (replace the placeholder) |
| `config.gs.example` → rename to `config.gs` | `config.gs` (new file) |
| `appsscript.json` | enable manifest in Project Settings, then paste |

### 3. Configure your secrets

In your local copy of the repo (not committed to git):

```bash
cp config.gs.example config.gs
```

Edit `config.gs` and fill in your values:

```javascript
FAMILY_CALENDAR_ID: 'your-family-calendar-id@group.calendar.google.com',
WORK_EMAIL:         'you@work.com'
```

**Finding your Family Calendar ID:** Google Calendar → hover over the calendar → three-dot menu → **Settings and sharing** → scroll to **Integrate calendar** → copy the Calendar ID.

### 4. Run configure() to save secrets

In the Apps Script editor, select **`configure`** from the function dropdown and click **Run**. Approve the OAuth prompt.

This writes your secrets into Script Properties (Google's server-side secret store). `config.gs` is never needed again at runtime — the secrets now live in the project, not in any file.

### 5. Install the trigger

Select **`setupTrigger`** and click **Run**. This installs a 30-minute recurring trigger for `syncFamilyToWork`.

### 6. Verify

Select **`syncFamilyToWork`** and run it once manually. Check **Executions** (left sidebar) or **View → Logs** to confirm events were processed.

---

## Optional: deploy with clasp

[clasp](https://github.com/google/clasp) lets you push changes from this repo to Apps Script via the CLI.

```bash
npm install -g @google/clasp
clasp login
```

Replace `YOUR_SCRIPT_ID_HERE` in `.clasp.json` with the ID from **Project Settings**, then:

```bash
clasp push   # upload local files → Apps Script
clasp pull   # download remote changes → local
```

`config.gs` is gitignored so it won't be committed to GitHub, but `clasp push` will still upload it to your Apps Script project (which is what you want — it's how `configure()` gets deployed).

---

## Utility functions

| Function | Purpose |
|---|---|
| `configure()` | Save secrets to Script Properties (run once) |
| `syncFamilyToWork()` | Run a sync immediately |
| `setupTrigger()` | Install (or reinstall) the 30-minute trigger |
| `removeTrigger()` | Delete the trigger without re-creating it |

---

## Security model

| What | Where it lives | In git? |
|---|---|---|
| Calendar ID & work email | Script Properties (Google servers) | No |
| `config.gs` (sets the above) | Local only, gitignored | No |
| `config.gs.example` | Repo (placeholder values only) | Yes |
| All other source files | Repo | Yes |
