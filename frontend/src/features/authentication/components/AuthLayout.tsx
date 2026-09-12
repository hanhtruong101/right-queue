import { ArrowLeft } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

type AuthLayoutProps = {
  children: ReactNode
  description: string
  title: string
}

const AuthLayout = ({
  children,
  description,
  title,
}: AuthLayoutProps) => {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#F3F7FC] px-4 py-10 font-sans text-[#1E293B] antialiased sm:px-6">
      <div className="w-full max-w-md">
        <Link
          to="/"
          className="mx-auto flex cursor-pointer items-center gap-2.5 rounded-md text-[#1E293B] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F3F7FC]"
          aria-label="Return to the RightQueue home page"
        >
          <img src="/rightqueue-logo.svg" alt="" className="h-9 w-9" />
          <span className="text-xl font-semibold tracking-tight">RightQueue</span>
        </Link>

        <section
          aria-labelledby="auth-heading"
          className="mt-8 rounded-xl border border-[#D9E3F0] bg-white p-6 shadow-sm sm:p-8"
        >
          <Link
            to="/"
            className="inline-flex cursor-pointer items-center gap-2 rounded-sm text-sm font-medium text-[#526274] transition-colors hover:text-[#2F5E9E] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
          >
            <ArrowLeft size={17} strokeWidth={2} aria-hidden="true" />
            Back to home
          </Link>

          <header className="mt-6">
            <h1
              id="auth-heading"
              className="text-2xl font-bold tracking-tight text-[#1E293B] sm:text-3xl"
            >
              {title}
            </h1>
            <p className="mt-2 text-sm leading-6 text-[#526274]">
              {description}
            </p>
          </header>

          <div className="mt-7">{children}</div>
        </section>
      </div>
    </main>
  )
}

export default AuthLayout
