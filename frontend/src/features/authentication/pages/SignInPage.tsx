import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'

const SignInPage = () => {
  const handlePrototypeSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
  }

  return (
    <AuthLayout
      title="Welcome back"
      description="Sign in to manage your RightQueue requests."
    >
      <form onSubmit={handlePrototypeSubmit} className="space-y-5">
        <div>
          <label
            htmlFor="sign-in-email"
            className="block text-sm font-semibold text-[#1E293B]"
          >
            Email address
          </label>
          <input
            id="sign-in-email"
            name="email"
            type="email"
            autoComplete="email"
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
            required
            className="mt-2 block min-h-11 w-full rounded-md border border-[#D9E3F0] bg-white px-3.5 py-2.5 text-[#1E293B] outline-none transition focus:border-[#2F5E9E] focus:ring-2 focus:ring-[#2F5E9E]/20"
          />
        </div>

        <button
          type="submit"
          className="inline-flex min-h-11 w-full cursor-pointer items-center justify-center rounded-md bg-[#2F5E9E] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
        >
          Sign in
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-[#526274]">
        Don&apos;t have an account?{' '}
        <Link
          to="/sign-up"
          className="cursor-pointer rounded-sm font-semibold text-[#2F5E9E] underline-offset-4 hover:text-[#244B80] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
        >
          Create one
        </Link>
      </p>
    </AuthLayout>
  )
}

export default SignInPage
