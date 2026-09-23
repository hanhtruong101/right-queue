import { useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { ApiError } from '../../../services/apiClient'
import AuthLayout from '../components/AuthLayout'

const SignInPage = () => {
  const { isLoading, login, user } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const routeState = location.state as
    | { from?: { pathname: string; search?: string; hash?: string } }
    | null
  const requestedRoute = routeState?.from
    ? `${routeState.from.pathname}${routeState.from.search ?? ''}${routeState.from.hash ?? ''}`
    : '/dashboard'

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    setErrorMessage('')
    setIsSubmitting(true)

    try {
      await login({ username, password })
      navigate(requestedRoute, { replace: true })
    } catch (error) {
      if (
        error instanceof ApiError &&
        (error.status === 400 || error.status === 401)
      ) {
        setErrorMessage('The username or password is incorrect.')
      } else {
        setErrorMessage(
          'RightQueue could not sign you in. Please check your connection and try again.',
        )
      }
      setPassword('')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <AuthLayout
        title="Welcome back"
        description="Sign in to manage your RightQueue requests."
      >
        <p role="status" aria-live="polite" className="text-sm text-[#526274]">
          Checking your sign-in status…
        </p>
      </AuthLayout>
    )
  }

  if (user) {
    return <Navigate to={requestedRoute} replace />
  }

  return (
    <AuthLayout
      title="Welcome back"
      description="Sign in to manage your RightQueue requests."
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label
            htmlFor="sign-in-username"
            className="block text-sm font-semibold text-[#1E293B]"
          >
            Username
          </label>
          <input
            id="sign-in-username"
            name="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            disabled={isSubmitting}
            required
            className="mt-2 block min-h-11 w-full rounded-md border border-[#D9E3F0] bg-white px-3.5 py-2.5 text-[#1E293B] outline-none transition placeholder:text-slate-400 focus:border-[#2F5E9E] focus:ring-2 focus:ring-[#2F5E9E]/20"
          />
        </div>

        <div>
          <label
            htmlFor="sign-in-password"
            className="block text-sm font-semibold text-[#1E293B]"
          >
            Password
          </label>
          <input
            id="sign-in-password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={isSubmitting}
            required
            className="mt-2 block min-h-11 w-full rounded-md border border-[#D9E3F0] bg-white px-3.5 py-2.5 text-[#1E293B] outline-none transition focus:border-[#2F5E9E] focus:ring-2 focus:ring-[#2F5E9E]/20"
          />
        </div>

        <div className="min-h-6" aria-live="polite">
          {errorMessage && (
            <p role="alert" className="text-sm font-medium text-red-700">
              {errorMessage}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex min-h-11 w-full cursor-pointer items-center justify-center rounded-md bg-[#2F5E9E] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-65"
        >
          {isSubmitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-[#526274]">
        Need an account? Contact your organization administrator.
      </p>
    </AuthLayout>
  )
}

export default SignInPage
