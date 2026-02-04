"use client"

import { ReactNode, useState } from 'react'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

interface AuthLayoutProps {
    children: ReactNode
    title?: string
    subtitle?: string
}

export function AuthLayout({ children }: AuthLayoutProps) {
    const [expandedMember, setExpandedMember] = useState<string | null>(null);

    const toggleMember = (name: string) => {
        if (expandedMember === name) {
            setExpandedMember(null);
        } else {
            setExpandedMember(name);
        }
    };

    return (
        <div className="flex min-h-screen w-full">
            {/* Left Side - Marketing/Branding - EXPANDED WIDTH (60%) */}
            <div className="hidden lg:flex lg:w-[60%] flex-col bg-zinc-950 text-white relative overflow-hidden transition-all duration-500 ease-in-out">
                {/* Background Effects */}
                <div className="absolute top-[-20%] left-[-20%] w-[80%] h-[80%] rounded-full bg-indigo-600/20 blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full bg-purple-600/20 blur-[100px]" />

                {/* Content Container - Scrollable with Fade Mask */}
                <div className="relative z-10 flex-1 overflow-hidden flex flex-col">
                    {/* Fade Mask Top */}
                    <div className="absolute top-0 left-0 w-full h-12 bg-gradient-to-b from-zinc-950 to-transparent z-20 pointer-events-none" />

                    <div className="flex-1 overflow-y-auto p-16 pb-32 scrollbar-none">
                        <div className="flex items-center gap-3 mb-10 pt-2">
                            <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-900/40">
                                PM
                            </div>
                            <span className="text-2xl font-bold tracking-tight">POS<span className="text-indigo-400">Master</span></span>
                        </div>

                        <div className="space-y-12 max-w-2xl">
                            {/* Intro Section */}
                            <div className="space-y-6">
                                <h1 className="text-6xl font-extrabold tracking-tight leading-tight">
                                    Potencia tu negocio con <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">POS Master</span>
                                </h1>
                                <p className="text-xl text-zinc-400 leading-relaxed font-light">
                                    La solución integral para la gestión moderna de empresas. Diseñado para simplificar tus operaciones y maximizar tus ventas.
                                </p>
                            </div>

                            {/* Features Section */}
                            <div className="grid grid-cols-1 gap-8">
                                <div className="space-y-3 p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                    <h3 className="text-2xl font-semibold text-indigo-300 flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-300">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" /></svg>
                                        </div>
                                        Gestión de Ventas
                                    </h3>
                                    <p className="text-zinc-400 text-lg leading-relaxed">
                                        Realiza ventas rápidas y eficientes desde cualquier dispositivo. Nuestro punto de venta está optimizado para la velocidad y facilidad de uso.
                                    </p>
                                </div>

                                <div className="space-y-3 p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                    <h3 className="text-2xl font-semibold text-pink-300 flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-pink-500/20 text-pink-300">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" x2="8" y1="13" y2="13" /><line x1="16" x2="8" y1="17" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>
                                        </div>
                                        Cotizaciones Profesionales
                                    </h3>
                                    <p className="text-zinc-400 text-lg leading-relaxed">
                                        Genera cotizaciones formales en segundos. Descarga PDFs personalizados y conviértelos en ventas con un solo clic.
                                    </p>
                                </div>

                                <div className="space-y-3 p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                    <h3 className="text-2xl font-semibold text-emerald-300 flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-300">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" x2="16" y1="21" y2="21" /><line x1="12" x2="12" y1="17" y2="21" /></svg>
                                        </div>
                                        Control de Inventario
                                    </h3>
                                    <p className="text-zinc-400 text-lg leading-relaxed">
                                        Mantén tu stock siempre actualizado. Controla precios, variantes y disponibilidad en tiempo real para evitar quiebres de stock.
                                    </p>
                                </div>
                            </div>

                            {/* Team Section */}
                            <div className="pt-10">
                                <h3 className="text-3xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-400">
                                    Nuestro Equipo
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Card 1: Luciano */}
                                    <TeamCard
                                        name="Luciano Gonzalez"
                                        role="Ing. Civil Informático"
                                        location="Talca, Chile"
                                        image="/team/luciano.PNG"
                                        color="indigo"
                                        linkedin="https://www.linkedin.com/in/lucianomgr/"
                                        isExpanded={expandedMember === 'luciano'}
                                        onToggle={() => toggleMember('luciano')}
                                    />

                                    {/* Card 2: Fernanda */}
                                    <TeamCard
                                        name="Fernanda Parada"
                                        role="Estudiante de Administración"
                                        location="Talca, Chile"
                                        image="/team/fernanda.PNG"
                                        color="pink"
                                        linkedin="https://www.linkedin.com/in/fernanda-parada-7036a9394/"
                                        isExpanded={expandedMember === 'fernanda'}
                                        onToggle={() => toggleMember('fernanda')}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Fade Mask Bottom */}

                </div>

                {/* Fixed Footer for Contact */}
                <div className="relative z-30 p-8 bg-zinc-950/95 backdrop-blur-md shadow-[0_-20px_40px_-15px_rgba(0,0,0,0.8)]">
                    <p className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-3">Contacto & Soporte</p>
                    <div className="flex flex-col gap-2 text-zinc-400 text-base">
                        <div className="flex items-center gap-3 hover:text-white transition-colors cursor-pointer group">
                            <div className="p-2 rounded-full bg-zinc-900 group-hover:bg-zinc-800 transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" /></svg>
                            </div>
                            <span>+56 9 3053 1304</span>
                        </div>
                        <div className="flex items-center gap-3 hover:text-white transition-colors cursor-pointer group">
                            <div className="p-2 rounded-full bg-zinc-900 group-hover:bg-zinc-800 transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4" /><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94" /></svg>
                            </div>
                            <span>luciano.raw04@gmail.com</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side - Auth Form - COMPACT WIDTH (40%) */}
            <div className="flex-1 lg:w-[40%] flex flex-col items-center justify-center p-4 sm:p-8 bg-zinc-950 relative z-20 shadow-[-20px_0_80px_0px_rgba(0,0,0,0.8)]">
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

                <div className="w-full max-w-sm relative z-10">
                    {children}
                </div>
            </div>
        </div>
    )
}

