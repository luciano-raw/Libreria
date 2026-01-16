'use client'

import { useState } from 'react'
import { addProduct } from '@/server/actions/products'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { useRouter } from 'next/navigation'

export function ProductForm() {
    const router = useRouter()
    const [loading, setLoading] = useState(false)

    // Simple state for now
    const [formData, setFormData] = useState({
        name: '',
        barcode: '',
        brand: '',
        price: '',
        stock: '',
        description: ''
    })

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.id]: e.target.value })
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        setLoading(true)

        const res = await addProduct({
            name: formData.name,
            barcode: formData.barcode || null,
            brand: formData.brand || null,
            description: formData.description || null,
            price: parseFloat(formData.price),
            stock: parseInt(formData.stock) || 0
        })

        if (res.success) {
            alert('Producto guardado')
            router.push('/inventory')
            router.refresh()
        } else {
            alert(res.message)
            setLoading(false)
        }
    }

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Nuevo Producto</CardTitle>
            </CardHeader>
            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="barcode">Código de Barras</Label>
                            <Input id="barcode" placeholder="Escanear..." value={formData.barcode} onChange={handleChange} />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="brand">Marca</Label>
                            <Input id="brand" placeholder="Ej. Bic" value={formData.brand} onChange={handleChange} />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="name">Nombre / Modelo *</Label>
                        <Input id="name" placeholder="Ej. Lápiz Negro HB" value={formData.name} onChange={handleChange} required />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="price">Precio Venta *</Label>
                            <Input id="price" type="number" step="0.01" placeholder="0.00" value={formData.price} onChange={handleChange} required />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="stock">Stock Inicial *</Label>
                            <Input id="stock" type="number" placeholder="0" value={formData.stock} onChange={handleChange} required />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="description">Descripción</Label>
                        <Textarea id="description" placeholder="Detalles adicionales..." value={formData.description} onChange={handleChange} />
                    </div>

                </CardContent>
                <CardFooter className="flex justify-between">
                    <Button variant="outline" type="button" onClick={() => router.back()}>Cancelar</Button>
                    <Button type="submit" disabled={loading}>
                        {loading ? 'Guardando...' : 'Guardar Producto'}
                    </Button>
                </CardFooter>
            </form>
        </Card>
    )
}
