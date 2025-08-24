import os
from datetime import datetime, timedelta
import pytz
import dateparser
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID") or "primary"
LOCAL_TZ = pytz.timezone("Asia/Kolkata")


def get_calendar_service():
    if not SERVICE_ACCOUNT_FILE:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON not set.")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)



def parse_datetime_with_fallback(text: str) -> datetime:
    """
    Parse natural language date/time into IST datetime.
    If parsing fails, fallback to 'today 10:00 IST'.
    """
    dt = dateparser.parse(
        text,
        settings={
            "PREFER_DATES_FROM": "future",
            "TIMEZONE": str(LOCAL_TZ),
            "RETURN_AS_TIMEZONE_AWARE": True,
        },
    )
    if not dt:
        dt = datetime.now(LOCAL_TZ).replace(hour=10, minute=0, second=0, microsecond=0)
    return dt.astimezone(LOCAL_TZ)


def create_meeting_new(start_time: datetime, end_time: datetime, summary: str = "Meeting") -> dict:
    """
    Create a Google Calendar event.
    Returns event details including link.
    """
    service = get_calendar_service()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time.astimezone(pytz.UTC).isoformat(),
            "timeZone": str(LOCAL_TZ),
        },
        "end": {
            "dateTime": end_time.astimezone(pytz.UTC).isoformat(),
            "timeZone": str(LOCAL_TZ),
        },
        "reminders": {"useDefault": True},
    }

    created_event = (
        service.events()
        .insert(calendarId=CALENDAR_ID, body=event)
        .execute()
    )

    return {
        "id": created_event.get("id"),
        "summary": created_event.get("summary"),
        "start": created_event["start"].get("dateTime"),
        "end": created_event["end"].get("dateTime"),
        "htmlLink": created_event.get("htmlLink"),
    }


def find_available_slots(duration_minutes: int = 60, day: str = "today") -> list:
    """
    Check calendar for available slots in given day.
    """
    service = get_calendar_service()
    if day.lower() == "today":
        base_date = datetime.now(LOCAL_TZ)
    elif day.lower() == "tomorrow":
        base_date = datetime.now(LOCAL_TZ) + timedelta(days=1)
    else:
        base_date = parse_datetime_with_fallback(day)

    day_start = base_date.replace(hour=9, minute=0, second=0, microsecond=0)
    day_end = base_date.replace(hour=18, minute=0, second=0, microsecond=0)

    events_result = service.freebusy().query(
        body={
            "timeMin": day_start.isoformat(),
            "timeMax": day_end.isoformat(),
            "timeZone": str(LOCAL_TZ),
            "items": [{"id": CALENDAR_ID}],
        }
    ).execute()

    busy_times = events_result["calendars"][CALENDAR_ID]["busy"]

    free_slots = []
    cursor = day_start
    for busy in busy_times:
        busy_start = dateparser.parse(busy["start"]).astimezone(LOCAL_TZ)
        busy_end = dateparser.parse(busy["end"]).astimezone(LOCAL_TZ)

        if cursor + timedelta(minutes=duration_minutes) <= busy_start:
            free_slots.append(
                {
                    "start": cursor.isoformat(),
                    "end": (cursor + timedelta(minutes=duration_minutes)).isoformat(),
                }
            )
        cursor = max(cursor, busy_end)

    while cursor + timedelta(minutes=duration_minutes) <= day_end:
        free_slots.append(
            {
                "start": cursor.isoformat(),
                "end": (cursor + timedelta(minutes=duration_minutes)).isoformat(),
            }
        )
        cursor += timedelta(minutes=duration_minutes)

    return free_slots


def list_events(max_results: int = 10) -> list:
    """
    List upcoming events.
    """
    service = get_calendar_service()

    now = datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return [
        {
            "id": e.get("id"),
            "summary": e.get("summary"),
            "start": e["start"].get("dateTime", e["start"].get("date")),
            "end": e["end"].get("dateTime", e["end"].get("date")),
        }
        for e in events
    ]
