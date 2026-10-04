from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import get_connection
from datetime import datetime
import re
from database import create_tables, insert_sample_data


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="CampusConnect API",
    version="1.0"
)

create_tables()
insert_sample_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# REQUEST MODELS
# =========================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class QuestionRequest(BaseModel):
    question: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "CampusConnect API is running"
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login(request: LoginRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            users.id,
            users.username,
            users.student_id,
            students.name,
            students.roll_no,
            students.department
        FROM users
        JOIN students
        ON users.student_id = students.id
        WHERE users.username = ?
        AND users.password = ?
    """, (
        request.username,
        request.password
    ))

    row = cursor.fetchone()

    conn.close()

    if not row:

        return {
            "success": False,
            "message": "Invalid username or password"
        }

    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "user_id": row[0],
            "username": row[1],
            "student_id": row[2],
            "name": row[3],
            "roll_no": row[4],
            "department": row[5]
        }
    }


# =========================================================
# STUDENT
# =========================================================

@app.get("/student")
def get_student():

    conn = get_connection()

    row = conn.execute("""
        SELECT id, name, roll_no, department
        FROM students
        WHERE id = 1
    """).fetchone()

    conn.close()

    if not row:
        return {}

    return {
        "id": row[0],
        "name": row[1],
        "roll_no": row[2],
        "department": row[3]
    }


# =========================================================
# STUDENTS
# =========================================================

@app.get("/students")
def get_students():

    conn = get_connection()

    rows = conn.execute("""
        SELECT id, name, roll_no, department
        FROM students
    """).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "roll_no": row[2],
            "department": row[3]
        }
        for row in rows
    ]


# =========================================================
# ATTENDANCE
# =========================================================

@app.get("/attendance")
def get_attendance():

    conn = get_connection()

    rows = conn.execute("""
        SELECT id, student_id, subject, percentage
        FROM attendance
        WHERE student_id = 1
    """).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "student_id": row[1],
            "subject": row[2],
            "percentage": row[3]
        }
        for row in rows
    ]


# =========================================================
# FEES
# =========================================================

@app.get("/fees")
def get_fees():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            id,
            student_id,
            total_fee,
            paid_fee,
            due_date
        FROM fees
        WHERE student_id = 1
    """).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "student_id": row[1],
            "total_fee": row[2],
            "paid_fee": row[3],
            "balance_fee": row[2] - row[3],
            "due_date": row[4]
        }
        for row in rows
    ]


# =========================================================
# TIMETABLE
# =========================================================

@app.get("/timetable")
def get_timetable():

    conn = get_connection()

    rows = conn.execute("""
        SELECT id, day, subject, time, room
        FROM timetable
        ORDER BY id
    """).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "day": row[1],
            "subject": row[2],
            "time": row[3],
            "room": row[4]
        }
        for row in rows
    ]


# =========================================================
# ASSIGNMENTS
# =========================================================

@app.get("/assignments")
def get_assignments():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            id,
            student_id,
            title,
            subject,
            due_date,
            status
        FROM assignments
        WHERE student_id = 1
        ORDER BY id
    """).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "student_id": row[1],
            "title": row[2],
            "subject": row[3],
            "due_date": row[4],
            "status": row[5]
        }
        for row in rows
    ]


# =========================================================
# ANNOUNCEMENTS
# =========================================================

@app.get("/announcements")
def get_announcements():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            id,
            title,
            message,
            created_date
        FROM announcements
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "message": row[2],
            "created_date": row[3]
        }
        for row in rows
    ]


# =========================================================
# EVENTS
# =========================================================

@app.get("/events")
def get_events():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            id,
            event_name,
            event_date,
            venue,
            description
        FROM events
        ORDER BY id
    """).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "event_name": row[1],
            "event_date": row[2],
            "venue": row[3],
            "description": row[4]
        }
        for row in rows
    ]


# =========================================================
# DATE PARSER
# =========================================================

def extract_date(question):

    question = question.lower()

    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,

        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "sept": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12
    }

    month_pattern = (
        r"january|february|march|april|may|june|july|"
        r"august|september|october|november|december|"
        r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
    )

    # October 5 2026
    match = re.search(
        rf"\b({month_pattern})\s+(\d{{1,2}})"
        rf"(?:\s+(\d{{4}}))?\b",
        question
    )

    if match:

        return datetime(
            int(match.group(3) or 2026),
            months[match.group(1)],
            int(match.group(2))
        )

    # 5 October 2026
    match = re.search(
        rf"\b(\d{{1,2}})\s+({month_pattern})"
        rf"(?:\s+(\d{{4}}))?\b",
        question
    )

    if match:

        return datetime(
            int(match.group(3) or 2026),
            months[match.group(2)],
            int(match.group(1))
        )

    # 05/10/2026
    match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b",
        question
    )

    if match:

        return datetime(
            int(match.group(3)),
            int(match.group(2)),
            int(match.group(1))
        )

    return None


# =========================================================
# QUESTION SPLITTER
# =========================================================

def split_questions(question):

    question = re.sub(
        r"^\s*you\s*:\s*",
        "",
        question.strip(),
        flags=re.IGNORECASE
    )

    return [
        q.strip()
        for q in re.split(r"\?", question)
        if q.strip()
    ]


# =========================================================
# PROCESS QUESTION
# =========================================================

