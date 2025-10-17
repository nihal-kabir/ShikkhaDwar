# Course Cloning Feature - Testing Guide

## Feature Overview

The course cloning feature allows instructors to duplicate an existing course with all its content, making it easy to create course templates or reuse course materials.

## What Gets Cloned

✅ **Copied:**
- Course metadata (title with "(Copy)" suffix, description, category, duration)
- All lessons (with content, video URLs, order, week numbers)
- All resources attached to lessons (with file references)
- All quizzes (with settings like time limit, attempts, passing score)
- All questions within quizzes (with options, correct answers, points)
- Embedded quiz associations (quizzes linked to specific lessons)

❌ **Not Copied:**
- Student enrollments
- Quiz attempts and grades
- Progress records
- Announcements (optional - currently commented out)

## New Course Settings

The cloned course will:
- Have "(Copy)" appended to the title
- Be set to **unpublished** status
- All quizzes will be **unpublished**
- Belong to the same instructor who cloned it

## Testing Steps

### 1. Prerequisites
- You must be logged in as an instructor
- You must have at least one course with content

### 2. Access the Clone Feature
1. Navigate to Instructor Dashboard
2. Select a course to manage
3. Click "Manage Course"
4. Look for the "Clone Course" button in the top-right corner

### 3. Clone a Course
1. Click the "Clone Course" button
2. Review the confirmation modal showing what will be copied
3. Click "Clone Course" to confirm
4. You should see a success message
5. You'll be redirected to the manage page of the newly cloned course

### 4. Verify the Cloned Course
Check that the following were copied correctly:

**Course Information:**
- [ ] Title has "(Copy)" appended
- [ ] Description is identical
- [ ] Category matches
- [ ] Duration matches
- [ ] Status is "Draft" (unpublished)

**Lessons:**
- [ ] All lessons are present
- [ ] Lesson order is preserved (order_num)
- [ ] Week numbers match
- [ ] Content (HTML) is identical
- [ ] Video URLs are copied
- [ ] No lesson IDs match the original (new IDs created)

**Resources:**
- [ ] All resources attached to lessons are present
- [ ] Resource titles match
- [ ] File paths point to the same files
- [ ] Resources are associated with correct lessons in cloned course

