import type { ReactNode } from 'react'
import Footer from '../shared/components/Footer'
import Navbar from '../shared/components/Navbar'

type AppLayoutProps = {
  children: ReactNode
}

const AppLayout = ({ children }: AppLayoutProps) => {
  return (
    <div className="min-h-screen bg-white font-sans text-[#1E293B] antialiased">
      <Navbar />
      <main>{children}</main>
      <Footer />
    </div>
  )
}

export default AppLayout
