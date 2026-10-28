import { ArrowLeft, Plus } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../../../services/apiClient'
import { useAuth } from '../../hooks/useAuth'
import { getMyRequests } from '../api/requesterApi'
import type { ServiceRequestStatus, ServiceRequestSummary } from '../types'

type RequestListState =
  | { status: 'loading' }
  | { status: 'ready'; requests: ServiceRequestSummary[] }
  | { status: 'access-denied' }
  | { status: 'error' }

const statusLabels: Record<ServiceRequestStatus, string> = {
  SUBMITTED: 'Submitted',
  PENDING_TRIAGE: 'Pending triage',
  QUEUED: 'Queued',
  IN_PROGRESS: 'In progress',
  WAITING_FOR_REQUESTER: 'Waiting for you',
  RESOLVED: 'Resolved',
}

const dateFormatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
})

function RequestTime({ value }: { value: string }) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? (
    <>Not available</>
  ) : (
    <time dateTime={value}>{dateFormatter.format(date)}</time>
  )
}

function RequestCard({ request }: { request: ServiceRequestSummary }) {
  return (
    <li className="rounded-lg border border-[#D9E3F0] bg-white p-5 shadow-sm sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <h2 className="min-w-0 break-words text-lg font-semibold">{request.title}</h2>
        <span className="rounded-full bg-[#F3F7FC] px-3 py-1 text-sm font-semibold text-[#2F5E9E]">
          {statusLabels[request.current_status] ?? request.current_status}
        </span>
      </div>
      <p className="mt-2 break-all text-xs text-[#526274]">Reference: {request.reference}</p>
      <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-[#526274]">Service</dt>
          <dd className="mt-1 break-words font-medium">{request.service_name ?? 'Not specified'}</dd>
        </div>
        <div>
          <dt className="text-[#526274]">Assigned team</dt>
          <dd className="mt-1 break-words font-medium">{request.assigned_team_name ?? 'Not assigned yet'}</dd>
        </div>
        <div>
          <dt className="text-[#526274]">Submitted</dt>
          <dd className="mt-1"><RequestTime value={request.submitted_at} /></dd>
        </div>
        <div>
          <dt className="text-[#526274]">Last updated</dt>
          <dd className="mt-1"><RequestTime value={request.updated_at} /></dd>
        </div>
      </dl>
    </li>
  )
}

function RequestList({ organizationSlug }: { organizationSlug: string }) {
  const [state, setState] = useState<RequestListState>({ status: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    getMyRequests(organizationSlug, controller.signal)
      .then((requests) => {
        if (!controller.signal.aborted) setState({ status: 'ready', requests })
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        const accessDenied = error instanceof ApiError && [401, 403, 404].includes(error.status)
        setState({ status: accessDenied ? 'access-denied' : 'error' })
      })

    return () => controller.abort()
  }, [organizationSlug, attempt])

  if (state.status === 'loading') {
    return <p role="status" className="mt-8 text-[#526274]">Loading your requests…</p>
  }

  if (state.status === 'access-denied') {
    return <p role="alert" className="mt-8 text-[#526274]">Your requests are unavailable. Return to the dashboard to check your sign-in and organization access.</p>
  }

  if (state.status === 'error') {
    return (
      <div className="mt-8 rounded-lg border border-red-200 bg-red-50 p-5">
        <p role="alert" className="text-red-800">We could not load your requests. Please try again.</p>
        <button
          type="button"
          onClick={() => {
            setState({ status: 'loading' })
            setAttempt((previous) => previous + 1)
          }}
          className="mt-3 cursor-pointer rounded-md px-3 py-2 font-semibold text-[#2F5E9E] underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E]"
        >
          Try again
        </button>
      </div>
    )
  }

  if (state.requests.length === 0) {
    return (
      <div role="status" className="mt-8 rounded-lg border border-dashed border-[#D9E3F0] bg-white p-8 text-center">
        <h2 className="text-lg font-semibold">No requests yet</h2>
        <p className="mt-2 text-[#526274]">Requests you submit to this organization will appear here.</p>
      </div>
    )
  }

  return (
    <section aria-label="Your request history" className="mt-8">
      <p role="status" className="mb-4 text-sm text-[#526274]">
        {state.requests.length} {state.requests.length === 1 ? 'request' : 'requests'} · Newest first
      </p>
      <ul className="space-y-4">
        {state.requests.map((request) => <RequestCard key={request.reference} request={request} />)}
      </ul>
    </section>
  )
}

export default function MyRequestsPage() {
  const { organizationSlug = '' } = useParams()
  const { user } = useAuth()
  const membership = user?.memberships.find((item) => item.organization_slug === organizationSlug)

  return (
    <div className="min-h-screen bg-[#F3F7FC] font-sans text-[#1E293B] antialiased">
      <header className="border-b border-[#D9E3F0] bg-white">
        <div className="mx-auto max-w-6xl px-4 py-5 sm:px-6 lg:px-8">
          <Link to="/dashboard" className="inline-flex items-center gap-2.5 rounded-md text-lg font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E]">
            <img src="/rightqueue-logo.svg" alt="" className="h-8 w-8" />
            RightQueue
          </Link>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <Link to="/dashboard" className="inline-flex items-center gap-2 rounded-sm text-sm font-semibold text-[#2F5E9E] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E]">
          <ArrowLeft size={17} aria-hidden="true" /> Back to dashboard
        </Link>
        <div className="mt-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            {membership && <p className="text-sm font-semibold text-[#2F5E9E]">{membership.organization_name}</p>}
            <h1 className="mt-2 text-3xl font-bold tracking-tight">My requests</h1>
            <p className="mt-3 text-[#526274]">View your submitted requests and their latest status.</p>
          </div>
          {membership && (
            <Link to={`/organizations/${encodeURIComponent(organizationSlug)}/requests/new`} className="inline-flex min-h-10 items-center gap-2 rounded-md bg-[#2F5E9E] px-4 py-2 text-sm font-semibold text-white hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2">
              <Plus size={17} aria-hidden="true" /> Submit a request
            </Link>
          )}
        </div>
        {membership && user ? (
          <RequestList key={`${user.id}:${organizationSlug}`} organizationSlug={organizationSlug} />
        ) : (
          <p role="alert" className="mt-8 text-[#526274]">You do not have an active membership in this organization.</p>
        )}
      </main>
    </div>
  )
}
