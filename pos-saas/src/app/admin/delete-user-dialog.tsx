'use client'

import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { deleteUser } from '@/server/actions/admin'
import { useToast } from '@/hooks/use-toast'

export function DeleteUserDialog({ userId, userName }: { userId: string, userName: string }) {
    const [open, setOpen] = useState(false)
    const { toast } = useToast()

    const handleDelete = async () => {
        try {
            const res = await deleteUser(userId)
            if (res.success) {
                toast({ title: 'Usuario eliminado', description: `Se ha eliminado a ${userName}.` })
            } else {
                toast({ title: 'Error', description: res.message, variant: 'destructive' })
            }
        } catch (error) {
            toast({ title: 'Error', description: 'Ocurrió un error inesperado', variant: 'destructive' })
        } finally {
            setOpen(false)
        }
    }

    return (
        <AlertDialog open={open} onOpenChange={setOpen}>
            <AlertDialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-600 hover:text-red-500 hover:bg-red-500/10" title="Eliminar Definitivamente">
                    <Trash2 className="w-4 h-4" />
                </Button>
            </AlertDialogTrigger>
            <AlertDialogContent className="bg-zinc-900 border-zinc-800 text-zinc-100">
                <AlertDialogHeader>
                    <AlertDialogTitle>¿Estás completamente seguro?</AlertDialogTitle>
                    <AlertDialogDescription className="text-zinc-400">
                        Esta acción no se puede deshacer. Se eliminará permanentemente al usuario <strong>{userName}</strong> y todos sus datos asociados.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel className="bg-transparent border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white">Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700 text-white border-0">Eliminar</AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}
