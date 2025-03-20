from flask import Flask, request, jsonify, send_file  
from flask_cors import CORS  
import firebase_admin  
from firebase_admin import credentials, firestore  
from werkzeug.security import generate_password_hash, check_password_hash  
import pytesseract  
from PIL import Image  
import matplotlib.pyplot as plt  
import logging  
import os  
import requests  
from datetime import datetime  
import io  

# Initialize Flask App  
app = Flask(__name__)  
CORS(app)  

# Set the path for Tesseract (modify if necessary for your OS)  
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  

# Initialize Firebase  
if not firebase_admin._apps:  
    cred = credentials.Certificate("/etc/secrets/serviceAccountkey.json")  # Update the path  
    firebase_admin.initialize_app(cred)  

db = firestore.client()  

# Configure Logging  
logging.basicConfig(level=logging.INFO) 
import os


# API Endpoints
from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/registerfac", methods=["POST","GET"])
def registerFac():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    passwd = data.get("password")
    
    if not (name and email and passwd):
        return jsonify({"error": "Missing fields"}), 400
    
    user = {
        "name": name,
        "email": email,
        "role": "Faculty",
        "courseIds": [],
        "pass": generate_password_hash(passwd, method='pbkdf2:sha256')  # Change here
    }
    
    try:
        doc_ref = db.collection('users').add(user)
        return jsonify({"message": "User  registered", "id": doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/registerstd", methods=["POST","GET"])
def registerstd():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    passwd = data.get("password")
    
    if not (name and email and passwd):
        return jsonify({"error": "Missing fields"}), 400
    
    user = {
        "name": name,
        "email": email,
        "role": "Student",
        "courseIds": [],
        "pass": generate_password_hash(passwd, method='pbkdf2:sha256')  # Change here
    }
    
    try:
        doc_ref = db.collection('users').add(user)
        return jsonify({"message": "User  registered", "id": doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/login", methods=["POST"])  
def login():  
    data = request.json  
    email = data.get("email")  
    password = data.get("password")  # Get password from request  

    if not (email and password):  
        return jsonify({"error": "Email and password required"}), 400  

    # Query Firestore to find the user by email  
    users_ref = db.collection('users').where("email", "==", email).stream()  
    user_doc = next(users_ref, None)  

    if not user_doc:  
        return jsonify({"error": "User  not found"}), 404  

    user = user_doc.to_dict()  

    # Check password  
    if not check_password_hash(user["pass"], password):  # This remains unchanged
        return jsonify({"error": "Incorrect password"}), 401  
        
@app.route("/get-courses", methods=["POST"])
def get_courses():
    data = request.json
    course_ids = data.get("courseIds")

    if not course_ids:
        return jsonify({"error": "No course IDs provided"}), 400

    try:
        courses = []
        for course_id in course_ids:
            course_ref = db.collection("courses").document(course_id).get()
            if course_ref.exists:
                courses.append(course_ref.to_dict())

        return jsonify({"courses": courses}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/add-course", methods=["POST"])
def add_course():
    data = request.json
    course_code = data.get("code")
    course_name = data.get("name")
    faculty_email = data.get("facultyEmail")

    if not (course_code and course_name and faculty_email):
        return jsonify({"error": "Missing fields"}), 400

    try:
        # ✅ 1. Add course to Firestore "courses" collection
        db.collection("courses").document(course_code).set({
            "code": course_code,
            "name": course_name,
            "facultyEmail": faculty_email
        })

        return jsonify({"message": "Course added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update-faculty-courses", methods=["POST"])
def update_faculty_courses():
    data = request.json
    email = data.get("email")
    course_ids = data.get("courseIds")

    if not (email and course_ids):
        return jsonify({"error": "Missing fields"}), 400

    try:
        # ✅ 2. Update faculty's course list in Firestore
        users_ref = db.collection("users").where("email", "==", email).stream()
        user_doc = next(users_ref, None)

        if user_doc:
            user_ref = db.collection("users").document(user_doc.id)
            user_ref.update({"courseIds": course_ids})
            return jsonify({"message": "Faculty courses updated"}), 200

        return jsonify({"error": "Faculty not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
import uuid
logging.basicConfig(level=logging.INFO)

# ✅ API: Add a new question
@app.route("/add-question", methods=["POST"])
def add_question():
    data = request.json
    course_id = data.get("courseId")
    question_text = data.get("question")

    if not course_id or not question_text:
        return jsonify({"error": "Missing courseId or question"}), 400

    try:
        question_id = str(uuid.uuid4())  # ✅ Generate unique questionId

        # ✅ Store question in Firestore
        db.collection("questions").document(question_id).set({
            "questionId": question_id,
            "courseId": course_id,
            "question": question_text,
            "answerKey": "",  # ✅ Placeholder for extracted text
            "submissions": []
        })

        logging.info(f"Added question {question_id} for course {course_id}")

        return jsonify({"message": "Question added", "questionId": question_id}), 201
    except Exception as e:
        logging.error(f"Error adding question: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ API: Get questions for a course
@app.route("/get-questions", methods=["POST"])
def get_questions():
    data = request.json
    course_id = data.get("courseId")

    if not course_id:
        return jsonify({"error": "Missing course ID"}), 400

    try:
        questions_ref = db.collection("questions").where("courseId", "==", course_id).stream()
        questions = [q.to_dict() for q in questions_ref]

        logging.info(f"Fetched {len(questions)} questions for course {course_id}")

        return jsonify({"questions": questions}), 200
    except Exception as e:
        logging.error(f"Error fetching questions: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ API: Upload answer key (image) and extract text
@app.route("/upload-answer-key", methods=["POST"])
def upload_answer_key():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    question_id = request.form.get("questionId")

    if not question_id:
        return jsonify({"error": "Missing question ID"}), 400

    try:
        # ✅ Convert image to text using Tesseract
        image = Image.open(io.BytesIO(file.read()))

        # ✅ Convert image to grayscale (improves OCR accuracy)
        image = image.convert("L")  
        
        extracted_text = pytesseract.image_to_string(image)

        # ✅ Store extracted text in Firestore
        question_ref = db.collection("questions").document(question_id)
        question_ref.update({"answerKey": extracted_text})

        logging.info(f"Uploaded answer key for question {question_id}, extracted text: {extracted_text}")

        return jsonify({
            "message": "Answer key uploaded successfully",
            "extractedText": extracted_text
        }), 201
    except Exception as e:
        logging.error(f"Error processing answer key: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ API: Fetch all courses & student-enrolled courses
@app.route("/get-student-courses", methods=["POST"])
def get_student_courses1():
    data = request.json
    student_email = data.get("email")

    if not student_email:
        return jsonify({"error": "Missing student email"}), 400

    try:
        # ✅ Get student data
        users_ref = db.collection("users").where("email", "==", student_email).stream()
        student_doc = next(users_ref, None)

        if not student_doc:
            return jsonify({"error": "Student not found"}), 404

        student_data = student_doc.to_dict()
        enrolled_course_ids = student_data.get("courseIds", [])

        # ✅ Fetch all courses
        courses_ref = db.collection("courses").stream()
        all_courses = [course.to_dict() for course in courses_ref]

        return jsonify({
            "enrolledCourses": [course for course in all_courses if course["code"] in enrolled_course_ids],
            "allCourses": all_courses
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ API: Fetch questions for a course
@app.route("/get-course-questions", methods=["POST"])
def get_course_questions():
    data = request.json
    course_id = data.get("courseId")

    if not course_id:
        return jsonify({"error": "Missing course ID"}), 400

    try:
        questions_ref = db.collection("questions").where("courseId", "==", course_id).stream()
        questions = [q.to_dict() for q in questions_ref]
        return jsonify({"questions": questions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ API: Submit student's answer
@app.route("/submit-answer", methods=["POST"])
def submit_answer():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    student_email = request.form.get("studentEmail")
    question_id = request.form.get("questionId")

    if not (student_email and question_id):
        return jsonify({"error": "Missing fields"}), 400

    try:
        submission_id = str(uuid.uuid4())
        submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ Store submission in Firestore
        db.collection("submissions").document(submission_id).set({
            "submissionId": submission_id,
            "questionId": question_id,
            "studentEmail": student_email,
            "fileName": file.filename,
            "submissionTime": submission_time,
            "grade": None  # Grading will be done later
        })

        return jsonify({"message": "Submission successful", "submissionId": submission_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ API: Fetch student submissions & grades
@app.route("/get-submissions", methods=["POST"])
def get_submissions():
    data = request.json
    student_email = data.get("email")

    if not student_email:
        return jsonify({"error": "Missing student email"}), 400

    try:
        submissions_ref = db.collection("submissions").where("studentEmail", "==", student_email).stream()
        submissions = [sub.to_dict() for sub in submissions_ref]
        return jsonify({"submissions": submissions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ✅ API: Enroll student in a course
# ✅ API: Fetch enrolled & all available courses for a student
@app.route("/generate-progress-chart", methods=["POST"])
def generate_progress_chart():
    data = request.json
    student_email = data.get("studentEmail")

    if not student_email:
        return jsonify({"error": "Missing student email"}), 400

    try:
        # ✅ Fetch student scores over time
        submissions_ref = db.collection("submissions").where("studentEmail", "==", student_email).stream()
        scores = []
        timestamps = []

        for sub in submissions_ref:
            sub_data = sub.to_dict()
            raw_score = sub_data.get("score", 0)
            raw_timestamp = sub_data.get("submissionTime", "0")  # Example: "2025-03-12 14:30:00"

            try:
                # ✅ Convert score to float
                score = float(raw_score) if isinstance(raw_score, (int, float, str)) and str(raw_score).replace('.', '', 1).isdigit() else 0
            except ValueError:
                score = 0

            try:
                # ✅ Convert timestamp to a numerical value (epoch time for sorting)
                from datetime import datetime
                timestamp = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S").timestamp()
            except ValueError:
                timestamp = 0  # Default if conversion fails

            scores.append(score)
            timestamps.append(timestamp)

        if not scores or not timestamps:
            return jsonify({"message": "No progress data available", "progressChart": None}), 200

        # ✅ Sort data by timestamp (ensures correct order in the graph)
        sorted_data = sorted(zip(timestamps, scores))
        timestamps, scores = zip(*sorted_data)

        # ✅ Convert timestamps to readable dates for X-axis
        from datetime import datetime
        formatted_dates = [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in timestamps]

        # ✅ Generate and save the progress chart
        os.makedirs("progress_charts", exist_ok=True)
        chart_path = f"progress_charts/progress_{student_email}.png"

        plt.figure(figsize=(10, 6))
        plt.plot(sorted(formatted_dates), sorted(scores), marker="o", linestyle="-", color="blue")  # ✅ Ensures numerical X-axis
        plt.xlabel("Date")
        plt.ylabel("Position")
        plt.title(f"Progress Chart for {student_email}")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.savefig(chart_path)
        plt.close()

        return jsonify({"message": "Progress chart generated", "progressChartUrl": f"/get-progress-chart/{student_email}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-progress-chart/<student_email>")
def get_progress_chart(student_email):
    chart_path = f"charts/progress_chart_{student_email}.png"
    if os.path.exists(chart_path):
        return send_file(chart_path, mimetype="image/png")
    return jsonify({"error": "Chart not found"}), 404 
import traceback
import cv2
import time


proctoring_results = {}  # Stores warnings for each user
proctoring_threads = {}  # Track running proctoring threads

@app.route("/start-proctoring", methods=["POST"])
def start_proctoring():
    """Starts proctoring and tracks warnings if a face is not detected."""
    data = request.json
    student_email = data.get("studentEmail")
    
    if not student_email:
        return jsonify({"error": "Missing student email"}), 400

    def proctor():
        """Checks if the user is looking at the screen using face detection."""
        warnings = 0
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            proctoring_results[student_email] = {"status": "error", "warnings": 3}
            return

        face_not_detected_time = 0  # Track time without a face detected

        while warnings < 3:
            if student_email in proctoring_threads and not proctoring_threads[student_email]:
                break  # ✅ Stop if submission has been made

            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

            if len(faces) == 0:
                if face_not_detected_time == 0:
                    face_not_detected_time = time.time()  # Start timer when face disappears

                elif time.time() - face_not_detected_time >= 3:  # Face missing for 3 seconds
                    warnings += 1
                    print(f"⚠️ Warning {warnings}/3: Face not detected for 3 seconds!")
                    face_not_detected_time = 0  # Reset timer
            else:
                face_not_detected_time = 0  # Reset timer when face is detected

            proctoring_results[student_email] = {"status": "active", "warnings": warnings}

            if warnings >= 3:
                proctoring_results[student_email] = {"status": "failed", "warnings": 3}
                break

            time.sleep(1)  # ✅ Reduce CPU load

        cap.release()

    # ✅ Start proctoring in a background thread
    proctoring_threads[student_email] = True
    thread = threading.Thread(target=proctor, daemon=True)
    thread.start()

    return jsonify({"message": "Proctoring started. Type your answer and submit."}), 200

@app.route("/get-warnings", methods=["GET"])
def get_warnings():
    """Returns the warning count for a student."""
    student_email = request.args.get("studentEmail")
    if not student_email:
        return jsonify({"error": "Missing student email"}), 400

    warnings = proctoring_results.get(student_email, {}).get("warnings", 0)
    return jsonify({"warnings": warnings})
@app.route("/submit-answer1", methods=["POST"])
def submit_answer1():
    """Receives the user answer, stops proctoring, and sends it to `/evaluate-answer`."""
    data = request.json
    student_email = data.get("studentEmail")
    question_id = data.get("questionId")
    ques = data.get("ques")
    key = data.get("key")
    user_answer = data.get("answer")

    if not (student_email and question_id and ques and key and user_answer):
        return jsonify({"error": "Missing required fields"}), 400

    # ✅ Stop the proctoring thread when user submits
    proctoring_threads[student_email] = False

    try:
        response = requests.post("http://127.0.0.1:5000/evaluate-answer", json={
            "studentEmail": student_email,
            "questionId": question_id,
            "ques": ques,
            "key": key,
            "answer": user_answer
        })

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ API: Enroll student in a course
@app.route("/enroll-course", methods=["POST"])
def enroll_course():
    data = request.json
    student_email = data.get("email")
    course_id = data.get("courseId")

    if not (student_email and course_id):
        return jsonify({"error": "Missing student email or course ID"}), 400

    try:
        users_ref = db.collection("users").where("email", "==", student_email).stream()
        student_doc = next(users_ref, None)

        if not student_doc:
            return jsonify({"error": "Student not found"}), 404

        student_ref = db.collection("users").document(student_doc.id)
        student_data = student_doc.to_dict()
        enrolled_courses = student_data.get("courseIds", [])

        if course_id in enrolled_courses:
            return jsonify({"message": "Already enrolled"}), 200

        enrolled_courses.append(course_id)
        student_ref.update({"courseIds": enrolled_courses})

        return jsonify({"message": "Enrollment successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
from datetime import datetime
import threading

@app.route("/evaluate-answer", methods=["POST"])
def evaluate_answer():
    """Starts proctoring and evaluates the submitted answer asynchronously."""
    try:
        # ✅ Ensure JSON content type
        if not request.is_json:
            return jsonify({"error": "Invalid content type. Use 'application/json'."}), 415
        
        data = request.get_json()  # ✅ Correctly parse JSON request

        question_id = data.get("questionId")
        student_email = data.get("studentEmail")
        ques = data.get("ques")
        key = data.get("key")

        if not (question_id and student_email and ques and key):
            return jsonify({"error": "Missing required fields"}), 400

        def process_result(submitted_text):
            """Processes the extracted text after proctoring is complete."""
            extracted_text = submitted_text.strip()
            print(f"Extracted Text: {extracted_text}")

            # ✅ Evaluate the answer
            file, mes, score ="","",9.5 #return_score(ques + '\n\n' + extracted_text, key)

            # ✅ Store submission in Firestore
            submission_id = f"{student_email}_{question_id}_{int(datetime.now().timestamp())}"

            db.collection("submissions").document(submission_id).set({
                "submissionId": submission_id,
                "questionId": question_id,
                "studentEmail": student_email,
                "score": score,
                "submissionTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "scoreText": mes,
                "file": file
            })

            print(f"✅ Submission {submission_id} saved with score: {score}")
            return file,mes,score

        file,mes,score =process_result(data.get("answer"))

        return jsonify({"score": score,"scoreText": mes,"file":file }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/add-comment", methods=["POST"])
def add_comment():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    content = data.get("content")

    if not name or not email or not content:
        return jsonify({"error": "Missing data"}), 400

    try:
        # Save the comment to Firestore under a "comments" collection
        db.collection("comments").add({
            "name": name,
            "email": email,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        return jsonify({"message": "Comment added successfully"}), 201
    except Exception as e:
        error_trace = traceback.format_exc()
        return jsonify({"error": str(e), "traceback": error_trace}), 500
    
@app.route("/get-comments", methods=["POST"])
def get_comments():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Missing email"}), 400

    try:
        # Retrieve comments from Firestore where email matches
        comments_ref = db.collection("comments").stream()
        comments = [{"name": doc.to_dict()["name"], "comment": doc.to_dict()["content"]} for doc in comments_ref]

        return jsonify(comments), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/get-highest-marks", methods=["POST"])
def get_highest_marks():
    data = request.json
    course_id = data.get("courseId")

    if not course_id:
        return jsonify({"error": "Missing course ID"}), 400

    try:
        questions_ref = db.collection("questions").where("courseId", "==", course_id).stream()
        question_ids = [q.id for q in questions_ref]  # Extract question IDs
        print(question_ids)
        if not question_ids:
            return jsonify({"message": "No questions found for this course", "submissions": []}), 200

        # Step 2: Retrieve submissions where questionId is in the extracted question_ids list
        submissions_ref = db.collection("submissions").where("questionId", "in", question_ids).stream()
        student_scores = {}
        print(submissions_ref)

        for sub in submissions_ref:
            sub_data = sub.to_dict()
            print(sub_data)
            student = sub_data["studentEmail"]
            score = sub_data.get("score", 0)
            print(score)
            try:
                float(student_scores[student])
                if student in student_scores:
                    student_scores[student] = max(float(student_scores[student]), score)
                else:
                    student_scores[student] = score
            except :
                continue

        print(student_scores)
        return jsonify({"highestScores": student_scores}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port)
