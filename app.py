from flask import Flask, redirect
import psycopg2

app = Flask(__name__)

app.secret_key = 'key'

DB_SETTINGS = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '',
    'host': 'localhost',
    'port': 5454
}


def get_db_connection():
    return psycopg2.connect(**DB_SETTINGS)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO Person (Email, Password, FirstName, LastName) 
                           VALUES (%s, %s, %s, %s) RETURNING Id;""",
                        (email, password, first_name, last_name)
                    )
                    user_id = cur.fetchone()[0]
                    conn.commit()
                    return jsonify({'id': user_id, 'message': 'Registration successful'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return '''
        <form method="POST">
            <label for="email">Email:</label>
            <input type="email" name="email" required><br>
            <label for="password">Password:</label>
            <input type="password" name="password" required><br>
            <label for="first_name">First Name:</label>
            <input type="text" name="first_name" required><br>
            <label for="last_name">Last Name:</label>
            <input type="text" name="last_name" required><br>
            <button type="submit">Register</button>
        </form>
    ''', 200


@app.route('/users', methods=['GET'])
def get_users():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Person;")
            users = cur.fetchall()
            return jsonify(users)


@app.route('/courses', methods=['GET'])
def get_courses():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Course;")
            courses = cur.fetchall()
            return jsonify(courses)


from flask import request, jsonify, flash


@app.route('/courses/create', methods=['GET', 'POST'])
def create_course():
    if request.method == 'GET':
        return '''
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Create Course</title>
            </head>
            <body>
                <h1>Create a New Course</h1>
                <form method="POST">
                    <label for="name">Course Name:</label>
                    <input type="text" id="name" name="name" required><br><br>

                    <label for="teacher_id">Teacher ID:</label>
                    <input type="number" id="teacher_id" name="teacher_id" required><br><br>

                    <label for="student_ids">List of Student IDs (comma separated):</label>
                    <input type="text" id="student_ids" name="student_ids" required><br><br>

                    <button type="submit">Create Course</button>
                </form>
            </body>
            </html>
        '''

    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        teacher_id = data.get('teacher_id')
        student_ids = data.get('student_ids').split(',')

        if not name or not teacher_id or not student_ids:
            flash('Please fill in all fields!', 'error')
            return redirect('/courses/create')

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO Course (Name, TeacherId) 
                           VALUES (%s, %s) RETURNING Id;""",
                        (name, teacher_id)
                    )
                    course_id = cur.fetchone()[0]

                    for student_id in student_ids:
                        cur.execute(
                            "INSERT INTO Course_Student (CourseId, StudentId) VALUES (%s, %s);",
                            (course_id, student_id.strip())
                        )

                    conn.commit()
                    flash(f'Course "{name}" created successfully!', 'success')
                    return jsonify({'message': 'Course created successfully', 'id': course_id}), 201

        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect('/courses/create')

    return jsonify({'message': 'Invalid request method'}), 405