def process_single_question(question):

    q = question.lower().strip()

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # STUDENT DETAILS
    # =====================================================

    if any(
        x in q
        for x in [
            "name",
            "who am i",
            "roll number",
            "roll no",
            "department"
        ]
    ):

        cursor.execute("""
            SELECT name, roll_no, department
            FROM students
            WHERE id = 1
        """)

        row = cursor.fetchone()

        conn.close()

        if row:

            answers = []

            if "name" in q or "who am i" in q:
                answers.append(row[0])

            if "roll" in q:
                answers.append(row[1])

            if "department" in q:
                answers.append(row[2])

            if answers:
                return "\n".join(answers)

    # =====================================================
    # FEES
    # =====================================================

    if any(
        x in q
        for x in [
            "fee",
            "fees",
            "paid",
            "balance",
            "remaining",
            "total",
            "due"
        ]
    ):

        cursor.execute("""
            SELECT total_fee, paid_fee, due_date
            FROM fees
            WHERE student_id = 1
        """)

        row = cursor.fetchone()

        conn.close()

        if row:

            total, paid, due_date = row
            balance = total - paid

            answers = []

            if any(
                x in q
                for x in [
                    "total",
                    "overall",
                    "how much fee"
                ]
            ):
                answers.append(
                    f"₹{total:,.0f}"
                )

            if any(
                x in q
                for x in [
                    "paid",
                    "already paid",
                    "i paid"
                ]
            ):
                answers.append(
                    f"₹{paid:,.0f}"
                )

            if any(
                x in q
                for x in [
                    "balance",
                    "remaining",
                    "left"
                ]
            ):
                answers.append(
                    f"₹{balance:,.0f}"
                )

            if any(
                x in q
                for x in [
                    "due date",
                    "deadline",
                    "when should"
                ]
            ):
                answers.append(due_date)

            if answers:
                return "\n".join(answers)

            return (
                f"Total Fee: ₹{total:,.0f}\n"
                f"Paid Fee: ₹{paid:,.0f}\n"
                f"Balance Fee: ₹{balance:,.0f}\n"
                f"Due Date: {due_date}"
            )

    # =====================================================
    # ATTENDANCE
    # =====================================================

    if "attendance" in q or "percentage" in q:

        rows = cursor.execute("""
            SELECT subject, percentage
            FROM attendance
            WHERE student_id = 1
        """).fetchall()

        conn.close()

        for row in rows:

            if row[0].lower() in q:

                return (
                    f"Your {row[0]} attendance "
                    f"is {row[1]}%."
                )

        if not rows:
            return "No attendance data found."

        return "\n".join(
            f"{row[0]}: {row[1]}%"
            for row in rows
        )

    # =====================================================
    # ANNOUNCEMENTS
    # =====================================================

    if any(
        x in q
        for x in [
            "announcement",
            "announcements",
            "notice",
            "notices"
        ]
    ):

        rows = cursor.execute("""
            SELECT title, message, created_date
            FROM announcements
            ORDER BY id DESC
        """).fetchall()

        conn.close()

        if not rows:
            return "There are no announcements."

        return "\n\n".join(
            f"{row[0]}\n"
            f"{row[1]}\n"
            f"Date: {row[2]}"
            for row in rows
        )

    # =====================================================
    # ASSIGNMENTS
    # =====================================================

    if any(
        x in q
        for x in [
            "assignment",
            "assignments",
            "homework"
        ]
    ):

        rows = cursor.execute("""
            SELECT title, subject, due_date, status
            FROM assignments
            WHERE student_id = 1
            ORDER BY id
        """).fetchall()

        conn.close()

        if not rows:
            return "No assignments found."

        target_date = extract_date(q)

        filtered = []

        for row in rows:

            if not target_date:
                filtered.append(row)
                continue

            try:

                assignment_date = datetime.strptime(
                    row[2],
                    "%d %b %Y"
                )

                if assignment_date <= target_date:
                    filtered.append(row)

            except ValueError:

                filtered.append(row)

        if "pending" in q:

            filtered = [
                row
                for row in filtered
                if row[3].lower() == "pending"
            ]

        if not filtered:
            return "No assignments found."

        return "\n\n".join(
            f"{row[0]}\n"
            f"Subject: {row[1]}\n"
            f"Due Date: {row[2]}\n"
            f"Status: {row[3]}"
            for row in filtered
        )

    # =====================================================
    # TIMETABLE
    # =====================================================

    if any(
        x in q
        for x in [
            "class",
            "timetable",
            "schedule",
            "lecture"
        ]
    ):

        rows = cursor.execute("""
            SELECT day, subject, time, room
            FROM timetable
            ORDER BY id
        """).fetchall()

        conn.close()

        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday"
        ]

        for day in days:

            if day in q:

                day_rows = [
                    row
                    for row in rows
                    if row[0].lower() == day
                ]

                if not day_rows:
                    return f"No classes found for {day.title()}."

                return "\n".join(
                    f"{row[2]} - {row[1]} - {row[3]}"
                    for row in day_rows
                )

        return "\n".join(
            f"{row[0]} - {row[2]} - "
            f"{row[1]} - {row[3]}"
            for row in rows
        )

    # =====================================================
    # EVENTS
    # =====================================================

    if any(
        x in q
        for x in [
            "event",
            "events",
            "workshop",
            "hackathon"
        ]
    ):

        rows = cursor.execute("""
            SELECT event_name, event_date, venue, description
            FROM events
            ORDER BY id
        """).fetchall()

        conn.close()

        if not rows:
            return "No events found."

        return "\n\n".join(
            f"{row[0]}\n"
            f"Date: {row[1]}\n"
            f"Venue: {row[2]}\n"
            f"{row[3]}"
            for row in rows
        )

    # =====================================================
    # UNKNOWN
    # =====================================================

    conn.close()

    return (
        "I could not find relevant information "
        "in the CampusConnect database."
    )


# =========================================================
# ASK
# =========================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    questions = split_questions(
        request.question
    )

    return {
        "answers": [
            {
                "question": question,
                "answer": process_single_question(question)
            }
            for question in questions
        ]
    }