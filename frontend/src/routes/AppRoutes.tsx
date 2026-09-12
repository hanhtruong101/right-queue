import { useEffect } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import AppLayout from '../app/AppLayout'
import SignInPage from '../features/authentication/pages/SignInPage'
import SignUpPage from '../features/authentication/pages/SignUpPage'
import HomePage from '../features/marketing/pages/HomePage'

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
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default AppRoutes
