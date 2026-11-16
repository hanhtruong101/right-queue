import {
  ArrowLeft,
  CheckCircle2,
  ClipboardPenLine,
  Send,
} from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../../../services/apiClient'
import { useAuth } from '../../hooks/useAuth'
import { createServiceRequest } from '../api/requesterApi'
import type {
  CreatedServiceRequest,
  RequestStatus,
} from '../types'

type FieldErrors = Partial<Record<'title' | 'description', string>>

const statusLabels: Record<RequestStatus, string> = {
  QUEUED: 'Queued',
  PENDING_TRIAGE: 'Pending triage',
}

const formatSubmittedTime = (submittedAt: string) => {
  const date = new Date(submittedAt)

  if (Number.isNaN(date.getTime())) {
    return submittedAt
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

const NewRequestPage = () => {
  const { organizationSlug = '' } = useParams()
  const { user } = useAuth()
  const membership = user?.memberships.find(
    (item) => item.organization_slug === organizationSlug,
  )

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [createdRequest, setCreatedRequest] =
    useState<CreatedServiceRequest | null>(null)

  const validateForm = () => {
    const errors: FieldErrors = {}

    if (title.trim().length < 5) {
      errors.title = 'Enter a title containing at least 5 characters.'
    }

    if (!description.trim()) {
      errors.description = 'Enter a description of your request.'
    }

    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isSubmitting || !membership) {
      return
    }

    setFormError('')
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      const response = await createServiceRequest(organizationSlug, {
        title: title.trim(),
        description: description.trim(),
      })
      setCreatedRequest(response)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (error) {
      if (error instanceof ApiError && error.status === 400) {
        const data =
          error.data && typeof error.data === 'object'
            ? (error.data as Record<string, unknown>)
            : {}
        const errors: FieldErrors = {}

        if ('title' in data) {
          errors.title = 'Enter a valid title containing at least 5 characters.'
        }
        if ('description' in data) {
          errors.description = 'Enter a valid description for your request.'
        }

        setFieldErrors(errors)
        setFormError(
          Object.keys(errors).length
            ? 'Please review the highlighted fields and try again.'
            : 'Your request could not be submitted. Please review it and try again.',
        )
      } else if (
        error instanceof ApiError &&
        (error.status === 403 || error.status === 404)
      ) {
        setFormError(
          'You no longer have access to submit requests for this organization.',
        )
      } else {
        setFormError(
          'RightQueue could not submit your request. Please check your connection and try again.',
        )
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const resetForm = () => {
    setTitle('')
    setDescription('')
    setFieldErrors({})
    setFormError('')
    setCreatedRequest(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (!membership) {
    return (
      <PageShell>
        <section className="mx-auto max-w-xl rounded-lg border border-[#D9E3F0] bg-white p-6 text-center shadow-sm sm:p-8">
          <h1 className="text-2xl font-bold tracking-tight">Access denied</h1>
          <p className="mt-3 leading-7 text-[#526274]">
            You do not have an active membership for this organization.
          </p>
          <Link
            to="/dashboard"
            className="mt-6 inline-flex min-h-11 items-center justify-center rounded-md bg-[#2F5E9E] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
          >
            Return to dashboard
          </Link>
        </section>
      </PageShell>
    )
  }

  if (createdRequest) {
    const statusLabel =
      statusLabels[createdRequest.current_status] ?? createdRequest.current_status
    const routingExplanation =
      createdRequest.current_status === 'QUEUED'
        ? 'Your request was routed to the team best placed to handle it.'
        : 'Your request will be reviewed before it is routed to a team.'

    return (
      <PageShell>
        <section
          aria-labelledby="confirmation-heading"
          className="mx-auto max-w-2xl rounded-lg border border-[#D9E3F0] bg-white p-6 shadow-sm sm:p-8"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#F3F7FC] text-[#2F5E9E]">
            <CheckCircle2 size={27} aria-hidden="true" />
          </div>
          <h1
            id="confirmation-heading"
            className="mt-5 text-2xl font-bold tracking-tight sm:text-3xl"
          >
            Request submitted
          </h1>
          <p className="mt-3 leading-7 text-[#526274]">{routingExplanation}</p>

          <dl className="mt-7 divide-y divide-[#D9E3F0] border-y border-[#D9E3F0]">
            <ConfirmationRow label="Reference" value={createdRequest.reference} />
            <ConfirmationRow label="Title" value={createdRequest.title} />
            <ConfirmationRow
              label="Service"
              value={createdRequest.service_name ?? 'Not yet identified'}
            />
            <ConfirmationRow
              label="Assigned team"
              value={createdRequest.assigned_team_name ?? 'Not yet assigned'}
            />
            <ConfirmationRow label="Status" value={statusLabel} />
            <ConfirmationRow
              label="Submitted"
              value={formatSubmittedTime(createdRequest.submitted_at)}
            />
          </dl>

          <div className="mt-7 flex flex-col gap-3 sm:flex-row">
            <Link
              to={`/organizations/${encodeURIComponent(organizationSlug)}/requests`}
              className="inline-flex min-h-11 items-center justify-center rounded-md bg-[#2F5E9E] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
            >
              View my requests
            </Link>
            <button
              type="button"
              onClick={resetForm}
              className="inline-flex min-h-11 cursor-pointer items-center justify-center rounded-md border border-[#2F5E9E] bg-white px-5 py-2.5 text-sm font-semibold text-[#2F5E9E] transition-colors hover:bg-[#F3F7FC] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
            >
              Submit another request
            </button>
          </div>
        </section>
      </PageShell>
    )
  }

  return (
    <PageShell>
      <div className="mx-auto max-w-2xl">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 rounded-sm text-sm font-semibold text-[#2F5E9E] hover:text-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
        >
          <ArrowLeft size={17} aria-hidden="true" />
          Back to dashboard
        </Link>

        <header className="mt-6">
          <p className="text-sm font-semibold tracking-wide text-[#2F5E9E] uppercase">
            {membership.organization_name}
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Submit a request
          </h1>
          <p className="mt-3 leading-7 text-[#526274]">
            Describe what you need help with. RightQueue will identify the
            appropriate service and route your request automatically. Unclear
            requests will be reviewed by a triage coordinator.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          noValidate
          className="mt-8 rounded-lg border border-[#D9E3F0] bg-white p-6 shadow-sm sm:p-8"
        >
          <div>
            <label htmlFor="request-title" className="block text-sm font-semibold">
              Title
            </label>
            <p id="request-title-help" className="mt-1 text-sm text-[#526274]">
              Summarize what you need in at least 5 characters.
            </p>
            <input
              id="request-title"
              name="title"
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              disabled={isSubmitting}
              aria-describedby={
                fieldErrors.title
                  ? 'request-title-help request-title-error'
                  : 'request-title-help'
              }
              aria-invalid={Boolean(fieldErrors.title)}
              maxLength={150}
              required
              className="mt-2 block min-h-11 w-full rounded-md border border-[#D9E3F0] bg-white px-3.5 py-2.5 outline-none transition focus:border-[#2F5E9E] focus:ring-2 focus:ring-[#2F5E9E]/20 disabled:bg-slate-50"
            />
            {fieldErrors.title && (
              <p id="request-title-error" className="mt-2 text-sm text-red-700">
                {fieldErrors.title}
              </p>
            )}
          </div>

          <div className="mt-5">
            <label
              htmlFor="request-description"
              className="block text-sm font-semibold"
            >
              Description
            </label>
            <p
              id="request-description-help"
              className="mt-1 text-sm text-[#526274]"
            >
              Include the details that will help the receiving team understand
              your request.
            </p>
            <textarea
              id="request-description"
              name="description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              disabled={isSubmitting}
              aria-describedby={
                fieldErrors.description
                  ? 'request-description-help request-description-error'
                  : 'request-description-help'
              }
              aria-invalid={Boolean(fieldErrors.description)}
              required
              rows={6}
              className="mt-2 block w-full resize-y rounded-md border border-[#D9E3F0] bg-white px-3.5 py-2.5 outline-none transition focus:border-[#2F5E9E] focus:ring-2 focus:ring-[#2F5E9E]/20 disabled:bg-slate-50"
            />
            {fieldErrors.description && (
              <p
                id="request-description-error"
                className="mt-2 text-sm text-red-700"
              >
                {fieldErrors.description}
              </p>
            )}
          </div>

          <div className="mt-6 min-h-6" aria-live="assertive">
            {formError && (
              <p role="alert" className="text-sm font-medium text-red-700">
                {formError}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="mt-3 inline-flex min-h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-md bg-[#2F5E9E] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-65 sm:w-auto"
          >
            <Send size={17} aria-hidden="true" />
            {isSubmitting ? 'Submitting…' : 'Submit request'}
          </button>
        </form>
      </div>
    </PageShell>
  )
}

const PageShell = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen bg-[#F3F7FC] font-sans text-[#1E293B] antialiased">
    <header className="border-b border-[#D9E3F0] bg-white">
      <div className="mx-auto flex min-h-18 max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link
          to="/dashboard"
          className="flex items-center gap-2.5 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-4"
          aria-label="RightQueue dashboard"
        >
          <img src="/rightqueue-logo.svg" alt="" className="h-8 w-8" />
          <span className="text-lg font-semibold tracking-tight">RightQueue</span>
        </Link>
        <div className="flex items-center gap-2 text-sm font-medium text-[#526274]">
          <ClipboardPenLine size={18} aria-hidden="true" />
          New request
        </div>
      </div>
    </header>
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
      {children}
    </main>
  </div>
)

const ConfirmationRow = ({ label, value }: { label: string; value: string }) => (
  <div className="grid gap-1 py-4 sm:grid-cols-[10rem_1fr] sm:gap-4">
    <dt className="text-sm font-medium text-[#526274]">{label}</dt>
    <dd className="break-words font-medium">{value}</dd>
  </div>
)

export default NewRequestPage
