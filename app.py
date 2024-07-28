import streamlit as st
import time
import pandas as pd

# Database stuff
from pymongo import MongoClient

client = MongoClient("mongodb+srv://nakshatradubey:NSlVfXFGT1lrlIql@tutornet.2k02z1h.mongodb.net/")

db = client['TutorNet_Database']

collection = db['Users']

if 'user' not in st.session_state:
    st.session_state.user = None

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'points' not in st.session_state:
    st.session_state.points = ""

if 'subjects' not in st.session_state:
    st.session_state.subjects = ""

if 'times' not in st.session_state:
    st.session_state.times = ""

if 'days' not in st.session_state:
    st.session_state.days = ""

if 'grade' not in st.session_state:
    st.session_state.grade = None

if 'classes_taught' not in st.session_state:
    st.session_state.classes_taught = None

if 'classes_taken' not in st.session_state:
    st.session_state.classes_taken = None

if 'pool' not in st.session_state:
    st.session_state.pool = None

if "tutor" not in st.session_state:
    st.session_state.tutor = None

# Streamlit code

tabs = st.tabs(["Get a Tutor", "View Tutors", "My profile", "Register", "Sign in" , "Classes"])
credit = 20

def update_credit_score(current_score, rating_given):
    # Define parameters
    max_impact = 50
    neutral_rating = 5
    min_score = 500
    max_score = 1500
    
    # Calculate rating impact per point
    rating_impact = max_impact / neutral_rating  # 10 points per rating unit difference
    
    # Calculate change in score based on rating
    delta_s = rating_impact * (rating_given - neutral_rating)
    
    # Update score based on rating
    new_score = current_score + delta_s
    
    # Ensure score is within the defined range
    if new_score < min_score:
        new_score = min_score
    elif new_score > max_score:
        new_score = max_score
    
    return new_score


with tabs[5]: # Classes Tab
    st.title("Your Classes")
    if st.button("View Classes"):
        if st.session_state.user is None:
            st.error("Register or Sign-in before viewing this tab!")
        else:
            st.write(f"Your Students: {st.session_state.user.get('students')}")
            st.write(f"Your Tutors: {st.session_state.tutor.get("name")} on {st.session_state.days} at {st.session_state.times} for {st.session_state.tutor.get("subjects")}")
    
    if (st.session_state.tutor is not None):
        tutor_rating = st.text_input("Rate your tutor")
                
        if st.button("Submit Rating"):
            current_tutor_points = st.session_state.tutor.get("points")
            new_points = update_credit_score(current_tutor_points, int(tutor_rating))
            collection.update_one({"name": st.session_state.tutor.get("name")}, {"$set": {"points": new_points}})
            st.session_state.tutor = collection.find_one({"name": st.session_state.tutor.get("name")})
            st.success(f"Updated Tutor Points: {new_points}")

def assign_pool(credit_score):
    min_score = 500
    interval = 200
    num_pools = 5
    
    pool_index = (credit_score - min_score) // interval + 1

    
    # Ensure pool index is within range [1, 5]
    if pool_index < 1:
        pool_index = 1
    elif pool_index > num_pools:
        pool_index = num_pools

    # Pool 1 --> anything < 500
    # Pool 2 --> 500-699
    # Pool 3 --> 700-899
    # Pool 4 --> 900-1099
    # Pool 5 --> anything >= 1100

    return pool_index 


with tabs[0]: # Get a tutor tab
    st.header("Get a Tutor")
    help_subject = st.selectbox("Which subject do you need help in?", ["Math", "English", "Physics", "Chemistry", "Computer Science"])
    if st.button("Get a Tutor!"):
        if st.session_state.user is None:
            st.error("Register or Sign-in before viewing this tab!")
        else:
            user_list = collection.find({})
            for temp_user in user_list:
                collection.update_one({"name":temp_user.get("name")},{"$set":{"pool":assign_pool(temp_user.get("points"))}})
            st.session_state.pool = st.session_state.user.get("pool")

            pool_list = collection.find({"pool":st.session_state.pool})
            for temp_tutor in pool_list:
                if temp_tutor.get("name") == st.session_state.username:
                    continue #student cannot pick himself
                tutor_subject = temp_tutor.get("subjects")
                
                if help_subject == tutor_subject: 
                    if st.session_state.times == temp_tutor.get("times"):
                        if st.session_state.grade == temp_tutor.get("grade"):
                            if st.session_state.days == temp_tutor.get("days"):
                                st.session_state.tutor = temp_tutor
                                break
            if st.session_state.tutor is not None:
                with st.spinner("Matching Subjects......"):
                    time.sleep(1)
                with st.spinner("Matching Days......"):
                    time.sleep(1)
                with st.spinner("Matching Times......"):
                    time.sleep(1)
                with st.spinner("Selecting the best tutor......"):
                    time.sleep(1)
                st.success(f"You have been matched with {st.session_state.tutor.get("name")}")
    if st.session_state.tutor is not None:
        if st.button("Confirm"):
            collection.update_one({"name":st.session_state.username}, {"$set":{"tutors":st.session_state.tutor.get("name")}})
            collection.update_one({"name":st.session_state.tutor.get("name")}, {"$set":{"students":st.session_state.username}})
            with st.spinner("Confirming....."):
                time.sleep(1)
            st.success(f"Confirmed Class with {st.session_state.tutor.get("name")} on {st.session_state.days} at {st.session_state.times} for {help_subject}")


                

