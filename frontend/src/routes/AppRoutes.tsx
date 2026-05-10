import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import ErrorBoundary from "../components/ErrorBoundary";
import ProtectedRoute from "../features/auth/ProtectedRoute";

const Login = lazy(() => import("../features/auth/Login"));
const OverviewPage = lazy(() => import("../features/admin/screens/OverviewPage"));
const CandidatesPage = lazy(() => import("../features/admin/screens/CandidatesPage"));

const DashboardPage = lazy(() => import("../features/candidate/screens/DashboardPage"));
const BadgesPage = lazy(() => import("../features/candidate/screens/BadgesPage"));
const InstructionsPage = lazy(() => import("../features/assessment/InstructionsPage"));
const ThankYouPage = lazy(() => import("../features/assessment/ThankYouPage"));
const AssessmentPage = lazy(() => import("../features/assessment/AssessmentPage"));
const PastScoresPage = lazy(() => import("../features/candidate/screens/PastScoresPage"));

import PageLoader from "../components/PageLoader";

import DashboardLayout from "../components/layout/DashboardLayout";

const AppRoutes = () => {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute allowedRoles={["candidate"]} />}>
            <Route path="/candidate" element={<DashboardLayout role="candidate" />}>
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="badges" element={<BadgesPage />} />
              <Route path="scores" element={<PastScoresPage />} />
            </Route>
            <Route path="/candidate/instructions" element={<InstructionsPage />} />
            <Route path="/candidate/assessment/:sessionId" element={<AssessmentPage />} />
            <Route path="/candidate/thankyou" element={<ThankYouPage />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
            <Route path="/admin" element={<DashboardLayout role="admin" />}>
              <Route path="dashboard" element={<OverviewPage />} />
              <Route path="candidates" element={<CandidatesPage />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

export default AppRoutes;
