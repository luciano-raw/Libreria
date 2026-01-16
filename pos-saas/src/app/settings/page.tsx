'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { getStoreSettings, updateStoreSettings } from '@/server/actions/store'
import Link from 'next/link'

export default function SettingsPage() {
    const [primaryColor, setPrimaryColor] = useState('#18181b')
    const [secondaryColor, setSecondaryColor] = useState('#27272a')
    const [isLoading, setIsLoading] = useState(true)
    const [isSaving, setIsSaving] = useState(false)
    const { toast } = useToast()

    useEffect(() => {
        loadSettings()
    }, [])

    async function loadSettings() {
        const res = await getStoreSettings()
        if (res.success && res.settings) {
            setPrimaryColor((res.settings as any).pdfPrimaryColor || '#18181b')
            setSecondaryColor((res.settings as any).pdfSecondaryColor || '#27272a')
        }
        setIsLoading(false)
    }

    async function handleSave() {
        setIsSaving(true)
        const res = await updateStoreSettings({
            pdfPrimaryColor: primaryColor,
            pdfSecondaryColor: secondaryColor
        })

        if (res.success) {
            toast({ title: "Guardado", description: "La configuración de la tienda ha sido actualizada." })
        } else {
            toast({ title: "Error", description: "No se pudo guardar la configuración.", variant: "destructive" })
        }
        setIsSaving(false)
    }

    if (isLoading) return <div className="p-8 text-zinc-400">Cargando configuración...</div>

    return (
        <div className="p-8 max-w-4xl mx-auto min-h-screen bg-zinc-950 text-zinc-100">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-zinc-100">Configuración</h2>
                    <p className="text-zinc-400">Personaliza tu tienda y documentos.</p>
                </div>
                <Link href="/">
                    <Button variant="outline" className="border-zinc-800 text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100">
                        ← Volver al Inicio
                    </Button>
                </Link>
            </div>

            <div className="space-y-6">
                <Card className="bg-zinc-900 border-zinc-800">
                    <CardHeader>
                        <CardTitle className="text-zinc-100">Personalización de PDF</CardTitle>
                        <CardDescription className="text-zinc-400">
                            Elige los colores que se usarán en tus cotizaciones y reportes PDF.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <Label className="text-zinc-300">Color Principal (Cabeceras)</Label>
                                <div className="flex gap-3">
                                    <div
                                        className="w-12 h-12 rounded-lg border border-zinc-700 shadow-inner"
                                        style={{ backgroundColor: primaryColor }}
                                    />
                                    <Input
                                        type="color"
                                        className="h-12 w-24 bg-zinc-950 border-zinc-800 cursor-pointer p-1"
                                        value={primaryColor}
                                        onChange={(e) => setPrimaryColor(e.target.value)}
                                    />
                                    <Input
                                        type="text"
                                        className="h-12 flex-1 bg-zinc-950 border-zinc-800 font-mono"
                                        value={primaryColor}
                                        onChange={(e) => setPrimaryColor(e.target.value)}
                                    />
                                </div>
                                <p className="text-xs text-zinc-500">Se usará para la barra superior y títulos.</p>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-zinc-300">Color Secundario (Tablas)</Label>
                                <div className="flex gap-3">
                                    <div
                                        className="w-12 h-12 rounded-lg border border-zinc-700 shadow-inner"
                                        style={{ backgroundColor: secondaryColor }}
                                    />
                                    <Input
                                        type="color"
                                        className="h-12 w-24 bg-zinc-950 border-zinc-800 cursor-pointer p-1"
                                        value={secondaryColor}
                                        onChange={(e) => setSecondaryColor(e.target.value)}
                                    />
                                    <Input
                                        type="text"
                                        className="h-12 flex-1 bg-zinc-950 border-zinc-800 font-mono"
                                        value={secondaryColor}
                                        onChange={(e) => setSecondaryColor(e.target.value)}
                                    />
                                </div>
                                <p className="text-xs text-zinc-500">Se usará para las cabeceras de las tablas.</p>
                            </div>
                        </div>

                        <div className="pt-4 flex justify-end">
                            <Button
                                onClick={handleSave}
                                disabled={isSaving}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white min-w-[150px]"
                            >
                                {isSaving ? 'Guardando...' : 'Guardar Cambios'}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
