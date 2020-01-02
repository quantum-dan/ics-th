"""
Written by Daniel Philippus beginning Jan 2, 2020.

This program parses the "Student Detail Schedule" text (copied from the web browser)
in the Colorado School of Mines Trailhead system and converts it to an ics file suitable
for import into digital calendars.

Dependencies: ics (pip install ics)
"""

"""
Format:

Course Name - Course Number - Section Associated Term: Semester Year
CRN:    XXXXX
Status:     **Registration Type** on Month Day, Year
Grade Mode:     Mode
Credits:        X.XXX
Level:  Level
Campus:         Main Campus
Scheduled Meeting Times Type    Time    Days    Where   Date Range  Schedule Type Instructors
Class   XX:XX am - XX:XX pm     MTWRF   Building Name Number    Month Day, Year - Month Day, Year   Lecture Instructor Name (P)E-mail

Course Name ...

Relevant information is in the first and last rows.  First row, split on " - " and take the first two; title event as "Course Number Course Name" (e.g. "CEEN 312 SOIL MECHANICS").

For the last row, split on tabs.  Time is the second entry, days the third, location the fourth, and date range the fifth.  Month is 3 letters, e.g. Jan 07, 2020.

Entries will be separated by "\n\n".
"""

from ics import Calendar, Event
from ics.parse import ContentLine

class Course(object):
    # Convenience class to hold course data
    def __init__(self, name, number, starttime, stoptime, days, location, startdate, enddate):
        self.name = name
        self.number = number
        self.starttime = starttime
        self.stoptime = stoptime
        self.days = days
        self.location = location
        self.startdate = startdate
        self.enddate = enddate
    def as_event(self):
        # Take a course object and turn it into an ics Event object
        e = Event()
        e.name = self.number + " " + self.name
        e.begin = make_date(self.startdate) + " " + make_time(self.starttime)
        e.end = make_date(self.startdate) + " " + make_time(self.stoptime)
        e.location = self.location
        # ics.py doesn't support repeating
        e.extra.append(ContentLine(
            name = "RRULE",
            value = "FREQ=WEEKLY;" + "UNTIL=" + make_date(self.enddate) + "T000000Z;" +
                "WKST=SU;BYDAY=" + make_days(self.days)
                ))
        return e

def make_calendar(string):
    return Calendar(events = [parse(course).as_event() for course in separate(string)])


def separate(fullstr, sep = "\n\n"):
    # Separate raw copy-pasted text into entries
    return [s for s in fullstr.split(sep) if s.strip() != ""]

def parse(entry, first_sep = " - ", second_sep = "\t"):
    # Parse entries into Course objects
    lines = entry.split("\n")
    first = lines[0]
    second = lines[-1]
    f_items = [s.strip() for s in first.split(first_sep)]
    s_items = [s.strip() for s in second.split(second_sep)]
    return Course(
            f_items[0],
            f_items[1],
            s_items[1].split(" - ")[0].strip(),
            s_items[1].split(" - ")[1].strip(),
            s_items[2],
            s_items[3],
            s_items[4].split(" - ")[0].strip(),
            s_items[4].split(" - ")[1].strip()
            )

def make_days(days):
    # Make repeat days from days like MWF
    return ",".join(
        [{"M": "MO", "T": "TU", "W": "WE", "R": "TH", "F": "FR"}[day.upper()] for day in days]
        )

def make_time(time):
    # Convert a time string from the text into an ics-suitable version
    parts = time.split(" ")
    pm = parts[1].strip() in ["pm", "PM"]
    hour = parts[0].split(":")[0].strip()
    minute = parts[0].split(":")[1].strip()
    if pm and int(hour) < 12:
        # 24 hour time
        hour = str(int(hour) + 12)
    if len(hour) < 2:
        # 01:00 not 1:00
        hour = "0" + hour
    return hour + ":" + minute + ":00"

def make_date(date):
    # Convert a date string from the text into an ics-suitable date
    month = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12"
            }[date.split(" ")[0].strip().lower()]
    day = date.split(" ")[1].strip()[:-1]
    year = date.split(" ")[2].strip()
    return "-".join([year, month, day])

def make_event(course):
    # Take a course object and turn it into an ics Event object
    e = Event()
    e.name = course.number + " " + course.name
    e.begin = make_time(course.starttime)
    e.end = make_time(course.endtime)