with tabs[2]: # Profile Tab
    st.title("Your Profile")
    if st.button("View Profile!"):
        if st.session_state.user is None:
            st.error("Register or Sign-in before viewing this tab!")
        else:
            st.write("Username:", st.session_state.username)
            st.write("Credit Points:", st.session_state.points)
            st.write("Grade:", st.session_state.grade)
            st.write("Strong Subjects:", st.session_state.subjects)
            st.write("Available Times:", st.session_state.times)
            st.write("Available Days:", st.session_state.days)
            st.write("Classes Taught:", st.session_state.classes_taught)
            st.write("Classes Taken:", st.session_state.classes_taken)



def form_validity(name, grade, subjects, days, times):
    return bool(name) and bool(grade) and bool(subjects) and bool(days) and bool(times)

with tabs[3]: # Register Tab
    st.header("Register")
    st.write("Already registered? Try the sign-in tab instead.")
    name = st.text_input("What's your name?")
    password = st.text_input("What's your password? (minimum length is 8)")
    grade = st.selectbox("Which grade are you in?", ["9", "10", "11", "12"])
    strong_subjects = st.multiselect("What are your strong subjects?", ["Math", "English", "Physics", "Chemistry", "Computer Science"])
    available_days = st.multiselect("Which day suits you?", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    available_times = st.multiselect("Time:", ["4:00pm", "5:00pm", "6:00pm", "7:00pm", "8:00pm", "9:00pm", "10:00 pm"])
    points = 1020
    students = ""
    tutors = ""

    name_exists = collection.find_one({"name": name}) is not None
    error_message = st.empty()
    if name_exists:
        error_message.error("The name already exists!")
    else:
        error_message.empty() 

    valid = form_validity(name, grade, strong_subjects, available_days, available_times)

    if st.button("Register!"):
        if name_exists:
            st.error("That name already exists!")
        elif len(name) < 5:
            st.error("Username has to be at least 5 characters")
        elif not valid:
            st.error("Do not leave a question empty!")
        elif len(password) < 8:
            st.error("Password is too short!")
        else:
            with st.spinner("Submitting..."):
                time.sleep(1)
            with st.spinner("Creating profile..."):
                time.sleep(2)

            subjects = ", ".join(strong_subjects)
            days = ", ".join(available_days)
            times = ", ".join(available_times)
            
            classes_taught = 0
            classes_taken = 0

            pool = None

            collection.insert_one({"name": name, "password": password, "grade": grade, "subjects": subjects, "times": times, "days": days, "points":points, "classes_taught":classes_taught, "classes_taken":classes_taken, "pool":pool, "students":students, "tutors":tutors})
            st.success("Profile Created!")
            st.success("+20 Credit Points")
            st.session_state.username = name
            st.session_state.user = collection.find_one({"name":st.session_state.username})
            st.session_state.grade = st.session_state.user.get("grade")
            st.session_state.subjects = st.session_state.user.get("subjects")
            st.session_state.times = st.session_state.user.get("times")
            st.session_state.days = st.session_state.user.get("days")
            st.session_state.points = st.session_state.user.get("points")
            st.session_state.classes_taught = st.session_state.user.get("classes_taught")
            st.session_state.classes_taken = st.session_state.user.get("classes_taken")

        
with tabs[4]: # Sign-in

        st.header("Sign-in")
        st.write("Haven't created an account? Try the Register page.")
        name = st.text_input("Username", key = "sign_in_name")
        entered_password = st.text_input("Password", key="sign_in_password")

        temp_user = collection.find_one({"name":name})
        name_exists = False
        password_is_correct = False
        
        if temp_user:
            name_exists = True
            if (entered_password == temp_user.get("password")):
                password_is_correct = True

        valid = name_exists and password_is_correct and bool(name) and bool(entered_password)

        if st.button("Sign-in!"):
            with st.spinner("Checking username and password...."):
                time.sleep(2)
            if not valid:
                st.error("Incorrect username or password.")
            else:
                st.session_state.username = name
                st.session_state.user = collection.find_one({"name":st.session_state.username})
                st.session_state.grade = st.session_state.user.get("grade")
                st.session_state.subjects = st.session_state.user.get("subjects")
                st.session_state.times = st.session_state.user.get("times")
                st.session_state.days = st.session_state.user.get("days")
                st.session_state.points = st.session_state.user.get("points")
                st.session_state.classes_taught = st.session_state.user.get("classes_taught")
                st.session_state.classes_taken = st.session_state.user.get("classes_taken")
                with st.spinner("Logging in....."):
                    time.sleep(2)
                st.success("Logged in!")


def display_leaderboard():
    projection = {"_id": 0, "name": 1, "points": 1, "classes_taught":1, "subjects":1}
    cursor = collection.find({}, projection)
    data = list(cursor)
    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by="points", ascending=False).reset_index(drop=True)
    df_sorted.index += 1
    df_sorted.rename(columns={"name":"Username", "points":"Credit Points", "subjects":"Strong Subjects", "classes_taught":"Classes Taught"}, inplace=True)
    st.table(df_sorted)

with tabs[1]:
    if st.button("View Leaderboard!"):
        if st.session_state.user is None:
            st.error("Register or Sign-in before viewing this tab!")
        else:    
            with st.container():
                st.title("Leaderboard")
                display_leaderboard()
        
        
