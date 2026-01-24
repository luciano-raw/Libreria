'use client'

import { useState } from 'react'
import { LayoutGrid } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { updateUserPermissions } from '@/server/actions/admin' // This will be called from client
import { useToast } from '@/hooks/use-toast'

const MODULES = [
    { id: 'sales', label: 'Ventas (POS)' },
    { id: 'inventory', label: 'Inventario' },
    { id: 'history', label: 'Historial' },
    { id: 'quotes', label: 'Cotizaciones' },
]

export function ClientPermissionsDialog({ user }: { user: any }) {
    const [open, setOpen] = useState(false)
    const { toast } = useToast()

    // Get initial permissions from the first store relation (assuming single store for now)
    const initialPermissions = user.stores?.[0]?.permissions || []
    const [selectedPermissions, setSelectedPermissions] = useState<string[]>(initialPermissions)

    const handleToggle = (moduleId: string) => {
        setSelectedPermissions(current =>
            current.includes(moduleId)
                ? current.filter(id => id !== moduleId)
                : [...current, moduleId]
        )
    }

    const handleSave = async () => {
        try {
            const res = await updateUserPermissions(user.id, selectedPermissions)
            if (res.success) {
                toast({ title: 'Permisos actualizados', description: `Módulos actualizados para ${user.name}` })
                setOpen(false)
            } else {
                toast({ title: 'Error', description: res.message, variant: 'destructive' })
            }
        } catch (error) {
            toast({ title: 'Error', description: 'Ocurrió un error inesperado', variant: 'destructive' })
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-600 hover:text-indigo-400 hover:bg-indigo-500/10" title="Gestionar Módulos">
                    <LayoutGrid className="w-4 h-4" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md bg-zinc-900 border-zinc-800 text-zinc-100">
                <DialogHeader>
                    <DialogTitle>Gestionar Módulos</DialogTitle>
                    <DialogDescription className="text-zinc-400">
                        Selecciona qué módulos puede ver <strong>{user.name}</strong>.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    {MODULES.map((module) => (
                        <div key={module.id} className="flex items-center space-x-2 p-3 rounded-lg border border-zinc-800 bg-zinc-950/50 hover:bg-zinc-900/50 transition-colors cursor-pointer" onClick={() => handleToggle(module.id)}>
                            <Checkbox
                                id={module.id}
                                checked={selectedPermissions.includes(module.id)}
                                onCheckedChange={() => handleToggle(module.id)}
                                className="border-zinc-600 data-[state=checked]:bg-indigo-600 data-[state=checked]:border-indigo-600"
                            />
                            <Label htmlFor={module.id} className="flex-1 cursor-pointer text-zinc-300 font-medium">
                                {module.label}
                            </Label>
                        </div>
                    ))}
                </div>
                <DialogFooter>
                    <Button variant="ghost" onClick={() => setOpen(false)} className="text-zinc-400 hover:text-white">Cancelar</Button>
                    <Button onClick={handleSave} className="bg-indigo-600 hover:bg-indigo-700 text-white">Guardar Cambios</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
