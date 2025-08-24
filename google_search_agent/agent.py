from google.adk.agents import Agent
from .scheduler_tools import find_available_slots, create_meeting_new, parse_datetime_with_fallback

def check_availability(duration: str = "60 minutes", day: str = "today"):
    """Check calendar availability for a given duration and day.
    Args:
        duration (str): Duration of the meeting in minutes. Default is "60 minutes".
        day (str): Day to check availability. Options are "today", "tomorrow", or a specific date in "YYYY-MM-DD" format. Default is "today".
    Returns:
        dict: A dictionary containing available time slots.
    """
    try:
        duration_minutes = int(duration.split()[0])
    except Exception:
        duration_minutes = 60

    slots = find_available_slots(duration_minutes, day)
    return {"available_slots": slots}


def schedule_meeting(
    duration: str = "60 minutes",
    day: str = "today",
    time: str = "",
    title: str = "New Meeting",
    time_slot: str = ""
):
    """Schedule a meeting in Google Calendar.
    Args:
        duration (str): Duration of the meeting in minutes. Default is "60 minutes".
        day (str): Day to schedule the meeting. Options are "today", "tomorrow", or a specific date in "YYYY-MM-DD" format. Default is "today".
        time (str): Time to schedule the meeting (e.g., "8 am", "14:00"). Optional.
        title (str): Title of the meeting. Default is "New Meeting".
    Returns:
        dict: A dictionary containing details of the scheduled event.
    """
    from datetime import timedelta


    if time:
        day_time_str = f"{day} {time}"
    else:
        day_time_str = day


    start_dt = parse_datetime_with_fallback(day_time_str)
    try:
        duration_minutes = int(duration.split()[0])
    except Exception:
        duration_minutes = 60
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event_link = create_meeting_new(start_dt, end_dt, summary=title)
    return {"event_link": event_link}


root_agent = Agent(
    name="smart_scheduler_agent",
    model="gemini-2.0-flash-exp",
    description="Agent that checks Google Calendar availability and schedules meetings.",
    instruction="""
You are a smart and friendly meeting scheduling assistant.

Your responsibilities:
1. Help the user find suitable time slots by using `check_availability` on their calendar. 
   - Present options clearly and concisely.
   - Make sure to suggest multiple choices when possible.

2. Guide the user in selecting a preferred slot. 
   - Confirm their choice before proceeding.

3. Once the user confirms, use `schedule_meeting` to create the event in their calendar.
   - Include essential details (title, date, time).
   - Ensure the event is scheduled without errors.

4. Provide a warm, natural confirmation message (e.g., “Your meeting has been scheduled for Tuesday at 3 PM.”). 
   - Do not read links aloud. 
   - Instead, return links or metadata inside the JSON response for system use.

General guidelines:
- Keep your responses concise, polite, and user-friendly.
- Ask clarifying questions if details are missing (like meeting title, participants, or duration).
- Always prioritize accuracy when scheduling.

""",
    tools=[check_availability, schedule_meeting],
)