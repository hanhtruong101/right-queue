import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../features/hooks/useAuth'

type ProtectedRouteProps = {
  children: ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isLoading, user } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#F3F7FC] px-4 text-[#1E293B]">
        <div
          role="status"
          aria-live="polite"
          className="flex items-center gap-3 text-sm font-medium text-[#526274]"
        >
          <span
            aria-hidden="true"
            className="h-5 w-5 animate-spin rounded-full border-2 border-[#D9E3F0] border-t-[#2F5E9E]"
          />
          Checking your sign-in status…
        </div>
      </main>
    )
  }

  if (!user) {
    return <Navigate to="/sign-in" replace state={{ from: location }} />
  }

  return children
}

export default ProtectedRoute
