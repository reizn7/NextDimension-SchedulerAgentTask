# 🗓️ Smart Scheduler Agent  

A **smart meeting scheduling assistant** that integrates with **Google Calendar** to automatically check availability and schedule meetings for you.  
Powered by `Python`, `Google Calendar API`, and an AI-driven agent, it makes managing meetings seamless and stress-free.  

---

## ✨ Features  
- 🔍 **Check Availability**: Fetches free time slots from your calendar.  
- 🤖 **Smart Agent**: Handles natural language requests like _“schedule a meeting tomorrow at 3 PM”_.  
- 🗂️ **Accurate Date Handling**: Resolves today, tomorrow, or custom dates reliably.  
- 📅 **Easy Scheduling**: Creates Google Calendar events with title, date, and duration.  
- ✅ **Friendly Confirmation**: Confirms scheduled events naturally (without exposing raw links).  
- 🔒 **Secure**: Uses Google Service Accounts to access your calendar safely.  

---

## 🛠️ Tech Stack  
- **Language:** Python 3.10+  
- **APIs:** Google Calendar API  
- **Libraries:**  
  - `google adk agents`
  - `google oauth2` 
  - `pytz`  
  - `dateparser`  

---

##📂 Project Structure
├── google_search_agent
│   │   sechduler_tools.py #for calendar api
│   │   agent.py #agent to schedule using tools


