import { auth, currentUser } from '@clerk/nextjs/server'
import { db } from '@/server/db'
import { isImpersonating, getActiveStoreId, getUserPermissions } from '@/server/auth'
import { OnboardingForm } from '@/components/onboarding-form'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { SignOutButton } from '@clerk/nextjs'
import { Button } from '@/components/ui/button'
import { ModuleCard } from '@/components/module-card'

export default async function Home() {
  const user = await currentUser()
  if (!user) redirect('/sign-in')

  // 1. Sync User to DB (if not exists)
  // ... (rest of the file remains similar) ...
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
  const impersonating = await isImpersonating()
  if (dbUser.isSuperAdmin && !impersonating) {
    redirect('/admin')
  }

  // 3. Status Gates
  if (dbUser.status === 'PENDING') {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center bg-zinc-950 text-zinc-100 relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-[-20%] left-[-20%] w-[80%] h-[80%] rounded-full bg-indigo-600/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full bg-purple-600/10 blur-[100px]" />

        <div className="relative z-10 max-w-md w-full">
          <div className="mb-8 flex justify-center">
            <div className="h-16 w-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center shadow-2xl shadow-indigo-900/30">
              <span className="text-3xl">⏳</span>
            </div>
          </div>

          <h1 className="text-3xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-400">Solicitud en Revisión</h1>
          <p className="text-zinc-400 mb-8 text-lg leading-relaxed">
            Hemos recibido tu registro. Un administrador debe aprobar tu cuenta para que puedas acceder al sistema.
          </p>

          <div className="p-6 bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 rounded-xl mb-8 shadow-lg">
            <div className="space-y-3 text-left">
              <div className="flex justify-between items-center border-b border-zinc-800 pb-2">
                <span className="text-zinc-500 text-sm">Usuario</span>
                <span className="text-zinc-200 font-medium">{user.firstName} {user.lastName}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-500 text-sm">Email</span>
                <span className="text-zinc-200 font-medium">{dbUser.email}</span>
              </div>
              <div className="pt-2 flex justify-center">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-500/10 text-yellow-500 border border-yellow-500/20">
                  Pendiente de Aprobación
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <SignOutButton signOutOptions={{ redirectUrl: '/sign-in' }}>
              <Button className="w-full bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700 h-11">
                Volver al Inicio de Sesión
              </Button>
            </SignOutButton>
            <p className="text-xs text-zinc-600 mt-4">
              Te enviaremos una notificación cuando tu cuenta esté activa.
            </p>
          </div>
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

  // 4. Approved Users -> Check Store / Impersonation
  let storeId: string | undefined
  try {
    storeId = await getActiveStoreId()
  } catch (err) {
    // User has no store
  }

  // 5. If Approved but no store -> Show Onboarding
  if (!storeId) {
    return <OnboardingForm />
  }

  // 6. Dashboard (Approved & Has Store)
  const permissions = await getUserPermissions()

  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 text-zinc-100">
      {/* Header code remains same ... */}
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

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <ModuleCard
              href="/sales"
              title="Nueva Venta"
              description="Punto de venta, caja, descuentos y boletas."
              icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" /></svg>}
              bgIcon={<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-400"><circle cx="8" cy="21" r="1" /><circle cx="19" cy="21" r="1" /><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" /></svg>}
              color="indigo"
              isLocked={!permissions.includes('sales')}
            />

            <ModuleCard
              href="/quotes"
              title="Cotizaciones"
              description="Historial y generación de documentos PDF."
              icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" /><polyline points="14 2 14 8 20 8" /></svg>}
              bgIcon={<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-pink-400"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" x2="8" y1="13" y2="13" /><line x1="16" x2="8" y1="17" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>}
              color="pink"
              isLocked={!permissions.includes('quotes')}
            />

            <ModuleCard
              href="/inventory"
              title="Inventario"
              description="Gestionar productos, stock y precios."
              icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" x2="16" y1="21" y2="21" /><line x1="12" x2="12" y1="17" y2="21" /></svg>}
              bgIcon={<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-400"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /><polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" x2="12" y1="22.08" y2="12" /></svg>}
              color="emerald"
              isLocked={!permissions.includes('inventory')}
            />

            <ModuleCard
              href="/sales/history"
              title="Historial"
              description="Revisar ventas pasadas y detalles."
              icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>}
              bgIcon={<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-400"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>}
              color="amber"
              isLocked={!permissions.includes('history')}
            />
          </div>
        </div>
      </main>
    </div>
  )
}

function LockIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>
  )
}
