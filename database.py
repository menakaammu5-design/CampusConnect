import sqlite3

DB_NAME = "campus.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# CREATE TABLES
# =========================================================

def create_tables():

    conn = get_connection()
    c = conn.cursor()

    # STUDENTS
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            department TEXT
        )
    """)

    # USERS
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            student_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    # ATTENDANCE
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT NOT NULL,
            percentage REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    # FEES
    c.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            total_fee REAL NOT NULL,
            paid_fee REAL NOT NULL,
            due_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    # TIMETABLE
    c.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            time TEXT NOT NULL,
            room TEXT
        )
    """)

    # ASSIGNMENTS
    c.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            title TEXT NOT NULL,
            subject TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    # ANNOUNCEMENTS
    c.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            created_date TEXT
        )
    """)

    # EVENTS
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            venue TEXT,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# INSERT SAMPLE DATA
# =========================================================

def insert_sample_data():

    conn = get_connection()
    c = conn.cursor()

    # =====================================================
    # STUDENT
    # =====================================================

    c.execute("""
        INSERT OR IGNORE INTO students
        (name, roll_no, department)
        VALUES (?, ?, ?)
    """, (
        "Admin",
        "CSE001",
        "Computer Science and Engineering"
    ))

    c.execute("""
        SELECT id
        FROM students
        WHERE roll_no = ?
    """, ("CSE001",))

    student = c.fetchone()

    if not student:
        conn.close()
        return

    student_id = student[0]

    # =====================================================
    # LOGIN USER
    # =====================================================

    c.execute("""
        INSERT OR IGNORE INTO users
        (username, password, student_id)
        VALUES (?, ?, ?)
    """, (
        "admin",
        "admin",
        student_id
    ))

    # =====================================================
    # ATTENDANCE
    # =====================================================

    count = c.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE student_id = ?
    """, (student_id,)).fetchone()[0]

    if count == 0:

        attendance_data = [
            (student_id, "Java", 92),
            (student_id, "Python", 85),
            (student_id, "Artificial Intelligence", 78),
            (student_id, "Machine Learning", 88),
            (student_id, "Deep Learning", 81),
            (student_id, "HTML", 95),
            (student_id, "CSS", 90),
            (student_id, "SQL", 87)
        ]

        c.executemany("""
            INSERT INTO attendance
            (student_id, subject, percentage)
            VALUES (?, ?, ?)
        """, attendance_data)

    # =====================================================
    # FEES
    # =====================================================

    count = c.execute("""
        SELECT COUNT(*)
        FROM fees
        WHERE student_id = ?
    """, (student_id,)).fetchone()[0]

    if count == 0:

        c.execute("""
            INSERT INTO fees
            (student_id, total_fee, paid_fee, due_date)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            50000,
            35000,
            "15 Oct 2026"
        ))

    # =====================================================
    # TIMETABLE
    # =====================================================

    count = c.execute("""
        SELECT COUNT(*)
        FROM timetable
    """).fetchone()[0]

    if count == 0:

        timetable_data = [
            ("Monday", "Java", "9:00 AM", "Room 101"),
            ("Monday", "Python", "11:00 AM", "Lab 2"),
            ("Tuesday", "Artificial Intelligence", "10:00 AM", "Room 205"),
            ("Wednesday", "Database", "9:00 AM", "Room 102"),
            ("Thursday", "Web Development", "11:00 AM", "Lab 1"),
            ("Friday", "Agentic AI", "10:00 AM", "AI Lab")
        ]

        c.executemany("""
            INSERT INTO timetable
            (day, subject, time, room)
            VALUES (?, ?, ?, ?)
        """, timetable_data)

    # =====================================================
    # ASSIGNMENTS
    # =====================================================

    count = c.execute("""
        SELECT COUNT(*)
        FROM assignments
        WHERE student_id = ?
    """, (student_id,)).fetchone()[0]

    if count == 0:

        assignment_data = [

            (
                student_id,
                "Java Mini Project",
                "Java",
                "30 Sep 2026",
                "Pending"
            ),

            (
                student_id,
                "Python Lab Record",
                "Python",
                "2 Oct 2026",
                "Submitted"
            ),

            (
                student_id,
                "AI Seminar",
                "Artificial Intelligence",
                "5 Oct 2026",
                "Pending"
            ),

            (
                student_id,
                "Agentic AI Assignment",
                "Agentic AI",
                "10 Oct 2026",
                "Pending"
            )
        ]

        c.executemany("""
            INSERT INTO assignments
            (student_id, title, subject, due_date, status)
            VALUES (?, ?, ?, ?, ?)
        """, assignment_data)

    # =====================================================
    # ANNOUNCEMENTS
    # =====================================================

    count = c.execute("""
        SELECT COUNT(*)
        FROM announcements
    """).fetchone()[0]

    if count == 0:

        announcement_data = [

            (
                "Exam Notice",
                "Internal examination starts from 10 October 2026.",
                "29 Sep 2026"
            ),

            (
                "Placement Drive",
                "Campus placement registration is open.",
                "29 Sep 2026"
            ),

            (
                "Assignment Notice",
                "Submit pending assignments before the deadline.",
                "30 Sep 2026"
            )
        ]

        c.executemany("""
            INSERT INTO announcements
            (title, message, created_date)
            VALUES (?, ?, ?)
        """, announcement_data)

    # =====================================================
    # EVENTS
    # =====================================================

    count = c.execute("""
        SELECT COUNT(*)
        FROM events
    """).fetchone()[0]

    if count == 0:

        event_data = [

            (
                "AI Workshop",
                "5 Oct 2026",
                "Seminar Hall",
                "Workshop on Generative AI"
            ),

            (
                "Hackathon",
                "12 Oct 2026",
                "Computer Lab",
                "24-hour college hackathon"
            ),

            (
                "Cultural Fest",
                "20 Oct 2026",
                "College Auditorium",
                "Annual college cultural event"
            )
        ]

        c.executemany("""
            INSERT INTO events
            (event_name, event_date, venue, description)
            VALUES (?, ?, ?, ?)
        """, event_data)

    conn.commit()
    conn.close()


# =========================================================
# RUN DATABASE SETUP
# =========================================================

if __name__ == "__main__":

    create_tables()
    insert_sample_data()

    print("Database created successfully!")
    print("Sample data inserted successfully!")