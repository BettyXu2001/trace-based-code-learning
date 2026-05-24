import React from 'react';
import type { Course } from '../types';

interface CourseNavigatorProps {
  course: Course;
  currentLessonId: number;
  onLessonSelect: (lessonId: number) => void;
}

export const CourseNavigator: React.FC<CourseNavigatorProps> = ({
  course,
  currentLessonId,
  onLessonSelect,
}) => {
  return (
    <div className="course-navigator">
      <h3>课程目录</h3>
      <div className="course-info">
        <p>{course.description}</p>
        <p className="total-steps">总步骤: {course.total_steps}</p>
      </div>
      <ul className="lesson-list">
        {course.lessons.map((lesson) => (
          <li
            key={lesson.id}
            className={`lesson-item ${currentLessonId === lesson.id ? 'active' : ''}`}
            onClick={() => onLessonSelect(lesson.id)}
          >
            <span className="lesson-number">Lesson {lesson.id}</span>
            <span className="lesson-title">{lesson.title.replace(/^Lesson \d+: /, '')}</span>
            <span className="lesson-type">{lesson.type}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
