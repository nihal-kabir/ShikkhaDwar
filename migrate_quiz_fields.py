"""
Database migration script to add new fields to the Quiz model
Run this script to add the missing columns to the existing quizzes table
"""

import os
import sys
import psycopg2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def migrate_quiz_fields():
    """Add new fields to the quizzes table"""
    try:
        config = Config()
        
        # Connect to the database
        connection = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        # List of new columns to add
        new_columns = [
            "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS instructions TEXT;",
            "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS passing_score INTEGER DEFAULT 70;",
            "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS randomize_questions BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS show_correct_answers BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE;"
        ]
        
        print("Starting migration to add new quiz fields...")
        
        for sql in new_columns:
            try:
                cursor.execute(sql)
                print(f"✓ Executed: {sql}")
            except Exception as e:
                print(f"✗ Error executing {sql}: {e}")
                
        connection.commit()
        print("Migration completed successfully!")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == '__main__':
    migrate_quiz_fields()