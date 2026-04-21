// ─── Configuration ───────────────────────────────────────────────────────────
// FAMILY_CALENDAR_ID: found in Google Calendar > Settings > [calendar] > Calendar ID
// WORK_EMAIL:         the address to invite to every family event
// DAYS_AHEAD:         how far into the future to sync (default 180 days)
// ─────────────────────────────────────────────────────────────────────────────
var FAMILY_CALENDAR_ID = 'your-family-calendar-id@group.calendar.google.com';
var WORK_EMAIL         = 'you@work.com';
var DAYS_AHEAD         = 180;

// ─── Main sync function ───────────────────────────────────────────────────────
function syncFamilyToWork() {
  var calendar = CalendarApp.getCalendarById(FAMILY_CALENDAR_ID);
  if (!calendar) {
    Logger.log('ERROR: Calendar not found — check FAMILY_CALENDAR_ID: ' + FAMILY_CALENDAR_ID);
    return;
  }

  var now = new Date();
  var end = new Date(now.getTime() + DAYS_AHEAD * 24 * 60 * 60 * 1000);
  var events = calendar.getEvents(now, end);

  Logger.log('Syncing ' + events.length + ' upcoming events to ' + WORK_EMAIL);

  var invited = 0;
  var skipped = 0;
  var errors  = 0;

  for (var i = 0; i < events.length; i++) {
    var event = events[i];
    try {
      if (isAlreadyInvited_(event, WORK_EMAIL)) {
        skipped++;
        continue;
      }
      event.addGuest(WORK_EMAIL);
      invited++;
      Logger.log('Invited: "' + event.getTitle() + '" on ' + event.getStartTime());
    } catch (e) {
      errors++;
      Logger.log('Skipped "' + event.getTitle() + '": ' + e.message);
    }
  }

  Logger.log('Done — invited: ' + invited + ', already present: ' + skipped + ', errors: ' + errors);
}

// ─── Trigger management ───────────────────────────────────────────────────────

/**
 * Run this once manually from the Apps Script editor to install the
 * 30-minute recurring trigger.  Re-running it is safe; it removes any
 * existing syncFamilyToWork triggers first.
 */
function setupTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'syncFamilyToWork') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }

  ScriptApp.newTrigger('syncFamilyToWork')
    .timeBased()
    .everyMinutes(30)
    .create();

  Logger.log('Trigger created: syncFamilyToWork will run every 30 minutes.');
}

/**
 * Removes all syncFamilyToWork triggers without creating a new one.
 */
function removeTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  var removed = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'syncFamilyToWork') {
      ScriptApp.deleteTrigger(triggers[i]);
      removed++;
    }
  }
  Logger.log('Removed ' + removed + ' trigger(s).');
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function isAlreadyInvited_(event, email) {
  var guests = event.getGuestList(true); // true = include calendar owner
  for (var i = 0; i < guests.length; i++) {
    if (guests[i].getEmail() === email) {
      return true;
    }
  }
  return false;
}
