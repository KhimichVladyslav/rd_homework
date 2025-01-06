from flask import Flask, request, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, User, Course, CourseStudentAssociation, Lesson, Homework, HomeworkAnswer

app = Flask(__name__)

engine = create_engine('postgresql://postgres:pass@localhost/postgres')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']
        first_name = data['first_name']
        last_name = data['last_name']

        user = User(email=email, password=password, first_name=first_name, last_name=last_name)
        session.add(user)
        session.commit()

        return jsonify({'message': 'User registered successfully'}), 201
    return jsonify({'message': 'GET method not supported'}), 405


@app.route('/users', methods=['GET'])
def get_users():
    users = session.query(User).all()
    result = [{"id": user.id, "email": user.email, "first_name": user.first_name,
               "last_name": user.last_name, "dog_name": user.dog_name, "photo": user.photo} for user in users]
    return jsonify(result)


@app.route('/courses', methods=['GET'])
def get_courses():
    courses = session.query(Course).all()
    result = [{"id": course.id, "title": course.title, "description": course.description,
               "teacher_id": course.teacher_id} for course in courses]
    return jsonify(result)


@app.route('/courses/create', methods=['GET', 'POST'])
def create_course():
    if request.method == 'POST':
        data = request.get_json()
        title = data['title']
        teacher_id = data['teacher_id']
        student_ids = data['student_ids']

        course = Course(title=title, teacher_id=teacher_id, description=data.get('description', ''))
        session.add(course)
        session.commit()

        for student_id in student_ids:
            association = CourseStudentAssociation(course_id=course.id, student_id=student_id)
            session.add(association)

        session.commit()

        return jsonify({'message': 'Course created successfully'}), 201
    return jsonify({'message': 'GET method not supported'}), 405


@app.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = session.query(Course).filter(Course.id == course_id).first()
    if not course:
        return jsonify({'message': 'Course not found'}), 404

    students = session.query(User).join(CourseStudentAssociation).filter(CourseStudentAssociation.course_id == course_id).all()
    lessons = session.query(Lesson).filter(Lesson.course_id == course_id).all()
    homeworks = session.query(Homework).filter(Homework.course_id == course_id).all()

    result = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "teacher_id": course.teacher_id,
        "students": [{"id": student.id, "first_name": student.first_name, "last_name": student.last_name} for student in students],
        "lessons": [{"id": lesson.id, "title": lesson.title, "description": lesson.description} for lesson in lessons],
        "homeworks": [{"id": homework.id, "description": homework.description, "max_grade": homework.max_grade} for homework in homeworks],
    }
    return jsonify(result)


@app.route('/courses/<int:course_id>/lectures', methods=['GET', 'POST'])
def add_lecture(course_id):
    if request.method == 'POST':
        data = request.get_json()
        title = data['title']
        description = data['description']

        lesson = Lesson(course_id=course_id, title=title, description=description)
        session.add(lesson)
        session.commit()

        return jsonify({'message': 'Lecture added successfully'}), 201
    return jsonify({'message': 'GET method not supported'}), 405


@app.route('/courses/<int:course_id>/tasks', methods=['GET', 'POST'])
def add_task(course_id):
    if request.method == 'POST':
        data = request.get_json()
        description = data['description']
        max_grade = data['max_grade']

        homework = Homework(course_id=course_id, description=description, max_grade=max_grade)
        session.add(homework)
        session.commit()

        return jsonify({'message': 'Homework added successfully'}), 201
    return jsonify({'message': 'GET method not supported'}), 405


@app.route('/courses/<int:course_id>/tasks/<int:task_id>/answers', methods=['GET', 'POST'])
def add_answer(course_id, task_id):
    if request.method == 'POST':
        data = request.get_json()
        description = data['description']
        student_id = data['student_id']

        answer = HomeworkAnswer(homework_id=task_id, description=description, student_id=student_id, grade=None)
        session.add(answer)
        session.commit()

        return jsonify({'message': 'Answer added successfully'}), 201
    return jsonify({'message': 'GET method not supported'}), 405


@app.route('/courses/<int:course_id>/tasks/<int:task_id>/answers/<int:answer_id>/mark', methods=['GET', 'POST'])
def mark_answer(course_id, task_id, answer_id):
    if request.method == 'POST':
        data = request.get_json()
        grade = data['grade']
        teacher_id = data['teacher_id']

        answer = session.query(HomeworkAnswer).filter(HomeworkAnswer.id == answer_id).first()
        if not answer:
            return jsonify({'message': 'Answer not found'}), 404

        answer.grade = grade
        session.commit()

        return jsonify({'message': 'Answer marked successfully'}), 200
    return jsonify({'message': 'GET method not supported'}), 405


@app.route('/courses/<int:course_id>/rating', methods=['GET'])
def get_rating(course_id):
    students_with_grades = session.query(
        User.id, User.first_name, User.last_name, func.avg(HomeworkAnswer.grade).label('average_grade')
    ).join(HomeworkAnswer, HomeworkAnswer.student_id == User.id).join(Homework, Homework.id == HomeworkAnswer.homework_id) \
        .filter(Homework.course_id == course_id).group_by(User.id).order_by(func.avg(HomeworkAnswer.grade).desc()).all()

    result = [{"id": student.id, "first_name": student.first_name, "last_name": student.last_name, "average_grade": student.average_grade} for student in students_with_grades]
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