**Quizzes:**
- [ ] All quizzes are present
- [ ] Quiz settings match (time limit, attempts, passing score)
- [ ] All quizzes are unpublished
- [ ] Quiz types match (lesson_quiz, assignment, exam)
- [ ] Embedded quiz associations preserved (if quiz was in lesson 1, it's still in lesson 1 of cloned course)

**Questions:**
- [ ] All questions for each quiz are present
- [ ] Question text is identical
- [ ] Question types match (MCQ, True/False, etc.)
- [ ] Options (JSON) are copied correctly
- [ ] Correct answers are preserved
- [ ] Point values match
- [ ] Question order is preserved

**Not Copied (Verify these are empty):**
- [ ] No student enrollments in cloned course
- [ ] No quiz attempts
- [ ] No grades
- [ ] No progress records

## Manual Testing Checklist

### Test Case 1: Clone Simple Course
1. Create a simple course with:
   - 3 lessons
   - 1 quiz with 3 questions
   - 1 resource on a lesson
2. Clone the course
3. Verify all content matches

**Expected Result:** ✅ New course created with all content, title has "(Copy)", status is unpublished

### Test Case 2: Clone Complex Course
1. Clone a course with:
   - 10+ lessons
   - Multiple quizzes
   - Embedded quizzes in lessons
   - Multiple resources per lesson
2. Verify data integrity

**Expected Result:** ✅ All relationships preserved, embedded quizzes still linked to correct lessons

### Test Case 3: Security Check
1. Try to clone a course you don't own (if possible)
2. Verify access is denied

**Expected Result:** ✅ Error message: "Access denied" and redirect to dashboard

### Test Case 4: Clone and Modify
1. Clone a course
2. Modify the cloned course (add lessons, edit quizzes)
3. Verify original course is unchanged

**Expected Result:** ✅ Original course remains intact, only cloned course is modified

### Test Case 5: Publish Cloned Course
1. Clone a published course
2. Verify cloned course is unpublished
3. Publish the cloned course
4. Verify both courses now show in catalog

**Expected Result:** ✅ Both courses are independent, both can be published

## Error Scenarios to Test

### Scenario 1: Database Error During Cloning
- If cloning fails, verify rollback occurs
- Original course should remain unchanged

### Scenario 2: Empty Course
- Clone a course with no lessons or quizzes
- Should create an empty clone successfully

### Scenario 3: Large Course
- Clone a course with 50+ lessons and 20+ quizzes
- Monitor performance and completion time

## Code Review Checklist

✅ **Implementation Review:**
- [x] Route uses POST method (prevents accidental cloning)
- [x] @instructor_required decorator applied
- [x] Ownership verification before cloning
- [x] Transaction management (db.session.commit/rollback)
- [x] Error handling with try/except
- [x] Flash messages for user feedback
- [x] Proper redirects after success/failure
- [x] db.session.flush() used to get new IDs before relationships
- [x] Lesson ID mapping for embedded quiz associations
- [x] All model fields copied appropriately

✅ **UI Review:**
- [x] Clone button visible on manage course page
- [x] Confirmation modal prevents accidental clicks
- [x] Modal clearly explains what will be copied
- [x] Warning about what won't be copied
- [x] Success message shows course name
- [x] Redirect to cloned course after success

## Performance Considerations

**For a course with:**
- 50 lessons
- 20 quizzes
- 100 total questions
- 50 resources

**Expected cloning time:** < 3 seconds

**Database operations:**
1. 1 Course INSERT
2. 50 Lesson INSERTs
3. 50 Resource INSERTs
4. 20 Quiz INSERTs
5. 100 Question INSERTs

**Total: ~221 database operations in one transaction**

## SQL Verification Queries

Run these queries in PostgreSQL to verify cloning:

```sql
-- Check if course was cloned
SELECT id, title, is_published, instructor_id
FROM courses
WHERE title LIKE '%(Copy)%'
ORDER BY created_at DESC
LIMIT 5;

-- Verify lesson count matches
SELECT course_id, COUNT(*) as lesson_count
FROM lessons
WHERE course_id IN (SELECT id FROM courses WHERE title LIKE '%(Copy)%')
GROUP BY course_id;

-- Verify quiz count matches
SELECT course_id, COUNT(*) as quiz_count
FROM quizzes
WHERE course_id IN (SELECT id FROM courses WHERE title LIKE '%(Copy)%')
GROUP BY course_id;

-- Check embedded quiz relationships
SELECT l.title as lesson_title, q.title as quiz_title
FROM quizzes q
JOIN lessons l ON q.lesson_id = l.id
WHERE q.course_id IN (SELECT id FROM courses WHERE title LIKE '%(Copy)%');

-- Verify no enrollments copied
SELECT course_id, COUNT(*) as enrollment_count
FROM enrollments
WHERE course_id IN (SELECT id FROM courses WHERE title LIKE '%(Copy)%')
GROUP BY course_id;
-- Should return 0 enrollments
```

## Known Limitations

1. **File Resources:** Resource file_path is copied by reference, not creating new files
   - Both original and cloned course share the same uploaded files
   - If you delete resources from original, cloned course will lose access
   - **Solution:** For production, implement file duplication on S3/storage

2. **Announcements:** Currently not cloned (by design)
   - Instructors may want fresh announcements for each course
   - Can be enabled by uncommenting code in clone_course function

3. **Due Dates:** Quiz due dates are copied as-is
   - May need manual adjustment for new semester
   - **Enhancement:** Add option to adjust all dates by X days

## Troubleshooting

### Issue: "Error cloning course"
**Possible causes:**
- Database connection issue
- Foreign key constraint violation
- Permission issue

**Solution:** Check error logs, verify database relationships

### Issue: Cloned course missing lessons
**Possible causes:**
- Lesson query failed
- db.session.flush() not called

**Solution:** Check lesson_mapping dictionary is populated

### Issue: Embedded quizzes not linked to lessons
**Possible causes:**
- lesson_mapping not working correctly
- lesson_id null in original quiz

**Solution:** Verify lesson_mapping[original_lesson.id] exists before assignment

## Success Criteria

The cloning feature is considered successful if:
1. ✅ All content is duplicated correctly
2. ✅ New course has unique IDs for all entities
3. ✅ Relationships are preserved (lessons→resources, quizzes→questions)
4. ✅ Embedded quiz associations work correctly
5. ✅ Original course remains unchanged
6. ✅ Cloned course is unpublished by default
7. ✅ No student data is copied
8. ✅ User receives clear feedback
9. ✅ Transaction rolls back on error
10. ✅ Performance is acceptable (< 5 seconds for typical course)

---

**Feature Status:** ✅ Implemented and Ready for Testing
**Testing Required:** Manual testing with real course data
**Estimated Testing Time:** 30 minutes
