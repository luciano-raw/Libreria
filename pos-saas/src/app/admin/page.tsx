import { db } from '@/server/db'
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { getPendingUsers, approveUser, rejectUser, getAllUsers, updateUserRole, deleteUser, suspendUser } from '@/server/actions/admin'
import { startImpersonation } from '@/server/actions/impersonation'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { SignOutButton } from '@clerk/nextjs'
import { LogOut } from 'lucide-react'

export default async function AdminPage() {
    const { userId } = await auth()
    if (!userId) redirect('/sign-in')

    const me = await db.user.findUnique({ where: { id: userId } })
    if (!me?.isSuperAdmin) {
        return <div className="p-8 text-red-500">Acceso Denegado. No eres Super Admin.</div>
    }

    const { users: pendingUsers } = await getPendingUsers()
    const { users: allUsers } = await getAllUsers()

    // Filter logic using serialized dates
    const admins = allUsers?.filter((u: any) => u.isSuperAdmin) || []
    const librarians = allUsers?.filter((u: any) => !u.isSuperAdmin && u.status === 'APPROVED') || []
    const suspended = allUsers?.filter((u: any) => u.status === 'SUSPENDED') || []

    return (
        <div className="min-h-screen bg-zinc-950 text-zinc-100">
            {/* Navbar */}
            <nav className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-purple-600 flex items-center justify-center font-bold text-white shadow-lg shadow-purple-900/20">
                            PM
                        </div>
                        <span className="font-bold text-lg tracking-tight">POS<span className="text-purple-400">Master</span> <span className="text-xs ml-2 px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700">Admin</span></span>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex flex-col items-end mr-2">
                            <span className="text-sm font-medium">{me.name}</span>
                            <span className="text-xs text-zinc-500">{me.email}</span>
                        </div>
                        <SignOutButton signOutOptions={{ redirectUrl: '/sign-in' }}>
                            <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors">
                                <LogOut className="h-4 w-4 mr-2" />
                                Salir
                            </Button>
                        </SignOutButton>
                    </div>
                </div>
            </nav>

            <div className="p-8 max-w-7xl mx-auto space-y-8">
                {/* Pending Requests - Always visible if any */}
                {pendingUsers && pendingUsers.length > 0 && (
                    <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="p-4 border-b border-amber-500/20 bg-amber-500/10 flex justify-between items-center">
                            <h2 className="font-semibold text-amber-200 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                                Solicitudes Pendientes
                            </h2>
                            <Badge className="bg-amber-500 text-white hover:bg-amber-600">{pendingUsers.length}</Badge>
                        </div>
                        <div className="p-4">
                            <Table>
                                <TableHeader className="bg-transparent border-none">
                                    <TableRow className="hover:bg-transparent border-zinc-800">
                                        <TableHead className="text-zinc-400 pl-0">Usuario</TableHead>
                                        <TableHead className="text-zinc-400">Email</TableHead>
                                        <TableHead className="text-right text-zinc-400 pr-0">Acciones</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {pendingUsers.map((user: any) => (
                                        <TableRow key={user.id} className="border-zinc-800 hover:bg-amber-500/5 transition-colors">
                                            <TableCell className="pl-0">
                                                <div className="flex flex-col">
                                                    <span className="font-medium text-zinc-200">{user.name || 'Sin nombre'}</span>
                                                    <span className="text-xs text-zinc-500">
                                                        {new Date(user.createdAt).toLocaleDateString()}
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="text-zinc-400">{user.email}</TableCell>
                                            <TableCell className="text-right pr-0 gap-2 flex justify-end">
                                                <form action={async () => { 'use server'; await rejectUser(user.id) }}>
                                                    <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300 hover:bg-red-500/10 h-8">Rechazar</Button>
                                                </form>
                                                <form action={async () => { 'use server'; await approveUser(user.id) }}>
                                                    <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white border-0 h-8 shadow-lg shadow-emerald-900/20">Aprobar</Button>
                                                </form>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Librarians List */}
                    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 shadow-sm overflow-hidden h-fit">
                        <div className="p-4 border-b border-zinc-800 bg-zinc-900/80 flex justify-between items-center">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-500/10 rounded-lg">
                                    <UsersIcon className="w-5 h-5 text-blue-400" />
                                </div>
                                <h2 className="font-semibold text-zinc-200">Negocios Activos</h2>
                            </div>
                            <Badge variant="secondary" className="bg-zinc-800 text-zinc-300">{librarians.length}</Badge>
                        </div>
                        <div className="max-h-[500px] overflow-y-auto p-2">
                            {librarians.length > 0 ? (
                                <div className="space-y-2">
                                    {librarians.map((user: any) => (
                                        <div key={user.id} className="group p-3 rounded-lg border border-zinc-800/50 bg-zinc-900/50 hover:bg-zinc-800/50 transition-all flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-linear-to-br from-zinc-700 to-zinc-800 flex items-center justify-center text-sm font-bold text-zinc-400 group-hover:from-blue-600 group-hover:to-blue-800 group-hover:text-white transition-all">
                                                    {user.name?.[0]?.toUpperCase() || 'U'}
                                                </div>
                                                <div>
                                                    <div className="text-zinc-200 font-medium text-sm leading-none mb-1">{user.name}</div>
                                                    <div className="text-zinc-500 text-xs">{user.email}</div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                {/* Impersonation Button */}
                                                {user.stores && user.stores[0] && (
                                                    <form action={async () => { 'use server'; await startImpersonation(user.stores[0].storeId) }}>
                                                        <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-600 hover:text-indigo-400 hover:bg-indigo-500/10" title="Acceder como este usuario">
                                                            <LogInIcon className="w-4 h-4" />
                                                        </Button>
                                                    </form>
                                                )}

                                                <form action={async () => { 'use server'; await suspendUser(user.id) }}>
                                                    <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-600 hover:text-amber-500 hover:bg-amber-500/10" title="Suspender Cuenta">
                                                        <PauseCircleIcon className="w-4 h-4" />
                                                    </Button>
                                                </form>
                                                <form action={async () => { 'use server'; await deleteUser(user.id) }}>
                                                    <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-600 hover:text-red-500 hover:bg-red-500/10" title="Eliminar Definitivamente">
                                                        <Trash2Icon className="w-4 h-4" />
                                                    </Button>
                                                </form>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-center text-zinc-600 py-8 text-sm">No hay negocios activos.</p>
                            )}
                        </div>
                    </div>

                    <div className="space-y-8">
                        {/* Suspended Users */}
                        {suspended.length > 0 && (
                            <div className="rounded-xl border border-red-900/30 bg-red-900/5 shadow-sm overflow-hidden">
                                <div className="p-4 border-b border-red-900/20 bg-red-900/10 flex justify-between items-center">
                                    <h2 className="font-semibold text-red-200 text-sm uppercase tracking-wider">Suspendidos</h2>
                                    <Badge variant="outline" className="border-red-500/30 text-red-400">{suspended.length}</Badge>
                                </div>
                                <div className="p-2 space-y-2">
                                    {suspended.map((user: any) => (
                                        <div key={user.id} className="p-3 rounded-lg border border-red-900/20 bg-red-950/30 flex items-center justify-between">
                                            <div className="flex items-center gap-3 opacity-75">
                                                <div className="w-8 h-8 rounded-full bg-red-900/50 flex items-center justify-center text-xs font-bold text-red-400">
                                                    {user.name?.[0]?.toUpperCase() || 'X'}
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-red-200 text-sm font-medium decoration-red-500/50">{user.name}</span>
                                                    <span className="text-red-400/50 text-xs">{user.email}</span>
                                                </div>
                                            </div>
                                            <form action={async () => { 'use server'; await approveUser(user.id) }}>
                                                <Button size="sm" variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/20 h-7 text-xs">
                                                    Reactivar
                                                </Button>
                                            </form>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Admins List (Compact) */}
                        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 shadow-sm overflow-hidden">
                            <div className="p-4 border-b border-zinc-800 bg-zinc-900/80 flex justify-between items-center">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-purple-500/10 rounded-lg">
                                        <ShieldCheckIcon className="w-5 h-5 text-purple-400" />
                                    </div>
                                    <h2 className="font-semibold text-zinc-200">Administradores</h2>
                                </div>
                            </div>
                            <div className="p-2">
                                {admins.map((user: any) => (
                                    <div key={user.id} className="p-3 flex items-center justify-between hover:bg-zinc-800/30 rounded-lg transition-colors">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-purple-900/50 flex items-center justify-center text-xs font-bold text-purple-300">
                                                {user.name?.[0]?.toUpperCase()}
                                            </div>
                                            <div className="text-sm text-zinc-300">{user.email}</div>
                                        </div>
                                        {!user.isSuperAdmin && (
                                            <Button variant="ghost" size="sm" className="h-6 text-xs text-zinc-500">Remover</Button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function Trash2Icon(props: any) {
    return (
        <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /><line x1="10" x2="10" y1="11" y2="17" /><line x1="14" x2="14" y1="11" y2="17" /></svg>
    )
}

function UsersIcon(props: any) {
    return (
        <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
    )
}

function ShieldCheckIcon(props: any) {
    return (
        <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><path d="m9 12 2 2 4-4" /></svg>
    )
}

function PauseCircleIcon(props: any) {
    return (
        <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="10" x2="10" y1="15" y2="9" /><line x1="14" x2="14" y1="15" y2="9" /></svg>
    )
}

function LogInIcon(props: any) {
    return (
        <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" /><polyline points="10 17 15 12 10 7" /><line x1="15" x2="3" y1="12" y2="12" /></svg>
    )
}
