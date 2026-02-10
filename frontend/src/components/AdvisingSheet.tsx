import React, { useState, useEffect } from 'react';
import {
  addCourse,
  Course,
  CourseInput,
  ExtractedData,
  getCourses,
  getUserCourses,
  updateUserCourse,
  uploadFile,
  UserCourse,
  UserCourseUpdate,
} from '../api';
import { AxiosError } from 'axios';

interface ApiErrorResponse {
  error?: string;
}

const AdvisingSheet: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [userCourses, setUserCourses] = useState<UserCourse[]>([]);
  const [newCourse, setNewCourse] = useState({
    code: '',
    name: '',
    credits: '',
    required: false,
    prerequisites: '',
  });
  const [selectedCourse, setSelectedCourse] = useState('');
  const [completed, setCompleted] = useState(false);
  const [grade, setGrade] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    void fetchCourses();
    void fetchUserCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await getCourses();
      setCourses(response.data);
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };

  const fetchUserCourses = async () => {
    try {
      const response = await getUserCourses();
      setUserCourses(response.data);
    } catch (error) {
      console.error('Error fetching user courses:', error);
    }
  };

  const handleAddCourse = async (e: React.FormEvent) => {
    e.preventDefault();

    const parsedCredits = Number.parseInt(newCourse.credits, 10);
    if (Number.isNaN(parsedCredits)) {
      return;
    }

    const payload: CourseInput = {
      code: newCourse.code,
      name: newCourse.name,
      credits: parsedCredits,
      required: newCourse.required,
      prerequisites: newCourse.prerequisites
        .split(',')
        .map((p) => p.trim())
        .filter(Boolean),
    };

    try {
      await addCourse(payload);
      setNewCourse({ code: '', name: '', credits: '', required: false, prerequisites: '' });
      await fetchCourses();
    } catch (error) {
      console.error('Error adding course:', error);
    }
  };

  const handleUpdateUserCourse = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload: UserCourseUpdate = {
      course_code: selectedCourse,
      completed,
      grade,
    };

    try {
      await updateUserCourse(payload);
      setSelectedCourse('');
      setCompleted(false);
      setGrade('');
      await fetchUserCourses();
    } catch (error) {
      console.error('Error updating user course:', error);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading file...');
    setExtractedData(null);

    try {
      const response = await uploadFile(file);
      setUploadStatus('Upload successful! Extracting course data...');

      if (response.data.extracted_data) {
        setExtractedData(response.data.extracted_data);
        const coursesCount = response.data.extracted_data.courses?.length || 0;
        const created = response.data.courses_created || 0;
        const updated = response.data.courses_updated || 0;

        setUploadStatus(`Success! Found ${coursesCount} courses. Created ${created}, Updated ${updated}.`);
      } else {
        setUploadStatus('File uploaded successfully!');
      }

      setFile(null);
      await fetchUserCourses();
      await fetchCourses();
    } catch (error) {
      const apiError = error as AxiosError<ApiErrorResponse>;
      console.error('Error uploading file:', apiError);
      const errorMsg = apiError.response?.data?.error || 'Upload failed. Please try again.';
      setUploadStatus(`Error: ${errorMsg}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <h2>Advising Sheet</h2>

      <div style={{ marginBottom: '30px', padding: '20px', background: '#f9f9f9', borderRadius: '8px' }}>
        <h3>Upload Advising Sheet (AI-Powered Extraction)</h3>
        <p style={{ color: '#666', fontSize: '14px' }}>
          Upload your academic transcript (PDF, CSV, or Excel) and LandingAI will extract your courses.
        </p>
        <form onSubmit={handleFileUpload}>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            accept=".pdf,.xlsx,.xls,.csv"
            disabled={isUploading}
            style={{ marginBottom: '10px' }}
          />
          <button type="submit" disabled={!file || isUploading} style={{ marginLeft: '10px' }}>
            {isUploading ? 'Processing...' : 'Upload & Extract'}
          </button>
        </form>

        {uploadStatus && (
          <div
            style={{
              marginTop: '15px',
              padding: '12px',
              background: uploadStatus.startsWith('Error:') ? '#fee' : '#efe',
              border: `1px solid ${uploadStatus.startsWith('Error:') ? '#fcc' : '#cfc'}`,
              borderRadius: '6px',
            }}
          >
            <strong>{uploadStatus}</strong>
          </div>
        )}

        {extractedData && (
          <div
            style={{
              marginTop: '20px',
              padding: '15px',
              background: '#fff',
              border: '2px solid #4CAF50',
              borderRadius: '8px',
            }}
          >
            <h4>Extracted Data:</h4>
            {extractedData.student_name && (
              <p>
                <strong>Student:</strong> {extractedData.student_name}
              </p>
            )}
            {extractedData.student_id && (
              <p>
                <strong>Student ID:</strong> {extractedData.student_id}
              </p>
            )}
            {extractedData.program && (
              <p>
                <strong>Program:</strong> {extractedData.program}
              </p>
            )}
            <p>
              <strong>Courses Found:</strong> {extractedData.courses?.length || 0}
            </p>

            {extractedData.courses && extractedData.courses.length > 0 && (
              <details style={{ marginTop: '10px' }}>
                <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>View Course Details</summary>
                <ul style={{ marginTop: '10px' }}>
                  {extractedData.courses.map((course, idx) => (
                    <li key={`${course.course_code}-${idx}`} style={{ marginBottom: '8px' }}>
                      <strong>{course.course_code}</strong>: {course.course_name} ({course.credits} credits)
                      {course.grade && ` - Grade: ${course.grade}`}
                      {course.professor && ` - Prof: ${course.professor}`}
                      {course.completed && ' - Completed'}
                    </li>
                  ))}
                </ul>
              </details>
            )}

            <button
              onClick={() => setExtractedData(null)}
              style={{
                marginTop: '10px',
                padding: '6px 12px',
                background: '#666',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Close
            </button>
          </div>
        )}
      </div>

      <div>
        <h3>Add New Course</h3>
        <form onSubmit={handleAddCourse}>
          <input
            type="text"
            placeholder="Course Code"
            value={newCourse.code}
            onChange={(e) => setNewCourse({ ...newCourse, code: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="Course Name"
            value={newCourse.name}
            onChange={(e) => setNewCourse({ ...newCourse, name: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Credits"
            value={newCourse.credits}
            onChange={(e) => setNewCourse({ ...newCourse, credits: e.target.value })}
            required
          />
          <label>
            <input
              type="checkbox"
              checked={newCourse.required}
              onChange={(e) => setNewCourse({ ...newCourse, required: e.target.checked })}
            />
            Required
          </label>
          <input
            type="text"
            placeholder="Prerequisites (comma separated codes)"
            value={newCourse.prerequisites}
            onChange={(e) => setNewCourse({ ...newCourse, prerequisites: e.target.value })}
          />
          <button type="submit">Add Course</button>
        </form>
      </div>

      <div>
        <h3>Update Your Courses</h3>
        <form onSubmit={handleUpdateUserCourse}>
          <select value={selectedCourse} onChange={(e) => setSelectedCourse(e.target.value)} required>
            <option value="">Select Course</option>
            {courses.map((course) => (
              <option key={course.id} value={course.code}>
                {course.code} - {course.name}
              </option>
            ))}
          </select>
          <label>
            <input type="checkbox" checked={completed} onChange={(e) => setCompleted(e.target.checked)} />
            Completed
          </label>
          <input
            type="text"
            placeholder="Grade"
            value={grade}
            onChange={(e) => setGrade(e.target.value)}
          />
          <button type="submit">Update</button>
        </form>
      </div>

      <div>
        <h3>Your Courses</h3>
        <ul>
          {userCourses.map((uc) => (
            <li key={uc.id}>
              {uc.course.code} - {uc.course.name} - Completed: {uc.completed ? 'Yes' : 'No'} - Grade:{' '}
              {uc.grade || 'N/A'}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AdvisingSheet;
