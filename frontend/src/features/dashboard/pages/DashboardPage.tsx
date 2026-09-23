import { Building2, LogOut, Plus, UserRound } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import type { OrganizationRole } from '../../authentication/types'

const roleLabels: Record<OrganizationRole, string> = {
  REQUESTER: 'Requester',
  STAFF: 'Staff',
  TRIAGE_COORDINATOR: 'Triage coordinator',
  ORGANIZATION_ADMIN: 'Organization administrator',
}

const DashboardPage = () => {
  const { logout, user } = useAuth()
  const navigate = useNavigate()
  const [isSigningOut, setIsSigningOut] = useState(false)
  const [logoutError, setLogoutError] = useState('')

  if (!user) {
    return null
  }

  const displayName = user.first_name.trim() || user.username

  const handleSignOut = async () => {
    if (isSigningOut) {
      return
    }

    setLogoutError('')
    setIsSigningOut(true)

    try {
      await logout()
      navigate('/', { replace: true })
    } catch {
      setLogoutError(
        'RightQueue could not sign you out. You are still signed in; please try again.',
      )
    } finally {
      setIsSigningOut(false)
    }
  }

  return (
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

          <button
            type="button"
            onClick={handleSignOut}
            disabled={isSigningOut}
            className="inline-flex min-h-10 cursor-pointer items-center justify-center gap-2 rounded-md border border-[#D9E3F0] bg-white px-3.5 py-2 text-sm font-semibold text-[#2F5E9E] transition-colors hover:border-[#2F5E9E] hover:bg-[#F3F7FC] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-65"
          >
            <LogOut size={17} aria-hidden="true" />
            {isSigningOut ? 'Signing out…' : 'Sign out'}
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
        <header>
          <p className="text-sm font-semibold tracking-wide text-[#2F5E9E] uppercase">
            Dashboard
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Welcome, {displayName}
          </h1>
          <p className="mt-3 max-w-2xl leading-7 text-[#526274]">
            Review your account and the organizations where you can use RightQueue.
          </p>
        </header>

        {logoutError && (
          <p
            role="alert"
            className="mt-6 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-800"
          >
            {logoutError}
          </p>
        )}

        <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
          <section
            aria-labelledby="account-heading"
            className="rounded-lg border border-[#D9E3F0] bg-white p-6 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-[#F3F7FC] text-[#2F5E9E]">
                <UserRound size={21} aria-hidden="true" />
              </div>
              <h2 id="account-heading" className="text-lg font-semibold">
                Account
              </h2>
            </div>
            <dl className="mt-6 space-y-5">
              <div>
                <dt className="text-sm font-medium text-[#526274]">Username</dt>
                <dd className="mt-1 break-words font-medium">{user.username}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-[#526274]">Email</dt>
                <dd className="mt-1 break-words font-medium">
                  {user.email || 'Not provided'}
                </dd>
              </div>
            </dl>
          </section>

          <section
            aria-labelledby="organizations-heading"
            className="rounded-lg border border-[#D9E3F0] bg-white p-6 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-[#F3F7FC] text-[#2F5E9E]">
                <Building2 size={21} aria-hidden="true" />
              </div>
              <div>
                <h2 id="organizations-heading" className="text-lg font-semibold">
                  Organizations
                </h2>
                <p className="mt-0.5 text-sm text-[#526274]">
                  Your active RightQueue memberships
                </p>
              </div>
            </div>

            {user.memberships.length === 0 ? (
              <div className="mt-6 rounded-md border border-dashed border-[#D9E3F0] bg-[#F3F7FC] p-5">
                <p className="font-medium">No active organization memberships</p>
                <p className="mt-1 text-sm leading-6 text-[#526274]">
                  Contact your organization administrator if you expected to see an organization here.
                </p>
              </div>
            ) : (
              <ul className="mt-6 divide-y divide-[#D9E3F0] border-y border-[#D9E3F0]">
                {user.memberships.map((membership) => (
                  <li
                    key={membership.organization_slug}
                    className="py-5 first:pt-4 last:pb-4"
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <h3 className="font-semibold">
                          {membership.organization_name}
                        </h3>
                        <p className="mt-1 text-sm text-[#526274]">
                          {membership.organization_slug}
                        </p>
                      </div>
                      <div className="flex flex-col items-start gap-3 sm:items-end">
                        <div
                          className="flex flex-wrap gap-2 sm:justify-end"
                          aria-label={`Roles for ${membership.organization_name}`}
                        >
                          {membership.roles.map((role) => (
                            <span
                              key={role}
                              className="rounded-full bg-[#F3F7FC] px-3 py-1 text-xs font-semibold text-[#2F5E9E]"
                            >
                              {roleLabels[role]}
                            </span>
                          ))}
                        </div>
                        <Link
                          to={`/organizations/${encodeURIComponent(membership.organization_slug)}/requests/new`}
                          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md bg-[#2F5E9E] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#244B80] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2F5E9E] focus-visible:ring-offset-2"
                        >
                          <Plus size={17} aria-hidden="true" />
                          Submit a request
                        </Link>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}

export default DashboardPage
