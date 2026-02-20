import { createBrowserRouter } from 'react-router';
import Welcome from './screens/Welcome';
import Upload from './screens/Upload';
import Processing from './screens/Processing';
import CourseHistory from './screens/CourseHistory';
import GapAnalysis from './screens/GapAnalysis';
import Recommendations from './screens/Recommendations';
import AdvisorConfirmation from './screens/AdvisorConfirmation';
import Complete from './screens/Complete';
import NotFound from './screens/NotFound';
// Components is a developer reference screen — only register it in dev builds.
// import.meta.env.DEV is true during `npm run dev` and false in `npm run build`.
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
  // Only expose the component library in local development — never in production.
  ...(import.meta.env.DEV ? [{ path: '/components', Component: Components }] : []),
  {
    // Explicit 404 instead of silently redirecting broken URLs to Welcome.
    // Previously: { path: '*', Component: Welcome } — this hid broken links.
    path: '*',
    Component: NotFound,
  },
]);
