var DAYS_AHEAD = 180;

// ─── Main sync function ───────────────────────────────────────────────────────
function syncFamilyToWork() {
  var config = getConfig_();
  var calendar = CalendarApp.getCalendarById(config.familyCalendarId);
  if (!calendar) {
    Logger.log('ERROR: Calendar not found — check FAMILY_CALENDAR_ID in Script Properties.');
    return;
  }

  var now = new Date();
  var end = new Date(now.getTime() + DAYS_AHEAD * 24 * 60 * 60 * 1000);
  var events = calendar.getEvents(now, end);

  Logger.log('Syncing ' + events.length + ' upcoming events to ' + config.workEmail);

  var invited = 0;
  var skipped = 0;
  var errors  = 0;

  for (var i = 0; i < events.length; i++) {
    var event = events[i];
    try {
      if (isAlreadyInvited_(event, config.workEmail)) {
        skipped++;
        continue;
      }
      event.addGuest(config.workEmail);
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

function getConfig_() {
  var props = PropertiesService.getScriptProperties();
  var familyCalendarId = props.getProperty('FAMILY_CALENDAR_ID');
  var workEmail        = props.getProperty('WORK_EMAIL');
  if (!familyCalendarId || !workEmail) {
    throw new Error('Missing configuration. Run configure() to set FAMILY_CALENDAR_ID and WORK_EMAIL.');
  }
  return { familyCalendarId: familyCalendarId, workEmail: workEmail };
}

function isAlreadyInvited_(event, email) {
  var guests = event.getGuestList(true); // true = include calendar owner
  for (var i = 0; i < guests.length; i++) {
    if (guests[i].getEmail() === email) {
      return true;
    }
  }
  return false;
}
