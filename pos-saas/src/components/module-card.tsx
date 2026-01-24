'use client'

import Link from 'next/link'
import { Lock } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface ModuleCardProps {
    href: string
    title: string
    description: string
    icon: React.ReactNode
    bgIcon: React.ReactNode
    color: 'indigo' | 'pink' | 'emerald' | 'amber'
    isLocked?: boolean
}

export function ModuleCard({ href, title, description, icon, bgIcon, color, isLocked }: ModuleCardProps) {
    const { toast } = useToast()

    // Original styling logic
    const borderColors = {
        indigo: 'hover:border-indigo-500/50',
        pink: 'hover:border-pink-500/50',
        emerald: 'hover:border-emerald-500/50',
        amber: 'hover:border-amber-500/50',
    }

    const iconBgColors = {
        indigo: 'bg-indigo-500/10 group-hover:bg-indigo-500 group-hover:text-white',
        pink: 'bg-pink-500/10 group-hover:bg-pink-500 group-hover:text-white',
        emerald: 'bg-emerald-500/10 group-hover:bg-emerald-500 group-hover:text-white',
        amber: 'bg-amber-500/10 group-hover:bg-amber-500 group-hover:text-white',
    }

    const titleColors = {
        indigo: 'group-hover:text-indigo-400',
        pink: 'group-hover:text-pink-400',
        emerald: 'group-hover:text-emerald-400',
        amber: 'group-hover:text-amber-400',
    }

    if (isLocked) {
        return (
            <div
                onClick={() => toast({ title: "Módulo Bloqueado", description: "No tienes permiso para acceder a este módulo. Contacta a tu administrador.", variant: "destructive" })}
                className="h-full bg-zinc-950 border border-zinc-900 rounded-xl p-6 opacity-60 grayscale cursor-not-allowed relative overflow-hidden transition-all hover:bg-zinc-900/50"
            >
                <div className="absolute top-4 right-4 text-zinc-600">
                    <Lock className="w-6 h-6" />
                </div>

                {/* Background Icon (Faint) */}
                <div className="absolute top-0 right-0 p-3 opacity-5 pointer-events-none">
                    {bgIcon}
                </div>

                <div className={`w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center text-zinc-600 mb-4`}>
                    {icon}
                </div>
                <h3 className="font-semibold text-lg text-zinc-500 mb-2">{title}</h3>
                <p className="text-sm text-zinc-600">{description}</p>
            </div>
        )
    }

    return (
        <Link href={href} className="group">
            <div className={`h-full bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:bg-zinc-800 ${borderColors[color]} transition-all cursor-pointer relative overflow-hidden`}>
                <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                    {bgIcon}
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${iconBgColors[color]} mb-4 transition-colors`}>
                    {icon}
                </div>
                <h3 className={`font-semibold text-lg text-zinc-100 mb-2 ${titleColors[color]} transition-colors`}>{title}</h3>
                <p className="text-sm text-zinc-400">{description}</p>
            </div>
        </Link>
    )
}
