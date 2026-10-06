import streamlit as st
import requests
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

# API_URL = "https://campusconnect-api-xp25.onrender.com"
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="CampusConnect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# API HELPER
# =========================================================

def api_get(endpoint):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:
        return None


def api_post(endpoint, data):

    try:

        response = requests.post(
            f"{API_URL}{endpoint}",
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:
        return None


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <style>

        .login-container {
            max-width: 500px;
            margin: 80px auto;
            padding: 35px;
            border-radius: 20px;
            background-color: #f8f9fa;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.10);
        }

        .login-title {
            text-align: center;
            font-size: 38px;
            font-weight: bold;
        }

        .login-subtitle {
            text-align: center;
            font-size: 18px;
            margin-bottom: 30px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-container">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">🎓 CampusConnect</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Student Portal</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    username = st.text_input(
        "👤 Username",
        placeholder="Enter your username"
    )

    password = st.text_input(
        "🔑 Password",
        type="password",
        placeholder="Enter your password"
    )

    login_button = st.button(
        "🔐 Login",
        type="primary",
        use_container_width=True
    )

    if login_button:

        if not username.strip():

            st.warning(
                "⚠️ Please enter username."
            )

        elif not password.strip():

            st.warning(
                "⚠️ Please enter password."
            )

        else:

            result = api_post(
                "/login",
                {
                    "username": username,
                    "password": password
                }
            )

            if result is None:

                st.error(
                    "❌ Unable to connect to FastAPI."
                )

                st.info(
                    "Make sure FastAPI is running."
                )

            else:

                login_success = result.get(
                    "success",
                    False
                )

                if not login_success:

                    login_success = result.get(
                        "status",
                        False
                    )

                if login_success:

                    st.session_state.logged_in = True

                    st.session_state.username = username

                    st.success(
                        "✅ Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid username or password."
                    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# =========================================================
# LOAD DATA AFTER LOGIN
# =========================================================

student = api_get("/student")
attendance = api_get("/attendance")
fees = api_get("/fees")
timetable = api_get("/timetable")
assignments = api_get("/assignments")
announcements = api_get("/announcements")
events = api_get("/events")


# =========================================================
# API STATUS
# =========================================================

if student is None:

    st.error(
        "⚠️ FastAPI server is not running."
    )

    st.info(
        "Start FastAPI using:"
    )

    st.code(
        "uv run fastapi dev api.py"
    )

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()

    st.stop()


# =========================================================
# STUDENT DETAILS
# =========================================================

student_name = student.get(
    "name",
    "Student"
)

# UI display name
display_name = "Admin"

roll_no = student.get(
    "roll_no",
    "-"
)

department = student.get(
    "department",
    "-"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎓 CampusConnect")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👤 Student Profile",
        "💰 Fee Details",
        "📊 Attendance",
        "📅 Timetable",
        "📝 Assignments",
        "📢 Announcements",
        "🎉 College Events",
        "💬 AI Assistant"
    ]
)

st.sidebar.markdown("---")

st.sidebar.write(
    f"👩‍💼 {display_name}"
)

st.sidebar.write(
    f"🎫 {roll_no}"
)

st.sidebar.write(
    "🟢 API Connected"
)

st.sidebar.markdown("---")


# =========================================================
# LOGOUT
# =========================================================

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False

    st.session_state.username = ""

    st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.title("🎓 CampusConnect")

    st.subheader(
        f"Welcome, {display_name} 👋"
    )

    st.markdown("---")

    st.header("📊 Student Dashboard")

    # ---------------------------------------------
    # ATTENDANCE
    # ---------------------------------------------

    if attendance:

        percentages = [
            float(item["percentage"])
            for item in attendance
        ]

        overall_attendance = (
            sum(percentages) / len(percentages)
        )

    else:

        overall_attendance = 0

    # ---------------------------------------------
    # FEE
    # ---------------------------------------------

    if fees:

        total_fee = fees[0]["total_fee"]
        paid_fee = fees[0]["paid_fee"]
        balance_fee = fees[0]["balance_fee"]

    else:

        total_fee = 0
        paid_fee = 0
        balance_fee = 0

    # ---------------------------------------------
    # ASSIGNMENTS
    # ---------------------------------------------

    if assignments:

        pending_assignments = len([
            x
            for x in assignments
            if x["status"].lower() == "pending"
        ])

    else:

        pending_assignments = 0

    # ---------------------------------------------
    # DASHBOARD CARDS
    # ---------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.info("👤 Student")

        st.write(
            f"**{display_name}**"
        )

        st.write(roll_no)

    with col2:

        st.success("📚 Department")

        st.write(department)

    with col3:

        st.warning("📊 Attendance")

        st.metric(
            "Overall",
            f"{overall_attendance:.1f}%"
        )

    with col4:

        st.error("📝 Pending")

        st.metric(
            "Assignments",
            pending_assignments
        )

    st.markdown("---")

    # ---------------------------------------------
    # FEE SUMMARY
    # ---------------------------------------------

    st.subheader("💰 Fee Summary")

    fee_col1, fee_col2, fee_col3 = st.columns(3)

    with fee_col1:

        st.metric(
            "Total Fee",
            f"₹{total_fee:,.0f}"
        )

    with fee_col2:

        st.metric(
            "Paid Fee",
            f"₹{paid_fee:,.0f}"
        )

    with fee_col3:

        st.metric(
            "Balance Fee",
            f"₹{balance_fee:,.0f}"
        )


# =========================================================
# STUDENT PROFILE
# =========================================================

elif page == "👤 Student Profile":

    st.title("👤 Student Profile")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Name")

        st.info(display_name)

        st.write("### Roll Number")

        st.info(roll_no)

    with col2:

        st.write("### Department")

        st.info(department)

        st.write("### Year")

        st.info("Final Year")


# =========================================================
# FEE DETAILS
# =========================================================

elif page == "💰 Fee Details":

    st.title("💰 Fee Details")

    st.markdown("---")

    if not fees:

        st.warning(
            "No fee details found."
        )

    else:

        fee = fees[0]

        total_fee = fee["total_fee"]
        paid_fee = fee["paid_fee"]
        balance_fee = fee["balance_fee"]
        due_date = fee["due_date"]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Fee",
                f"₹{total_fee:,.0f}"
            )

        with col2:

            st.metric(
                "Paid Fee",
                f"₹{paid_fee:,.0f}"
            )

        with col3:

            st.metric(
                "Balance Fee",
                f"₹{balance_fee:,.0f}"
            )

        st.markdown("---")

        st.write(
            f"📅 **Deadline:** {due_date}"
        )


# =========================================================
# ATTENDANCE
# =========================================================

elif page == "📊 Attendance":

    st.title("📊 Attendance")

    st.markdown("---")

    if not attendance:

        st.warning(
            "No attendance data found."
        )

    else:

        percentages = [
            float(item["percentage"])
            for item in attendance
        ]

        overall = (
            sum(percentages) /
            len(percentages)
        )

        st.subheader(
            f"Overall Attendance: {overall:.1f}%"
        )

        st.progress(
            min(overall / 100, 1.0)
        )

        st.markdown("---")

        st.subheader(
            "📚 Subject-wise Attendance"
        )

        data = []

        for item in attendance:

            data.append({
                "Subject": item["subject"],
                "Percentage": f"{item['percentage']}%"
            })

        st.table(
            pd.DataFrame(data)
        )


# =========================================================
# TIMETABLE
# =========================================================

elif page == "📅 Timetable":

    st.title("📅 Timetable")

    st.markdown("---")

    if not timetable:

        st.warning(
            "No timetable found."
        )

    else:

        data = []

        for item in timetable:

            data.append({
                "Day": item["day"],
                "Subject": item["subject"],
                "Time": item["time"],
                "Room": item["room"]
            })

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# ASSIGNMENTS
# =========================================================

elif page == "📝 Assignments":

    st.title("📝 Assignments")

    st.markdown("---")

    if not assignments:

        st.warning(
            "No assignments found."
        )

    else:

        for item in assignments:

            col1, col2 = st.columns([3, 1])

            with col1:

                st.write(
                    f"📝 **{item['title']}**"
                )

                st.write(
                    f"Subject: {item['subject']}"
                )

            with col2:

                st.write(
                    f"📅 {item['due_date']}"
                )

                if item["status"].lower() == "pending":

                    st.warning(
                        item["status"]
                    )

                else:

                    st.success(
                        item["status"]
                    )

            st.markdown("---")


# =========================================================
# ANNOUNCEMENTS
# =========================================================

elif page == "📢 Announcements":

    st.title("📢 Announcements")

    st.markdown("---")

    if not announcements:

        st.info(
            "No announcements available."
        )

    else:

        for item in announcements:

            st.subheader(
                f"📢 {item['title']}"
            )

            st.write(
                item["message"]
            )

            st.caption(
                f"📅 {item['created_date']}"
            )

            st.markdown("---")


# =========================================================
# COLLEGE EVENTS
# =========================================================

elif page == "🎉 College Events":

    st.title("🎉 College Events")

    st.markdown("---")

    if not events:

        st.info(
            "No events available."
        )

    else:

        for item in events:

            st.subheader(
                f"🎉 {item['event_name']}"
            )

            st.write(
                f"📅 **Date:** {item['event_date']}"
            )

            st.write(
                f"📍 **Venue:** {item['venue']}"
            )

            st.write(
                item["description"]
            )

            st.markdown("---")


# =========================================================
# AI ASSISTANT
# =========================================================

elif page == "💬 AI Assistant":

    st.title(
        "💬 CampusConnect AI Assistant"
    )

    st.write(
        "Ask questions about your student details, "
        "fees, attendance, timetable, assignments, "
        "announcements and events."
    )

    st.markdown("---")

    question = st.text_input(
        "Ask your question",
        placeholder="Example: What is my name?"
    )

    if st.button(
        "Ask",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            result = api_post(
                "/ask",
                {
                    "question": question
                }
            )

            if result is None:

                st.error(
                    "Unable to connect to FastAPI."
                )

            else:

                answers = result.get(
                    "answers",
                    []
                )

                if not answers:

                    st.warning(
                        "No answer found."
                    )

                else:

                    for item in answers:

                        st.success(
                            item["answer"]
                        )