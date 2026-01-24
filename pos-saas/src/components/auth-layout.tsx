import { ReactNode } from 'react'

interface AuthLayoutProps {
    children: ReactNode
    title?: string
    subtitle?: string
}

export function AuthLayout({ children }: AuthLayoutProps) {
    return (
        <div className="flex min-h-screen w-full">
            {/* Left Side - Marketing/Branding */}
            <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-zinc-950 p-12 relative overflow-hidden text-white">
                {/* Background Effects */}
                <div className="absolute top-[-20%] left-[-20%] w-[80%] h-[80%] rounded-full bg-indigo-600/20 blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full bg-purple-600/20 blur-[100px]" />

                {/* Content */}
                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-10">
                        <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-900/40">
                            PM
                        </div>
                        <span className="text-2xl font-bold tracking-tight">POS<span className="text-indigo-400">Master</span></span>
                    </div>

                    <div className="space-y-6 max-w-lg">
                        <h1 className="text-5xl font-extrabold tracking-tight leading-tight">
                            Tu sistema de venta e inventario web, <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">simple y completo</span>
                        </h1>
                        <p className="text-lg text-zinc-400 leading-relaxed">
                            Gestiona tus ventas, controla tu inventario y haz crecer tu negocio con una plataforma diseñada para ser potente pero fácil de usar.
                        </p>
                    </div>
                </div>

                {/* Contact Info Footer */}
                <div className="relative z-10 space-y-2 border-t border-zinc-900 pt-8">
                    <p className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-3">Contacto & Soporte</p>
                    <div className="flex flex-col gap-2 text-zinc-400">
                        <div className="flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" /></svg>
                            <span>+56 9 3053 1304</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4" /><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94" /></svg>
                            <span>luciano.raw04@gmail.com</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side - Auth Form */}
            <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-8 bg-zinc-950 relative">
                <div className="absolute top-0 right-0 w-full h-full lg:hidden overflow-hidden pointer-events-none">
                    <div className="absolute top-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-indigo-600/10 blur-[80px]" />
                </div>

                {/* Mobile Logo (Visible only on small screens) */}
                <div className="lg:hidden mb-8 flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white">
                        PM
                    </div>
                    <span className="text-xl font-bold text-white tracking-tight">POS<span className="text-indigo-400">Master</span></span>
                </div>

                <div className="w-full max-w-md relative z-10">
                    {children}
                </div>
            </div>
        </div>
    )
}
