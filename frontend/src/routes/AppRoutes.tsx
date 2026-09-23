import { useEffect } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import AppLayout from '../app/AppLayout'
import SignInPage from '../features/authentication/pages/SignInPage'
import SignUpPage from '../features/authentication/pages/SignUpPage'
import DashboardPage from '../features/dashboard/pages/DashboardPage'
import HomePage from '../features/marketing/pages/HomePage'
import NewRequestPage from '../features/requester/pages/NewRequestPage'
import ProtectedRoute from './ProtectedRoute'

const RouteScrollReset = () => {
  const { pathname } = useLocation()

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [pathname])

  return null
}

const AppRoutes = () => {
  return (
    <>
      <RouteScrollReset />
      <Routes>
        <Route
          path="/"
          element={
            <AppLayout>
              <HomePage />
            </AppLayout>
          }
        />
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/sign-up" element={<SignUpPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizations/:organizationSlug/requests/new"
          element={
            <ProtectedRoute>
              <NewRequestPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default AppRoutes
