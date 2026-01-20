import { auth, currentUser } from '@clerk/nextjs/server'
import { db } from '@/server/db'
import { OnboardingForm } from '@/components/onboarding-form'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { SignOutButton } from '@clerk/nextjs'
import { Button } from '@/components/ui/button'

export default async function Home() {
  const user = await currentUser()
  if (!user) redirect('/sign-in')

  // 1. Sync User to DB (if not exists)
  // This ensures they appear in the Admin Panel as PENDING
  let dbUser = await db.user.findUnique({ where: { id: user.id } })

  if (!dbUser) {
    dbUser = await db.user.create({
      data: {
        id: user.id,
        email: user.emailAddresses[0].emailAddress,
        name: `${user.firstName} ${user.lastName}`.trim(),
        status: 'PENDING'
      }
    })
  }

  // 2. Super Admin Redirect
  if (dbUser.isSuperAdmin) {
    redirect('/admin')
  }

  // 3. Status Gates
  if (dbUser.status === 'PENDING') {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center bg-gray-50">
        <h1 className="text-2xl font-bold mb-2">⏳ Solicitud Recibida</h1>
        <p className="text-muted-foreground max-w-md mb-6">
          Tu cuenta ha sido creada, pero requiere aprobación del Administrador para activar tu negocio.
          <br />Te notificaremos cuando esté lista.
        </p>
        <div className="p-4 bg-white border rounded shadow-sm text-sm text-left w-full max-w-sm">
          <p><strong>ID:</strong> {user.id}</p>
          <p><strong>Email:</strong> {dbUser.email}</p>
          <p className="text-yellow-600 mt-2">Estado: Pendiente de Aprobación</p>
        </div>
        <div className="mt-8">
          <SignOutButton signOutOptions={{ redirectUrl: '/sign-in' }}>
            <Button variant="outline">Cerrar Sesión</Button>
          </SignOutButton>
        </div>
      </div>
    )
  }

  if (dbUser.status === 'REJECTED') {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center text-red-600 bg-red-50">
        <h1 className="text-3xl font-bold mb-2">❌ Solicitud Rechazada</h1>
        <p className="text-red-800">Lo sentimos, tu solicitud ha sido rechazada.</p>
        <p className="text-sm text-red-600 mt-4">Ponte en contacto con el administrador si crees que es un error.</p>
        <div className="mt-8">
          <SignOutButton signOutOptions={{ redirectUrl: '/' }}>
            <Button variant="outline" className="border-red-200 text-red-700 hover:bg-red-100">Cerrar Sesión</Button>
          </SignOutButton>
        </div>
      </div>
    )
  }

  if ((dbUser.status as any) === 'SUSPENDED') {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center bg-gray-900 text-white">
        <div className="p-4 rounded-full bg-amber-500/20 mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-500"><circle cx="12" cy="12" r="10" /><line x1="10" x2="10" y1="15" y2="9" /><line x1="14" x2="14" y1="15" y2="9" /></svg>
        </div>
        <h1 className="text-3xl font-bold mb-2">Cuenta Suspendida</h1>
        <p className="text-zinc-400 max-w-md">Tu acceso ha sido pausado temporalmente por un administrador.</p>
        <div className="mt-8">
          <SignOutButton signOutOptions={{ redirectUrl: '/sign-in' }}>
            <Button variant="outline" className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white">Cerrar Sesión</Button>
          </SignOutButton>
        </div>
      </div>
    )
  }

  // 4. Approved Users -> Check Store
  const userStore = await db.storeUser.findFirst({
    where: { userId: user.id },
    include: { store: true }
  })

  // 5. If Approved but no store -> Show Onboarding
  if (!userStore) {
    return <OnboardingForm />
  }

  // 6. Dashboard (Approved & Has Store)
  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-900/20">
              PM
            </div>
            <span className="font-bold text-lg tracking-tight">POS<span className="text-indigo-400">Master</span></span>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex flex-col items-end mr-2">
              <span className="text-sm font-medium">{user.firstName} {user.lastName}</span>
              <span className="text-xs text-zinc-500">{user.emailAddresses[0].emailAddress}</span>
            </div>
            <SignOutButton signOutOptions={{ redirectUrl: '/sign-in' }}>
              <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors">
                Cerrar Sesión
              </Button>
            </SignOutButton>
          </div>
        </div>
      </header>

      <main className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-10">
            <h2 className="text-3xl font-bold text-primary mb-2">Hola, {user.firstName}.</h2>
            <p className="text-muted-foreground">¿Qué te gustaría hacer hoy?</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/sales" className="group">
              <div className="h-full bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:bg-zinc-800 hover:border-indigo-500/50 transition-all cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                  <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-400"><circle cx="8" cy="21" r="1" /><circle cx="19" cy="21" r="1" /><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" /></svg>
                </div>
                <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-4 group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" /></svg>
                </div>
                <h3 className="font-semibold text-lg text-zinc-100 mb-2 group-hover:text-indigo-400 transition-colors">Nueva Venta</h3>
                <p className="text-sm text-zinc-400">Punto de venta, caja, descuentos y boletas.</p>
              </div>
            </Link>

            <Link href="/quotes" className="group">
              <div className="h-full bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:bg-zinc-800 hover:border-pink-500/50 transition-all cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                  <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-pink-400"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" x2="8" y1="13" y2="13" /><line x1="16" x2="8" y1="17" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>
                </div>
                <div className="w-12 h-12 rounded-lg bg-pink-500/10 flex items-center justify-center text-pink-400 mb-4 group-hover:bg-pink-500 group-hover:text-white transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" /><polyline points="14 2 14 8 20 8" /></svg>
                </div>
                <h3 className="font-semibold text-lg text-zinc-100 mb-2 group-hover:text-pink-400 transition-colors">Cotizaciones</h3>
                <p className="text-sm text-zinc-400">Historial y generación de documentos PDF.</p>
              </div>
            </Link>

            <Link href="/inventory" className="group">
              <div className="h-full bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:bg-zinc-800 hover:border-emerald-500/50 transition-all cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                  <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-400"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /><polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" x2="12" y1="22.08" y2="12" /></svg>
                </div>
                <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-4 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" x2="16" y1="21" y2="21" /><line x1="12" x2="12" y1="17" y2="21" /></svg>
                </div>
                <h3 className="font-semibold text-lg text-zinc-100 mb-2 group-hover:text-emerald-400 transition-colors">Inventario</h3>
                <p className="text-sm text-zinc-400">Gestionar productos, stock y precios.</p>
              </div>
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}
