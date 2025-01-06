from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    dog_name = Column(String(100))
    photo = Column(String(255), nullable=True)

    courses_as_teacher = relationship('Course', back_populates='teacher')
    courses_as_student = relationship('CourseStudentAssociation', back_populates='student')
    homework_answers = relationship('HomeworkAnswer', back_populates='student')

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    teacher = relationship('User', back_populates='courses_as_teacher')
    students = relationship('CourseStudentAssociation', back_populates='course')
    assignments = relationship('Homework', back_populates='course')
    lessons = relationship('Lesson', back_populates='course')

class CourseStudentAssociation(Base):
    __tablename__ = 'course_student_associations'

    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True)

    course = relationship('Course', back_populates='students')
    student = relationship('User', back_populates='courses_as_student')

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    course = relationship('Course', back_populates='lessons')

class Homework(Base):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    description = Column(Text, nullable=False)
    max_grade = Column(Float, nullable=False)

    course = relationship('Course', back_populates='assignments')
    answers = relationship('HomeworkAnswer', back_populates='homework')

class HomeworkAnswer(Base):
    __tablename__ = 'homework_answers'

    id = Column(Integer, primary_key=True)
    homework_id = Column(Integer, ForeignKey('homeworks.id'), nullable=False, index=True)
    description = Column(Text, nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    grade = Column(Float, nullable=False)

    homework = relationship('Homework', back_populates='answers')
    student = relationship('User', back_populates='homework_answers')