function TeamCard({ name, role, location, image, color, linkedin, isExpanded, onToggle }: any) {
    const borderColor = color === 'indigo' ? 'group-hover:border-indigo-500/50' : 'group-hover:border-pink-500/50';
    const textColor = color === 'indigo' ? 'text-indigo-400' : 'text-pink-400';
    const ringColor = color === 'indigo' ? 'border-indigo-500/30' : 'border-pink-500/30';
    const btnColor = color === 'indigo' ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-pink-600 hover:bg-pink-700';

    return (
        <motion.div
            layout
            onClick={onToggle}
            className={cn(
                "bg-zinc-900/40 backdrop-blur-sm border border-zinc-800/50 rounded-2xl overflow-hidden cursor-pointer transition-colors group relative",
                isExpanded ? "bg-zinc-900/80 border-zinc-700" : "hover:bg-zinc-900/60"
            )}
        >
            <motion.div layout className="p-6 flex flex-col items-center text-center gap-4">
                <motion.div
                    layout
                    className={cn(
                        "rounded-full bg-zinc-800 overflow-hidden relative border-2 shrink-0 transition-all duration-500 shadow-xl",
                        ringColor,
                        isExpanded ? "h-32 w-32" : "h-24 w-24"
                    )}
                >
                    <Image
                        src={image}
                        alt={name}
                        fill
                        className="object-cover"
                    />
                </motion.div>

                <div className="w-full pt-2">
                    <motion.h4 layout className="text-white font-bold text-xl mb-1">{name}</motion.h4>
                    <motion.p layout className={cn("font-medium text-base mb-2", textColor)}>{role}</motion.p>
                    <motion.p layout className="text-zinc-500 text-sm flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" /><circle cx="12" cy="10" r="3" /></svg>
                        {location}
                    </motion.p>

                    <AnimatePresence>
                        {isExpanded && (
                            <motion.div
                                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                                animate={{ opacity: 1, height: 'auto', marginTop: 24 }}
                                exit={{ opacity: 0, height: 0, marginTop: 0 }}
                                className="overflow-hidden w-full"
                            >
                                <a
                                    href={linkedin}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    className={cn(
                                        "inline-flex items-center gap-2 text-sm font-bold text-white px-6 py-3 rounded-xl transition-all w-full justify-center shadow-lg hover:scale-[1.02]",
                                        btnColor
                                    )}
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" /><rect x="2" y="9" width="4" height="12" /><circle cx="4" cy="4" r="2" /></svg>
                                    Conectar en LinkedIn
                                </a>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <motion.div
                    layout
                    className="absolute top-4 right-4 text-zinc-600 group-hover:text-zinc-400 transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={cn("transition-transform duration-300", isExpanded ? "rotate-180" : "")}><path d="m6 9 6 6 6-6" /></svg>
                </motion.div>
            </motion.div>
        </motion.div>
    )
}
