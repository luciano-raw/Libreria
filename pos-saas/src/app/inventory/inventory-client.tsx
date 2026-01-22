'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { updateProduct, deleteProduct, ProductData } from '@/server/actions/products'
import { Trash2, Edit, Search } from 'lucide-react'

type InventoryClientProps = {
    initialProducts: any[]
}

export default function InventoryClient({ initialProducts }: InventoryClientProps) {
    const [products, setProducts] = useState(initialProducts)
    const [editingProduct, setEditingProduct] = useState<any | null>(null)
    const [isEditOpen, setIsEditOpen] = useState(false)
    const [formLoading, setFormLoading] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const { toast } = useToast()
    const router = useRouter() // Use router to refresh if needed, though we update local state

    const filteredProducts = products.filter(product => {
        const query = searchQuery.toLowerCase()
        return (
            product.name.toLowerCase().includes(query) ||
            (product.brand && product.brand.toLowerCase().includes(query)) ||
            (product.barcode && product.barcode.toLowerCase().includes(query))
        )
    })

    const handleEditClick = (product: any) => {
        setEditingProduct({ ...product }) // Copy to avoid ref issues
        setIsEditOpen(true)
    }

    const handleDeleteClick = async (id: string) => {
        if (!confirm('¿Estás seguro de eliminar este producto?')) return

        const res = await deleteProduct(id)
        if (res.success) {
            toast({ title: "Eliminado", description: res.message })
            setProducts(products.filter(p => p.id !== id))
            router.refresh()
        } else {
            toast({ title: "Error", description: res.message, variant: "destructive" })
        }
    }

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!editingProduct) return

        setFormLoading(true)
        const res = await updateProduct(editingProduct.id, {
            name: editingProduct.name,
            barcode: editingProduct.barcode,
            brand: editingProduct.brand,
            description: editingProduct.description,
            price: Number(editingProduct.price),
            stock: Number(editingProduct.stock)
        })

        if (res.success) {
            toast({ title: "Actualizado", description: res.message })
            setIsEditOpen(false)
            setEditingProduct(null)
            // Update local list
            setProducts(products.map(p => p.id === editingProduct.id ? editingProduct : p))
            router.refresh()
        } else {
            toast({ title: "Error", description: res.message, variant: "destructive" })
        }
        setFormLoading(false)
    }

    return (
        <>
            <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-zinc-500" />
                    <Input
                        placeholder="Buscar por nombre, marca o código..."
                        className="pl-9 bg-zinc-900 border-zinc-800"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
            </div>

            <div className="border border-zinc-800 rounded-xl bg-zinc-900 shadow-sm overflow-hidden">
                <Table>
                    <TableHeader className="bg-zinc-900/50">
                        <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
                            <TableHead className="text-zinc-400">Código</TableHead>
                            <TableHead className="text-zinc-400">Nombre</TableHead>
                            <TableHead className="text-zinc-400">Marca</TableHead>
                            <TableHead className="text-right text-zinc-400">Precio</TableHead>
                            <TableHead className="text-right text-zinc-400">Stock</TableHead>
                            <TableHead className="text-right text-zinc-400">Acciones</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {filteredProducts && filteredProducts.length > 0 ? (
                            filteredProducts.map((product) => (
                                <TableRow key={product.id} className="border-zinc-800 hover:bg-zinc-800/30 transition-colors">
                                    <TableCell className="font-mono text-zinc-500 font-medium">{product.barcode || '-'}</TableCell>
                                    <TableCell className="text-zinc-200 font-medium">{product.name}</TableCell>
                                    <TableCell className="text-zinc-400">{product.brand || '-'}</TableCell>
                                    <TableCell className="text-right text-zinc-100 font-bold">${Number(product.price).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</TableCell>
                                    <TableCell className="text-right">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${product.stock <= 5
                                            ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                            }`}>
                                            {product.stock}
                                        </span>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex justify-end gap-2">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleEditClick(product)}
                                                className="text-zinc-400 hover:text-white hover:bg-zinc-800"
                                            >
                                                <Edit className="w-4 h-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleDeleteClick(product.id)}
                                                className="text-zinc-500 hover:text-red-400 hover:bg-red-900/10"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow className="border-zinc-800">
                                <TableCell colSpan={6} className="h-32 text-center text-zinc-500">
                                    <div className="flex flex-col items-center justify-center">
                                        <span className="mb-2 text-lg">🔍</span>
                                        No se encontraron productos.
                                    </div>
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
                <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-100">
                    <DialogHeader>
                        <DialogTitle>Editar Producto</DialogTitle>
                    </DialogHeader>
                    {editingProduct && (
                        <form onSubmit={handleSave} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Código de Barras</Label>
                                    <Input
                                        className="bg-zinc-950 border-zinc-800"
                                        value={editingProduct.barcode || ''}
                                        onChange={e => setEditingProduct({ ...editingProduct, barcode: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Marca</Label>
                                    <Input
                                        className="bg-zinc-950 border-zinc-800"
                                        value={editingProduct.brand || ''}
                                        onChange={e => setEditingProduct({ ...editingProduct, brand: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label>Nombre</Label>
                                <Input
                                    className="bg-zinc-950 border-zinc-800"
                                    value={editingProduct.name}
                                    onChange={e => setEditingProduct({ ...editingProduct, name: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Precio</Label>
                                    <Input
                                        type="number"
                                        step="0.01"
                                        className="bg-zinc-950 border-zinc-800"
                                        value={editingProduct.price}
                                        onChange={e => setEditingProduct({ ...editingProduct, price: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Stock</Label>
                                    <Input
                                        type="number"
                                        className="bg-zinc-950 border-zinc-800"
                                        value={editingProduct.stock}
                                        onChange={e => setEditingProduct({ ...editingProduct, stock: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>

                            <DialogFooter>
                                <Button type="button" variant="ghost" onClick={() => setIsEditOpen(false)}>Cancelar</Button>
                                <Button type="submit" className="bg-indigo-600 hover:bg-indigo-700" disabled={formLoading}>
                                    {formLoading ? 'Guardando...' : 'Guardar Cambios'}
                                </Button>
                            </DialogFooter>
                        </form>
                    )}
                </DialogContent>
            </Dialog>
        </>
    )
}
