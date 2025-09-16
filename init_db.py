"""
Database initialization script for University LMS
Run this script to create the database and sample data
"""

import os
import sys
import pymysql
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User, Course, Lesson, Quiz, Question, Enrollment, Progress, Announcement
from werkzeug.security import generate_password_hash
import json

def test_mysql_connection():
    """Test MySQL connection and create database if needed"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='_03nihal.k'
        )
        cursor = connection.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS lms_db')
        cursor.execute('USE lms_db')
        connection.commit()
        connection.close()
        print("MySQL connection successful and database created!")
        return True
    except Exception as e:
        print(f"MySQL connection failed: {e}")
        print("Please ensure MySQL is running and credentials are correct.")
        return False

def create_sample_data():
    """Create sample data for testing"""
    
    # Create sample users
    admin = User(
        username='admin',
        email='admin@university.edu',
        password_hash=generate_password_hash('admin123'),
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    
    instructor1 = User(
        username='prof_smith',
        email='smith@university.edu',
        password_hash=generate_password_hash('password123'),
        first_name='John',
        last_name='Smith',
        role='instructor'
    )
    
    instructor2 = User(
        username='prof_jones',
        email='jones@university.edu',
        password_hash=generate_password_hash('password123'),
        first_name='Sarah',
        last_name='Jones',
        role='instructor'
    )
    
    student1 = User(
        username='student1',
        email='student1@university.edu',
        password_hash=generate_password_hash('password123'),
        first_name='Alice',
        last_name='Johnson',
        role='student'
    )
    
    student2 = User(
        username='student2',
        email='student2@university.edu',
        password_hash=generate_password_hash('password123'),
        first_name='Bob',
        last_name='Davis',
        role='student'
    )
    
    db.session.add_all([admin, instructor1, instructor2, student1, student2])
    db.session.commit()
    
    # Create sample courses
    course1 = Course(
        title='Introduction to Python Programming',
        description='Learn the fundamentals of Python programming including variables, functions, loops, and object-oriented programming. Perfect for beginners!',
        category='Computer Science',
        instructor_id=instructor1.id,
        is_published=True,
        duration_weeks=8
    )
    
    course2 = Course(
        title='Web Development with Flask',
        description='Build dynamic web applications using Flask framework. Learn about routing, templates, databases, and deployment.',
        category='Computer Science',
        instructor_id=instructor1.id,
        is_published=True,
        duration_weeks=10
    )
    
    course3 = Course(
        title='Data Structures and Algorithms',
        description='Comprehensive course covering fundamental data structures and algorithms essential for computer science.',
        category='Computer Science',
        instructor_id=instructor2.id,
        is_published=True,
        duration_weeks=12
    )
    
    course4 = Course(
        title='Business Analytics',
        description='Learn to analyze business data and make data-driven decisions using statistical methods and tools.',
        category='Business',
        instructor_id=instructor2.id,
        is_published=True,
        duration_weeks=6
    )
    
    db.session.add_all([course1, course2, course3, course4])
    db.session.commit()
    
    # Create sample lessons for Python course
    lessons_python = [
        {
            'title': 'Getting Started with Python',
            'content': '''
            <h3>Welcome to Python Programming!</h3>
            <p>Python is a versatile, high-level programming language known for its simplicity and readability.</p>
            
            <h4>What you'll learn:</h4>
            <ul>
                <li>Python syntax and basic concepts</li>
                <li>Variables and data types</li>
                <li>Basic input/output operations</li>
            </ul>
            
            <h4>Your First Python Program</h4>
            <pre><code>
print("Hello, World!")
name = input("What's your name? ")
print(f"Hello, {name}!")
            </code></pre>
            
            <p>This simple program demonstrates basic Python syntax and string formatting.</p>
            ''',
            'order_num': 1,
            'week_number': 1,
            'video_url': 'https://www.youtube.com/watch?v=8DvywoWv6fI'
        },
        {
            'title': 'Variables and Data Types',
            'content': '''
            <h3>Understanding Variables and Data Types</h3>
            <p>Variables are containers for storing data values. Python has several built-in data types.</p>
            
            <h4>Basic Data Types:</h4>
            <ul>
                <li><strong>Integer (int):</strong> Whole numbers like 5, -3, 42</li>
                <li><strong>Float:</strong> Decimal numbers like 3.14, -0.5</li>
                <li><strong>String (str):</strong> Text like "Hello", 'Python'</li>
                <li><strong>Boolean (bool):</strong> True or False values</li>
            </ul>
            
            <h4>Examples:</h4>
            <pre><code>
# Variables and data types
age = 25          # integer
height = 5.9      # float
name = "Alice"    # string
is_student = True # boolean

print(f"Name: {name}, Age: {age}, Height: {height}, Student: {is_student}")
            </code></pre>
            ''',
            'order_num': 2,
            'week_number': 1
        },
        {
            'title': 'Control Structures - If Statements',
            'content': '''
            <h3>Making Decisions with If Statements</h3>
            <p>Control structures allow your program to make decisions based on different conditions.</p>
            
            <h4>Basic If Statement:</h4>
            <pre><code>
age = 18

if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")
            </code></pre>
            
            <h4>Comparison Operators:</h4>
            <ul>
                <li><code>==</code> Equal to</li>
                <li><code>!=</code> Not equal to</li>
                <li><code>&gt;</code> Greater than</li>
                <li><code>&lt;</code> Less than</li>
                <li><code>&gt;=</code> Greater than or equal to</li>
                <li><code>&lt;=</code> Less than or equal to</li>
            </ul>
            ''',
            'order_num': 3,
            'week_number': 2
        },
        {
            'title': 'Loops - For and While',
            'content': '''
            <h3>Repeating Actions with Loops</h3>
            <p>Loops allow you to repeat code multiple times efficiently.</p>
            
            <h4>For Loops:</h4>
            <pre><code>
# Loop through a range of numbers
for i in range(5):
    print(f"Count: {i}")

# Loop through a list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(f"I like {fruit}")
            </code></pre>
            
            <h4>While Loops:</h4>
            <pre><code>
# While loop example
count = 0
while count < 5:
    print(f"Count is {count}")
    count += 1
            </code></pre>
            
            <p>Use for loops when you know how many times to repeat, and while loops for conditional repetition.</p>
            ''',
            'order_num': 4,
            'week_number': 2
        }
    ]
    
    for lesson_data in lessons_python:
        lesson = Lesson(
            title=lesson_data['title'],
            content=lesson_data['content'],
            video_url=lesson_data.get('video_url', ''),
            order_num=lesson_data['order_num'],
            course_id=course1.id,
            week_number=lesson_data['week_number']
        )
        db.session.add(lesson)
    
    db.session.commit()
    
    # Create sample quiz for Python course
    quiz1 = Quiz(
        title='Python Basics Quiz',
        description='Test your understanding of Python fundamentals',
        course_id=course1.id,
        quiz_type='lesson_quiz',
        time_limit=30,
        max_attempts=3
    )
    
    db.session.add(quiz1)
    db.session.commit()
    
    # Create sample questions
    questions = [
        {
            'question_text': 'Which of the following is the correct way to declare a variable in Python?',
            'question_type': 'mcq',
            'options': {
                'A': 'var name = "John"',
                'B': 'name = "John"',
                'C': 'string name = "John"',
                'D': 'declare name = "John"'
            },
            'correct_answer': 'B',
            'points': 2
        },
        {
            'question_text': 'Python is a case-sensitive programming language.',
            'question_type': 'true_false',
            'correct_answer': 'true',
            'points': 1
        },
        {
            'question_text': 'What will be the output of: print(5 > 3 and 2 < 4)?',
            'question_type': 'mcq',
            'options': {
                'A': 'True',
                'B': 'False',
                'C': 'Error',
                'D': 'None'
            },
            'correct_answer': 'A',
            'points': 2
        }
    ]
    
    for i, q_data in enumerate(questions):
        question = Question(
            quiz_id=quiz1.id,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            options=json.dumps(q_data.get('options')) if q_data.get('options') else None,
            correct_answer=q_data['correct_answer'],
            points=q_data['points'],
            order_num=i + 1
        )
        db.session.add(question)
    
    # Create sample enrollments
    enrollment1 = Enrollment(user_id=student1.id, course_id=course1.id)
    enrollment2 = Enrollment(user_id=student1.id, course_id=course2.id)
    enrollment3 = Enrollment(user_id=student2.id, course_id=course1.id)
    enrollment4 = Enrollment(user_id=student2.id, course_id=course3.id)
    
    db.session.add_all([enrollment1, enrollment2, enrollment3, enrollment4])
    
    # Create sample announcements
    announcement1 = Announcement(
        title='Welcome to Python Programming!',
        content='Welcome to our Python programming course! We\'ll cover all the fundamentals you need to get started with programming in Python.',
        course_id=course1.id,
        author_id=instructor1.id
    )
    
    announcement2 = Announcement(
        title='Assignment Due Next Week',
        content='Don\'t forget that your first programming assignment is due next Friday. Please submit it through the course portal.',
        course_id=course1.id,
        author_id=instructor1.id,
        is_urgent=True
    )
    
    db.session.add_all([announcement1, announcement2])
    
    db.session.commit()
    print("Sample data created successfully!")

def main():
    """Initialize the database"""
    # Test MySQL connection first
    if not test_mysql_connection():
        return
        
    with app.app_context():
        # Drop all tables
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create sample data
        print("Creating sample data...")
        create_sample_data()
        
        print("\nDatabase initialization complete!")
        print("\nSample login credentials:")
        print("Instructor: prof_smith / password123")
        print("Student: student1 / password123")
        print("Admin: admin / admin123")

if __name__ == '__main__':
    main()