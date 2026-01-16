'use client' // Error components must be Client Components

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error('Admin Page Error:', error)
    }, [error])

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-950 text-red-500 p-6 text-center">
            <h2 className="text-3xl font-bold mb-4">¡Algo salió mal!</h2>
            <p className="mb-4 text-zinc-400 max-w-md">
                Ocurrió un error al cargar el panel de administración.
                <br />
                <span className="text-sm font-mono bg-zinc-900 p-1 rounded mt-2 block overflow-x-auto">
                    {error.message || 'Error desconocido'}
                </span>
            </p>
            <Button
                variant="outline"
                onClick={
                    // Attempt to recover by trying to re-render the segment
                    () => reset()
                }
                className="border-red-500 text-red-500 hover:bg-red-950"
            >
                Intentar de nuevo
            </Button>
        </div>
    )
}
