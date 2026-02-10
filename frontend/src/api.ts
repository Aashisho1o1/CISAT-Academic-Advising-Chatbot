import axios from 'axios';

export interface User {
  id: number;
  username: string;
  role: string;
}

export interface LoginResponse {
  message: string;
  user: User;
}

export interface Course {
  id: number;
  code: string;
  name: string;
  credits: number;
  required: boolean;
  prerequisites: string[];
}

export interface CourseInput {
  code: string;
  name: string;
  credits: number;
  required?: boolean;
  prerequisites?: string[];
}

export interface UserCourse {
  id: number;
  course: Pick<Course, 'code' | 'name' | 'credits'>;
  completed: boolean;
  grade: string;
  semester_taken?: string | null;
}

export interface UserCourseUpdate {
  course_code: string;
  completed?: boolean;
  grade?: string;
  semester_taken?: string;
}

export interface ExtractedCourse {
  course_code: string;
  course_name: string;
  credits: number;
  grade?: string;
  professor?: string;
  completed?: boolean;
  semester_taken?: string;
}

export interface ExtractedData {
  core_courses?: ExtractedCourse[];
  concentration_courses?: ExtractedCourse[];
  elective_courses?: ExtractedCourse[];
  courses?: ExtractedCourse[];
  student_name?: string;
  student_id?: string;
  program?: string;
}

export interface UploadResponse {
  message: string;
  id: number;
  extracted_data?: ExtractedData;
  courses_created?: number;
  courses_updated?: number;
}

export interface UploadAsyncResponse {
  message: string;
  job_id: string;
  advising_sheet_id: number;
}

export interface UploadStatusResponse {
  job_id: string;
  status: 'processing' | 'completed' | 'failed' | string;
  result: unknown;
}

export interface ProgressResponse {
  progress: number;
  completed: number;
  total: number;
}

export interface JourneyNode {
  id: string;
  label: string;
  completed: boolean;
  required: boolean;
  credits: number;
  semester?: string | null;
}

export interface JourneyEdge {
  from: string;
  to: string;
  id?: string;
}

export interface JourneyResponse {
  nodes: JourneyNode[];
  edges: JourneyEdge[];
}

export const DEFAULT_API_BASE_URL = 'http://localhost:8000/api';

export const resolveApiBaseUrl = (): string =>
  process.env.REACT_APP_API_BASE_URL || DEFAULT_API_BASE_URL;

export const API_BASE_URL = resolveApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const login = (username: string, password: string) =>
  api.post<LoginResponse>('/login', { username, password });

export const getCurrentUser = () => api.get<{ user: User }>('/me');

export const logout = () => api.post<{ message: string }>('/logout');

export const getCourses = () => api.get<Course[]>('/courses');

export const addCourse = (course: CourseInput) => api.post('/courses', course);

export const getUserCourses = () => api.get<UserCourse[]>('/user/courses');

export const updateUserCourse = (courseData: UserCourseUpdate) =>
  api.post<{ message: string }>('/user/courses', courseData);

export const uploadFile = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const uploadFileAsync = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<UploadAsyncResponse>('/upload/async', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const checkUploadStatus = (jobId: string) =>
  api.get<UploadStatusResponse>(`/upload/status/${jobId}`);

export const getProgress = () => api.get<ProgressResponse>('/progress');

export const getJourney = () => api.get<JourneyResponse>('/journey');

export default api;
