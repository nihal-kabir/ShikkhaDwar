#!/usr/bin/env python3
"""
Script to check if quizzes are being saved to the database
"""
from app import app
from models import db, Quiz, Question, Course

def check_database():
    with app.app_context():
        print("=" * 60)
        print("DATABASE QUIZ CHECK")
        print("=" * 60)

        # Check database connection
        try:
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection: SUCCESS")
        except Exception as e:
            print(f"❌ Database connection: FAILED - {e}")
            return

        # Check total quizzes
        total_quizzes = Quiz.query.count()
        print(f"\n📊 Total quizzes in database: {total_quizzes}")

        if total_quizzes == 0:
            print("\n⚠️  No quizzes found in database!")
            print("\nPossible reasons:")
            print("  1. No quizzes have been created yet")
            print("  2. Database transactions are not committing")
            print("  3. Database was reset/dropped")
            return

        # List all quizzes
        print("\n" + "=" * 60)
        print("QUIZ DETAILS")
        print("=" * 60)

        quizzes = Quiz.query.all()
        for i, quiz in enumerate(quizzes, 1):
            course = Course.query.get(quiz.course_id)
            questions_count = Question.query.filter_by(quiz_id=quiz.id).count()

            print(f"\n{i}. {quiz.title}")
            print(f"   ID: {quiz.id}")
            print(f"   Course: {course.title if course else 'Unknown'}")
            print(f"   Published: {'✅ Yes' if quiz.is_published else '❌ No'}")
            print(f"   Questions: {questions_count}")
            print(f"   Time Limit: {quiz.time_limit} min")
            print(f"   Max Attempts: {quiz.max_attempts}")
            print(f"   Passing Score: {quiz.passing_score}%")
            print(f"   Description: {quiz.description or 'None'}")

        # Check published quizzes
        published_quizzes = Quiz.query.filter_by(is_published=True).count()
        print(f"\n📢 Published quizzes: {published_quizzes}")
        print(f"📝 Draft quizzes: {total_quizzes - published_quizzes}")

        # Check questions
        total_questions = Question.query.count()
        print(f"\n❓ Total questions across all quizzes: {total_questions}")

        print("\n" + "=" * 60)
        print("DIAGNOSIS:")
        print("=" * 60)

        if total_quizzes > 0:
            print("✅ Quizzes ARE being saved to the database")
            if published_quizzes == 0:
                print("⚠️  No quizzes are published - students won't see them")
                print("   → Instructors need to publish quizzes from the manage page")
            if total_questions == 0:
                print("⚠️  Quizzes have no questions - add questions to make them functional")

        print("\n" + "=" * 60)

if __name__ == '__main__':
    check_database()