@app.route('/courses/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Course WHERE Id = %s;", (course_id,))
            course = cur.fetchone()
            cur.execute("SELECT StudentId FROM Course_Student WHERE CourseId = %s;", (course_id,))
            students = cur.fetchall()
            cur.execute("SELECT * FROM Lesson WHERE CourseId = %s;", (course_id,))
            lessons = cur.fetchall()
            cur.execute("SELECT * FROM Homework WHERE CourseId = %s;", (course_id,))
            homeworks = cur.fetchall()
            return jsonify({
                'course': course,
                'students': students,
                'lessons': lessons,
                'homeworks': homeworks
            })


@app.route('/courses/<int:course_id>/lectures', methods=['GET', 'POST'])
def manage_lectures(course_id):
    if request.method == 'GET':
        return '''
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Add Lecture</title>
            </head>
            <body>
                <h1>Add a Lecture to Course ID {{ course_id }}</h1>
                <form method="POST">
                    <label for="name">Lecture Name:</label>
                    <input type="text" id="name" name="name" required><br><br>

                    <label for="description">Description:</label>
                    <textarea id="description" name="description" required></textarea><br><br>

                    <button type="submit">Add Lecture</button>
                </form>
            </body>
            </html>
        '''.replace("{{ course_id }}", str(course_id))

    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        description = data.get('description')

        if not name or not description:
            return jsonify({'message': 'Both name and description are required!'}), 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO Lesson (CourseId, Name, Description) 
                           VALUES (%s, %s, %s) RETURNING Id;""",
                        (course_id, name, description)
                    )
                    lecture_id = cur.fetchone()[0]
                    conn.commit()
                    return jsonify({'message': 'Lecture added successfully', 'id': lecture_id}), 201

        except Exception as e:
            return jsonify({'message': f'An error occurred: {e}'}), 500

    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/courses/<int:course_id>/tasks', methods=['GET', 'POST'])
def manage_homework(course_id):
    if request.method == 'GET':
        return '''
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Add Homework</title>
            </head>
            <body>
                <h1>Add Homework to Course ID {{ course_id }}</h1>
                <form method="POST">
                    <label for="description">Description:</label>
                    <textarea id="description" name="description" required></textarea><br><br>

                    <button type="submit">Add Homework</button>
                </form>
            </body>
            </html>
        '''.replace("{{ course_id }}", str(course_id))

    if request.method == 'POST':
        data = request.form
        description = data.get('description')

        if not description:
            return jsonify({'message': 'Description is required!'}), 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Provide a default value for MaxGrade
                    cur.execute(
                        """INSERT INTO Homework (CourseId, Description, MaxGrade) 
                           VALUES (%s, %s, %s) RETURNING Id;""",
                        (course_id, description, 0)  # Default value for MaxGrade is 0
                    )
                    homework_id = cur.fetchone()[0]
                    conn.commit()
                    return jsonify({'message': 'Homework added successfully', 'id': homework_id}), 201

        except Exception as e:
            return jsonify({'message': f'An error occurred: {e}'}), 500

    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/courses/<int:course_id>/tasks/<int:task_id>/answers', methods=['GET', 'POST'])
def manage_answers(course_id, task_id):
    if request.method == 'GET':
        return '''
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Add Answer</title>
            </head>
            <body>
                <h1>Submit Answer for Homework Task ID {{ task_id }} in Course ID {{ course_id }}</h1>
                <form method="POST">
                    <label for="description">Description:</label>
                    <textarea id="description" name="description" required></textarea><br><br>

                    <label for="student_id">Student ID:</label>
                    <input type="number" id="student_id" name="student_id" required><br><br>

                    <button type="submit">Submit Answer</button>
                </form>
            </body>
            </html>
        '''.replace("{{ course_id }}", str(course_id)).replace("{{ task_id }}", str(task_id))

    if request.method == 'POST':
        data = request.form
        description = data.get('description')
        student_id = data.get('student_id')

        if not description or not student_id:
            return jsonify({'message': 'Description and Student ID are required!'}), 400

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT Id FROM Homework WHERE Id = %s", (task_id,))
                task_exists = cur.fetchone()

                if not task_exists:
                    return jsonify({'message': 'Task not found in Homework table!'}), 404

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO Homework_Response (HomeworkId, Description, StudentId) 
                           VALUES (%s, %s, %s) RETURNING Id;""",
                        (task_id, description, student_id)
                    )
                    answer_id = cur.fetchone()[0]
                    conn.commit()
                    return jsonify({'message': 'Answer submitted successfully', 'id': answer_id}), 201

        except Exception as e:
            return jsonify({'message': f'An error occurred: {e}'}), 500

    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/courses/<int:course_id>/tasks/<int:task_id>/answers/<int:answer_id>/mark', methods=['GET', 'POST'])
def mark_answer(course_id, task_id, answer_id):
    if request.method == 'GET':
        # Return a simple HTML form for grading the answer
        return '''
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Grade Answer</title>
            </head>
            <body>
                <h1>Grade Answer for Answer ID {{ answer_id }} on Task ID {{ task_id }} in Course ID {{ course_id }}</h1>
                <form method="POST">
                    <label for="date">Date:</label>
                    <input type="date" id="date" name="date" required><br><br>

                    <label for="grade">Grade:</label>
                    <input type="number" id="grade" name="grade" required><br><br>

                    <label for="teacher_id">Teacher ID:</label>
                    <input type="number" id="teacher_id" name="teacher_id" required><br><br>

                    <button type="submit">Submit Grade</button>
                </form>
            </body>
            </html>
        '''.replace("{{ course_id }}", str(course_id)).replace("{{ task_id }}", str(task_id)).replace("{{ answer_id }}", str(answer_id))

    if request.method == 'POST':
        data = request.form
        grade_date = data.get('date')
        grade_value = data.get('grade')
        teacher_id = data.get('teacher_id')

        # Check if all required fields are provided
        if not grade_date or not grade_value or not teacher_id:
            return jsonify({'message': 'Date, grade, and teacher ID are required!'}), 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Check if the answer_id exists in the Homework_Response table
                    cur.execute("SELECT 1 FROM Homework_Response WHERE Id = %s;", (answer_id,))
                    if cur.fetchone() is None:
                        return jsonify({'message': 'Answer ID not found in Homework_Response table'}), 404

                    # Insert grading data into Homework_Grade table
                    cur.execute(
                        """INSERT INTO Homework_Grade (ResponseId, Date, Grade, TeacherId) 
                           VALUES (%s, %s, %s, %s) RETURNING Id;""",
                        (answer_id, grade_date, grade_value, teacher_id)
                    )
                    grade_id = cur.fetchone()[0]
                    conn.commit()
                    return jsonify({'message': 'Grade submitted successfully', 'id': grade_id}), 201

        except Exception as e:
            return jsonify({'message': f'An error occurred: {e}'}), 500

    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/courses/<int:course_id>/rating', methods=['GET'])
def course_rating(course_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    s.Id AS StudentId, 
                    s.FirstName || ' ' || s.LastName AS StudentName,
                    AVG(g.Grade) AS AverageGrade
                FROM Person s
                JOIN Homework_Response r ON r.StudentId = s.Id
                JOIN Homework_Grade g ON g.ResponseId = r.Id
                WHERE r.HomeworkId IN (SELECT Id FROM Homework WHERE CourseId = %s)
                GROUP BY s.Id, StudentName
                ORDER BY AverageGrade DESC;
                """,
                (course_id,)
            )
            ratings = cur.fetchall()
            return jsonify(ratings)


if __name__ == '__main__':
    app.run(debug=True)
