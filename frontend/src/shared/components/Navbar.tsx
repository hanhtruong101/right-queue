import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-[#D9E3F0] bg-white">
      <nav
        aria-label="Main navigation"
        className="mx-auto flex h-18 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8"
      >
        <Link
          to="/"
          onClick={() => window.scrollTo({ top: 0 })}
          className="flex items-center gap-2.5 rounded-md text-[#1E293B] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-4"
          aria-label="RightQueue home"
        >
          <img src="/rightqueue-logo.svg" alt="" className="h-8 w-8" />
          <span className="text-lg font-semibold tracking-tight">RightQueue</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          <a
            href="#how-it-works"
            className="rounded-sm text-sm font-medium text-[#526274] transition-colors hover:text-[#2F5E9E] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-4"
          >
            How it works
          </a>
          <a
            href="#why-rightqueue"
            className="rounded-sm text-sm font-medium text-[#526274] transition-colors hover:text-[#2F5E9E] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-4"
          >
            Why RightQueue
          </a>
        </div>

        <Link
          to="/sign-in"
          className="cursor-pointer rounded-md border border-[#2F5E9E] px-4 py-2 text-sm font-semibold text-[#2F5E9E] transition-colors hover:bg-[#F3F7FC] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
          aria-label="Sign in to RightQueue"
        >
          Sign in
        </Link>
      </nav>
    </header>
  )
}

export default Navbar
