from django.contrib.admin.models import LogEntry as OldLogEntry
from django.contrib.admin.models import LogEntryManager

ADDITION = 1
CHANGE = 2
DELETION = 3

class LogEntry(OldLogEntry):
    pass

