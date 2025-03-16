import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase (for Colab)
if not firebase_admin._apps:
    cred = credentials.Certificate("/content/securityAccountkey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 1. Users Collection CRUD Operations
def create_user(name, email, role, courses):
    user = {
        "name": name,
        "email": email,
        "role": role,
        "courses": courses,
        "created_at": datetime.now()
    }
    # Add submission and grade history only for students
    if role.lower() == "student":
        user["submission_history"] = []
        user["grade_history"] = []
    
    try:
        result = db.collection('users').add(user)
        user_id = result[1].id
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            return user_id
        else:
            raise Exception("Failed to verify user creation")
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def read_user(user_id):
    try:
        user = db.collection('users').document(user_id.strip()).get()
        return user.to_dict() if user.exists else None
    except Exception as e:
        print(f"Error reading user: {e}")
        return None

def update_user(user_id, update_fields):
    try:
        user_id = user_id.strip()
        if not user_id:
            print("Error: User ID cannot be empty")
            return
        if not update_fields:
            print("Error: No fields provided to update")
            return
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            print(f"No user found with ID: {user_id}")
            return
        doc_ref.update(update_fields)
        print(f"User updated successfully with ID: {user_id}")
    except Exception as e:
        print(f"Error updating user: {e}")

def delete_user(user_id):
    try:
        user_id = user_id.strip()
        if not user_id:
            print("Error: User ID cannot be empty")
            return
        db.collection('users').document(user_id).delete()
    except Exception as e:
        print(f"Error deleting user: {e}")

def update_student_history(student_id, submission_id, grade=None):
    try:
        student_id = student_id.strip()
        user = read_user(student_id)
        if not user or user.get('role').lower() != 'student':
            print("Error: User is not a student or doesn't exist")
            return
        
        update_fields = {}
        submission_history = user.get('submission_history', [])
        submission_history.append({
            'submission_id': submission_id,
            'timestamp': datetime.now()
        })
        update_fields['submission_history'] = submission_history
        
        if grade is not None:
            grade_history = user.get('grade_history', [])
            grade_history.append({
                'submission_id': submission_id,
                'grade': grade,
                'timestamp': datetime.now()
            })
            update_fields['grade_history'] = grade_history
            
        update_user(student_id, update_fields)
    except Exception as e:
        print(f"Error updating student history: {e}")

# 2. Courses Collection CRUD Operations
def create_course(course_name, teacher_id, assignments):
    course = {
        "courseName": course_name,
        "teacherId": teacher_id,
        "assignments": assignments,
        "created_at": datetime.now()
    }
    try:
        result = db.collection('courses').add(course)
        return result[1].id
    except Exception as e:
        print(f"Error creating course: {e}")
        return None

def read_course(course_id):
    try:
        course = db.collection('courses').document(course_id.strip()).get()
        return course.to_dict() if course.exists else None
    except Exception as e:
        print(f"Error reading course: {e}")
        return None

def update_course(course_id, update_fields):
    try:
        course_id = course_id.strip()
        if not course_id:
            print("Error: Course ID cannot be empty")
            return
        if not update_fields:
            print("Error: No fields provided to update")
            return
        doc_ref = db.collection('courses').document(course_id)
        doc = doc_ref.get()
        if not doc.exists:
            print(f"No course found with ID: {course_id}")
            return
        doc_ref.update(update_fields)
        print(f"Course updated successfully with ID: {course_id}")
    except Exception as e:
        print(f"Error updating course: {e}")

def delete_course(course_id):
    try:
        course_id = course_id.strip()
        if not course_id:
            print("Error: Course ID cannot be empty")
            return
        db.collection('courses').document(course_id).delete()
    except Exception as e:
        print(f"Error deleting course: {e}")

# 3. Assignments Collection CRUD Operations
def create_assignment(course_id, title, description, due_date):
    assignment = {
        "courseId": course_id,
        "title": title,
        "description": description,
        "dueDate": due_date,
        "created_at": datetime.now()
    }
    try:
        result = db.collection('assignments').add(assignment)
        return result[1].id
    except Exception as e:
        print(f"Error creating assignment: {e}")
        return None

def read_assignment(assignment_id):
    try:
        assignment = db.collection('assignments').document(assignment_id.strip()).get()
        return assignment.to_dict() if assignment.exists else None
    except Exception as e:
        print(f"Error reading assignment: {e}")
        return None

def update_assignment(assignment_id, update_fields):
    try:
        assignment_id = assignment_id.strip()
        if not assignment_id:
            print("Error: Assignment ID cannot be empty")
            return
        if not update_fields:
            print("Error: No fields provided to update")
            return
        doc_ref = db.collection('assignments').document(assignment_id)
        doc = doc_ref.get()
        if not doc.exists:
            print(f"No assignment found with ID: {assignment_id}")
            return
        doc_ref.update(update_fields)
        print(f"Assignment updated successfully with ID: {assignment_id}")
    except Exception as e:
        print(f"Error updating assignment: {e}")

def delete_assignment(assignment_id):
    try:
        assignment_id = assignment_id.strip()
        if not assignment_id:
            print("Error: Assignment ID cannot be empty")
            return
        db.collection('assignments').document(assignment_id).delete()
    except Exception as e:
        print(f"Error deleting assignment: {e}")

# 4. Submissions Collection CRUD Operations
def create_submission(assignment_id, student_id, submission_date, content):
    submission = {
        "assignmentId": assignment_id,
        "studentId": student_id,
        "submissionDate": submission_date,
        "content": content,
        "grade": None,
        "feedbackId": None,
        "created_at": datetime.now()
    }
    try:
        result = db.collection('submissions').add(submission)
        submission_id = result[1].id
        # Update student history
        update_student_history(student_id, submission_id)
        return submission_id
    except Exception as e:
        print(f"Error creating submission: {e}")
        return None

def read_submission(submission_id):
    try:
        submission = db.collection('submissions').document(submission_id.strip()).get()
        return submission.to_dict() if submission.exists else None
    except Exception as e:
        print(f"Error reading submission: {e}")
        return None

def update_submission(submission_id, update_fields):
    try:
        submission_id = submission_id.strip()
        if not submission_id:
            print("Error: Submission ID cannot be empty")
            return
        if not update_fields:
            print("Error: No fields provided to update")
            return
        doc_ref = db.collection('submissions').document(submission_id)
        doc = doc_ref.get()
        if not doc.exists:
            print(f"No submission found with ID: {submission_id}")
            return
        doc_ref.update(update_fields)
        print(f"Submission updated successfully with ID: {submission_id}")
    except Exception as e:
        print(f"Error updating submission: {e}")

def delete_submission(submission_id):
    try:
        submission_id = submission_id.strip()
        if not submission_id:
            print("Error: Submission ID cannot be empty")
            return
        db.collection('submissions').document(submission_id).delete()
    except Exception as e:
        print(f"Error deleting submission: {e}")

def evaluate_submission(submission_id, grade):
    update_fields = {"grade": grade, "graded_at": datetime.now()}
    update_submission(submission_id, update_fields)
    # Update student grade history
    submission = read_submission(submission_id)
    if submission and submission.get('studentId'):
        update_student_history(submission['studentId'], submission_id, grade)

# 5. Feedback Collection CRUD Operations
def create_feedback(submission_id, comments, suggestions):
    feedback = {
        "submissionId": submission_id,
        "comments": comments,
        "suggestions": suggestions,
        "created_at": datetime.now()
    }
    try:
        result = db.collection('feedback').add(feedback)
        return result[1].id
    except Exception as e:
        print(f"Error creating feedback: {e}")
        return None

def read_feedback(feedback_id):
    try:
        feedback = db.collection('feedback').document(feedback_id.strip()).get()
        return feedback.to_dict() if feedback.exists else None
    except Exception as e:
        print(f"Error reading feedback: {e}")
        return None

def update_feedback(feedback_id, update_fields):
    try:
        feedback_id = feedback_id.strip()
        if not feedback_id:
            print("Error: Feedback ID cannot be empty")
            return
        if not update_fields:
            print("Error: No fields provided to update")
            return
        doc_ref = db.collection('feedback').document(feedback_id)
        doc = doc_ref.get()
        if not doc.exists:
            print(f"No feedback found with ID: {feedback_id}")
            return
        doc_ref.update(update_fields)
        print(f"Feedback updated successfully with ID: {feedback_id}")
    except Exception as e:
        print(f"Error updating feedback: {e}")

def delete_feedback(feedback_id):
    try:
        feedback_id = feedback_id.strip()
        if not feedback_id:
            print("Error: Feedback ID cannot be empty")
            return
        db.collection('feedback').document(feedback_id).delete()
    except Exception as e:
        print(f"Error deleting feedback: {e}")

# User Interface Functions
def register_user():
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    role = input("Enter your role (student/teacher): ")
    courses = []
    user_id = create_user(name, email, role, courses)
    if user_id:
        print(f"User created with ID: {user_id}")
    return user_id

def user_menu():
    while True:
        print("\nUser Menu:")
        print("1. Create User")
        print("2. Read User")
        print("3. Update User")
        print("4. Delete User")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            user_id = input("Enter user ID to read: ").strip()
            user = read_user(user_id)
            if user is not None:
                print(f"User read: {user}")
                if user.get('role').lower() == 'student':
                    print(f"Submission History: {user.get('submission_history', [])}")
                    print(f"Grade History: {user.get('grade_history', [])}")
            else:
                print(f"No user found with ID: {user_id}")
        elif choice == '3':
            user_id = input("Enter user ID to update: ").strip()
            update_fields = {}
            name = input("Enter new name (leave blank to skip): ")
            if name: update_fields["name"] = name
            email = input("Enter new email (leave blank to skip): ")
            if email: update_fields["email"] = email
            role = input("Enter new role (leave blank to skip): ")
            if role: update_fields["role"] = role
            update_user(user_id, update_fields)
        elif choice == '4':
            user_id = input("Enter user ID to delete: ").strip()
            delete_user(user_id)
            print(f"User deleted with ID: {user_id}")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def course_menu():
    while True:
        print("\nCourse Menu:")
        print("1. Create Course")
        print("2. Read Course")
        print("3. Update Course")
        print("4. Delete Course")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            course_name = input("Enter course name: ")
            teacher_id = input("Enter teacher ID: ")
            assignments = []
            course_id = create_course(course_name, teacher_id, assignments)
            if course_id:
                print(f"Course created with ID: {course_id}")
        elif choice == '2':
            course_id = input("Enter course ID to read: ").strip()
            course = read_course(course_id)
            if course is not None:
                print(f"Course read: {course}")
            else:
                print(f"No course found with ID: {course_id}")
        elif choice == '3':
            course_id = input("Enter course ID to update: ").strip()
            update_fields = {}
            course_name = input("Enter new course name (leave blank to skip): ")
            if course_name: update_fields["courseName"] = course_name
            update_course(course_id, update_fields)
        elif choice == '4':
            course_id = input("Enter course ID to delete: ").strip()
            delete_course(course_id)
            print(f"Course deleted with ID: {course_id}")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def assignment_menu():
    while True:
        print("\nAssignment Menu:")
        print("1. Create Assignment")
        print("2. Read Assignment")
        print("3. Update Assignment")
        print("4. Delete Assignment")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            course_id = input("Enter course ID: ")
            title = input("Enter assignment title: ")
            description = input("Enter assignment description: ")
            due_date = input("Enter due date (YYYY-MM-DD): ")
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
            assignment_id = create_assignment(course_id, title, description, due_date)
            if assignment_id:
                print(f"Assignment created with ID: {assignment_id}")
        elif choice == '2':
            assignment_id = input("Enter assignment ID to read: ").strip()
            assignment = read_assignment(assignment_id)
            if assignment is not None:
                print(f"Assignment read: {assignment}")
            else:
                print(f"No assignment found with ID: {assignment_id}")
        elif choice == '3':
            assignment_id = input("Enter assignment ID to update: ").strip()
            update_fields = {}
            title = input("Enter new title (leave blank to skip): ")
            if title: update_fields["title"] = title
            update_assignment(assignment_id, update_fields)
        elif choice == '4':
            assignment_id = input("Enter assignment ID to delete: ").strip()
            delete_assignment(assignment_id)
            print(f"Assignment deleted with ID: {assignment_id}")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def submission_menu():
    while True:
        print("\nSubmission Menu:")
        print("1. Create Submission")
        print("2. Read Submission")
        print("3. Update Submission")
        print("4. Evaluate Submission")
        print("5. Delete Submission")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            assignment_id = input("Enter assignment ID: ")
            student_id = input("Enter student ID: ")
            submission_date = datetime.now()
            content = input("Enter submission content: ")
            submission_id = create_submission(assignment_id, student_id, submission_date, content)
            if submission_id:
                print(f"Submission created with ID: {submission_id}")
        elif choice == '2':
            submission_id = input("Enter submission ID to read: ").strip()
            submission = read_submission(submission_id)
            if submission is not None:
                print(f"Submission read: {submission}")
            else:
                print(f"No submission found with ID: {submission_id}")
        elif choice == '3':
            submission_id = input("Enter submission ID to update: ").strip()
            update_fields = {}
            content = input("Enter new content (leave blank to skip): ")
            if content: update_fields["content"] = content
            update_submission(submission_id, update_fields)
        elif choice == '4':
            submission_id = input("Enter submission ID to evaluate: ").strip()
            if not submission_id:
                print("Error: Submission ID cannot be empty")
                continue
            grade = input("Enter the evaluated grade: ")
            evaluate_submission(submission_id, grade)
            print(f"Submission evaluated with ID: {submission_id} and grade: {grade}")
        elif choice == '5':
            submission_id = input("Enter submission ID to delete: ").strip()
            delete_submission(submission_id)
            print(f"Submission deleted with ID: {submission_id}")
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

def feedback_menu():
    while True:
        print("\nFeedback Menu:")
        print("1. Create Feedback")
        print("2. Read Feedback")
        print("3. Update Feedback")
        print("4. Delete Feedback")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            submission_id = input("Enter submission ID: ")
            comments = input("Enter comments: ")
            suggestions = input("Enter suggestions: ")
            feedback_id = create_feedback(submission_id, comments, suggestions)
            if feedback_id:
                print(f"Feedback created with ID: {feedback_id}")
        elif choice == '2':
            feedback_id = input("Enter feedback ID to read: ").strip()
            feedback = read_feedback(feedback_id)
            if feedback is not None:
                print(f"Feedback read: {feedback}")
            else:
                print(f"No feedback found with ID: {feedback_id}")
        elif choice == '3':
            feedback_id = input("Enter feedback ID to update: ").strip()
            update_fields = {}
            comments = input("Enter new comments (leave blank to skip): ")
            if comments: update_fields["comments"] = comments
            update_feedback(feedback_id, update_fields)
        elif choice == '4':
            feedback_id = input("Enter feedback ID to delete: ").strip()
            delete_feedback(feedback_id)
            print(f"Feedback deleted with ID: {feedback_id}")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Main Menu
def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. User Operations")
        print("2. Course Operations")
        print("3. Assignment Operations")
        print("4. Submission Operations")
        print("5. Feedback Operations")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            user_menu()
        elif choice == '2':
            course_menu()
        elif choice == '3':
            assignment_menu()
        elif choice == '4':
            submission_menu()
        elif choice == '5':
            feedback_menu()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()

