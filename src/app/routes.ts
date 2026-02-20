import { createBrowserRouter } from 'react-router';
import Welcome from './screens/Welcome';
import Upload from './screens/Upload';
import Processing from './screens/Processing';
import CourseHistory from './screens/CourseHistory';
import GapAnalysis from './screens/GapAnalysis';
import Recommendations from './screens/Recommendations';
import AdvisorConfirmation from './screens/AdvisorConfirmation';
import Complete from './screens/Complete';
import Components from './screens/Components';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: Welcome,
  },
  {
    path: '/upload',
    Component: Upload,
  },
  {
    path: '/processing',
    Component: Processing,
  },
  {
    path: '/course-history',
    Component: CourseHistory,
  },
  {
    path: '/gap-analysis',
    Component: GapAnalysis,
  },
  {
    path: '/recommendations',
    Component: Recommendations,
  },
  {
    path: '/advisor-confirmation',
    Component: AdvisorConfirmation,
  },
  {
    path: '/complete',
    Component: Complete,
  },
  {
    path: '/components',
    Component: Components,
  },
  {
    path: '*',
    Component: Welcome,
  },
]);
