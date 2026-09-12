import {
  ListChecks,
  MessageSquareText,
  Route,
  type LucideIcon,
} from 'lucide-react'

type Benefit = {
  title: string
  description: string
  icon: LucideIcon
}

const benefits: Benefit[] = [
  {
    title: 'Explain your issue naturally',
    description:
      'Describe what you need in your own words, without having to know which department handles it.',
    icon: MessageSquareText,
  },
  {
    title: 'Reach the right team sooner',
    description:
      'Clear routing rules direct your request to the most suitable service-team queue.',
    icon: Route,
  },
  {
    title: 'Track what happens next',
    description:
      'See the current status of your request and follow its progress after it is submitted.',
    icon: ListChecks,
  },
]

const steps = [
  {
    title: 'Describe your request',
    description:
      'Share a clear title and description of the support or service you need.',
  },
  {
    title: 'We route it to the right queue',
    description:
      'RightQueue checks clear, organization-specific rules. Unclear requests go to central triage for review.',
  },
  {
    title: 'Follow its progress',
    description:
      'Return to your request to see its status and what happens next.',
  },
]

const HomePage = () => {
  return (
    <>
      <section id="top" className="scroll-mt-18 overflow-hidden bg-white">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 py-16 sm:px-6 sm:py-20 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16 lg:px-8 lg:py-28">
          <div className="max-w-2xl">
            <p className="mb-4 text-sm font-semibold tracking-wide text-[#2F5E9E] uppercase">
              Service requests, clearly routed
            </p>
            <h1 className="text-4xl font-bold tracking-tight text-balance text-[#1E293B] sm:text-5xl lg:text-6xl lg:leading-[1.08]">
              Find the right team. First time.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-[#526274]">
              RightQueue helps people send service requests to the most suitable
              team, reducing repeated forwarding and making the next step clear.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                className="inline-flex min-h-11 items-center justify-center rounded-md bg-[#2F5E9E] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
              >
                Get started
              </button>
              <a
                href="#how-it-works"
                className="inline-flex min-h-11 items-center justify-center rounded-md border border-[#D9E3F0] bg-white px-5 py-2.5 text-sm font-semibold text-[#2F5E9E] transition-colors hover:border-[#2F5E9E] hover:bg-[#F3F7FC] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
              >
                See how it works
              </a>
            </div>
          </div>

          <div
            className="relative mx-auto w-full max-w-lg"
            aria-label="A request being directed to a team queue"
            role="img"
          >
            <div className="rounded-xl border border-[#D9E3F0] bg-[#F3F7FC] p-5 sm:p-7">
              <div className="flex items-center gap-3 rounded-lg border border-[#D9E3F0] bg-white p-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-[#F3F7FC]">
                  <img
                    src="/rightqueue-logo.svg"
                    alt=""
                    className="h-6 w-6"
                  />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold tracking-wide text-[#2F5E9E] uppercase">
                    New request
                  </p>
                  <p className="mt-1 truncate text-sm font-medium text-[#1E293B]">
                    I need help with a service
                  </p>
                </div>
              </div>

              <div className="flex justify-center py-4" aria-hidden="true">
                <div className="h-8 w-px bg-[#2F5E9E]" />
              </div>

              <div className="rounded-lg border border-[#D9E3F0] bg-white p-4 sm:p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold tracking-wide text-[#526274] uppercase">
                      Routed to
                    </p>
                    <p className="mt-1 font-semibold text-[#1E293B]">
                      Service-team queue
                    </p>
                  </div>
                  <span className="rounded-full bg-[#F3F7FC] px-2.5 py-1 text-xs font-semibold text-[#2F5E9E]">
                    Queued
                  </span>
                </div>
                <p className="mt-4 border-t border-[#D9E3F0] pt-4 text-sm leading-6 text-[#526274]">
                  If the route is unclear, central triage reviews the request.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="why-rightqueue" className="scroll-mt-18 bg-[#F3F7FC] py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold tracking-wide text-[#2F5E9E] uppercase">
              Why RightQueue
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-[#1E293B] sm:text-4xl">
              A clearer route from question to help
            </h2>
            <p className="mt-4 text-lg leading-8 text-[#526274]">
              Start with what you know. RightQueue handles the route and keeps
              the process visible.
            </p>
          </div>

          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {benefits.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="rounded-lg border border-[#D9E3F0] bg-white p-6"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-[#F3F7FC] text-[#2F5E9E]">
                  <Icon size={21} strokeWidth={1.8} aria-hidden="true" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-[#1E293B]">
                  {title}
                </h3>
                <p className="mt-2 text-sm leading-6 text-[#526274]">
                  {description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="scroll-mt-18 bg-white py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold tracking-wide text-[#2F5E9E] uppercase">
              How it works
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-[#1E293B] sm:text-4xl">
              Three steps to a clearer destination
            </h2>
          </div>

          <ol className="mt-12 grid gap-10 md:grid-cols-3 md:gap-8">
            {steps.map(({ title, description }, index) => (
              <li key={title} className="relative">
                <div className="flex h-10 w-10 items-center justify-center rounded-full border border-[#2F5E9E] bg-white text-sm font-bold text-[#2F5E9E]">
                  {index + 1}
                </div>
                <h3 className="mt-5 text-lg font-semibold text-[#1E293B]">
                  {title}
                </h3>
                <p className="mt-2 text-sm leading-6 text-[#526274]">
                  {description}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="bg-[#F3F7FC] py-16 sm:py-20">
        <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold tracking-tight text-[#1E293B] sm:text-4xl">
            Ready to send your request in the right direction?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg leading-8 text-[#526274]">
            Describe what you need and let RightQueue guide it to the next best
            step.
          </p>
          <button
            type="button"
            className="mt-8 inline-flex min-h-11 items-center justify-center rounded-md bg-[#2F5E9E] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
          >
            Get started
          </button>
        </div>
      </section>
    </>
  )
}

export default HomePage
