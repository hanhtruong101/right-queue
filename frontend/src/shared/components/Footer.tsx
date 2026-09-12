const Footer = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-[#D9E3F0] bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-10 sm:px-6 md:flex-row md:items-end md:justify-between lg:px-8">
        <div className="max-w-md">
          <div className="flex items-center gap-2.5">
            <img src="/rightqueue-logo.svg" alt="" className="h-7 w-7" />
            <span className="font-semibold tracking-tight text-[#1E293B]">
              RightQueue
            </span>
          </div>
          <p className="mt-3 text-sm leading-6 text-[#526274]">
            Helping service requests reach the team best placed to handle them.
          </p>
        </div>

        <p className="text-sm text-[#526274]">
          &copy; {currentYear} RightQueue. All rights reserved.
        </p>
      </div>
    </footer>
  )
}

export default Footer
