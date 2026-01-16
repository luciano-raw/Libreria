'use client'

import { Button } from "@/components/ui/button"
import { stopImpersonation } from "@/server/actions/impersonation"
import { EyeOff } from "lucide-react"

export default function ImpersonationBanner({ isImpersonating }: { isImpersonating: boolean }) {
    if (!isImpersonating) return null

    return (
        <div className="bg-indigo-600 text-white px-4 py-2 flex items-center justify-between text-sm shadow-md relative z-[100]">
            <div className="flex items-center gap-2 font-medium">
                <EyeOff className="w-4 h-4 animate-pulse" />
                <span>Modo de Acceso Administrativo Activo</span>
            </div>
            <Button
                size="sm"
                variant="secondary"
                onClick={() => stopImpersonation()}
                className="h-7 text-xs bg-white text-indigo-600 hover:bg-indigo-50 border-0"
            >
                Salir del Modo Admin
            </Button>
        </div>
    )
}
