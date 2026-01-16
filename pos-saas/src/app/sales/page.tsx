'use client'

import { useState, useEffect, useRef } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Search, ShoppingCart, Trash2, Printer, FileText, Plus, Minus, AlertTriangle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { getProducts } from '@/server/actions/products'
import { createQuote } from '@/server/actions/quotes'
import { generateQuotePDF } from '@/lib/pdf-generator' // We will create this
import { Badge } from '@/components/ui/badge'

// Types
type Product = {
    id: string
    name: string
    price: number
    stock: number
    barcode: string | null
    brand: string | null
}

type CartItem = Product & {
    quantity: number
}

export default function SalesPage() {
    const [searchQuery, setSearchQuery] = useState('')
    const [products, setProducts] = useState<Product[]>([])
    const [cart, setCart] = useState<CartItem[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const searchInputRef = useRef<HTMLInputElement>(null)
    const { toast } = useToast()

    // Load initial products (active ones)
    useEffect(() => {
        loadProducts()
    }, [])

    // Barcode Scanner Listener
    useEffect(() => {
        const handleKeyPress = (e: KeyboardEvent) => {
            // Simple logic: if not focused on input and typing alphanumeric, append to hidden buffer or focus input
            // For now, we rely on the user focusing the main input which is standard for simple web POS using USB scanners
            if (document.activeElement?.tagName !== 'INPUT') {
                searchInputRef.current?.focus()
            }
        }
        window.addEventListener('keydown', handleKeyPress)
        return () => window.removeEventListener('keydown', handleKeyPress)
    }, [])

    async function loadProducts() {
        setIsLoading(true)
        const res = await getProducts()
        if (res.success) {
            // Map Decimal to number for client math
            setProducts(res.products.map(p => ({
                ...p,
                price: Number(p.price),
                barcode: p.barcode || '',
                brand: p.brand || ''
            })))
        }
        setIsLoading(false)
    }

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (p.barcode && p.barcode.includes(searchQuery)) ||
        (p.brand && p.brand.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    // Check exact match for barcode scanning
    useEffect(() => {
        const exactMatch = products.find(p => p.barcode === searchQuery)
        if (exactMatch && searchQuery.length > 3) { // Assume barcodes have some length
            addToCart(exactMatch)
            setSearchQuery('')
        }
    }, [searchQuery, products])

    function addToCart(product: Product) {
        if (product.stock <= 0) {
            toast({ title: "Sin Stock", description: "Este producto no tiene stock disponible.", variant: "destructive" })
            return
        }

        setCart(current => {
            const existing = current.find(item => item.id === product.id)
            if (existing) {
                if (existing.quantity >= product.stock) {
                    toast({ title: "Stock Insuficiente", description: "No puedes agregar más unidades de las disponibles.", variant: "destructive" })
                    return current
                }
                return current.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item)
            }
            return [...current, { ...product, quantity: 1 }]
        })
    }

    function updateQuantity(id: string, delta: number) {
        setCart(current => current.map(item => {
            if (item.id === id) {
                const newQty = item.quantity + delta
                if (newQty < 1) return item // Don't remove here, distinct action
                if (newQty > item.stock) {
                    toast({ title: "Límite de Stock", description: "No hay suficiente stock.", variant: "destructive" })
                    return item
                }
                return { ...item, quantity: newQty }
            }
            return item
        }))
    }

    function removeFromCart(id: string) {
        setCart(current => current.filter(item => item.id !== id))
    }

    const total = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0)

    async function handleQuote() {
        if (cart.length === 0) return
        const clientName = prompt("Ingrese Nombre del Cliente:")
        if (!clientName) return

        const res = await createQuote({
            clientName,
            items: cart.map(i => ({ productId: i.id, quantity: i.quantity, price: i.price }))
        })

        if (res.success && res.quote) {
            // Generate PDF Client Side
            const pdfBlob = await generateQuotePDF(res.quote)
            const url = URL.createObjectURL(pdfBlob)
            window.open(url, '_blank')

            toast({ title: "Cotización Generada", description: "El PDF se ha generado correctamente." })
            setCart([])
        } else {
            toast({ title: "Error", description: res.error || "No se pudo guardar la cotización.", variant: "destructive" })
        }
    }

    return (
        <div className="h-[calc(100vh-4rem)] p-6 bg-zinc-950 flex gap-6 text-zinc-100">
            {/* Left: Product Catalog */}
            <div className="flex-1 flex flex-col gap-4">
                <div className="flex gap-4 bg-zinc-900 p-4 rounded-xl border border-zinc-800 shadow-sm sticky top-0 z-10">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-5 h-5" />
                        <Input
                            ref={searchInputRef}
                            className="pl-10 h-12 text-lg bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-indigo-500"
                            placeholder="Buscar por nombre, código de barras o marca..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            autoFocus
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 overflow-y-auto pb-4">
                    {filteredProducts.map(product => (
                        <Card
                            key={product.id}
                            onClick={() => addToCart(product)}
                            className={`p-4 cursor-pointer hover:shadow-md transition-all bg-zinc-900 border-zinc-800 border-l-4 ${product.stock <= 10 ? 'border-l-amber-500' : 'border-l-transparent'} hover:border-l-blue-500 group`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-xs font-mono text-zinc-500 truncate max-w-[80px]" title={product.barcode || ''}>{product.barcode || 'Sin Código'}</span>
                                {product.stock <= 10 && (
                                    <Badge variant="outline" className="text-amber-500 border-amber-500/20 bg-amber-500/10 text-[10px] px-1 py-0 h-5 md:h-auto">
                                        {product.stock === 0 ? 'AGOTADO' : 'BAJO STOCK'}
                                    </Badge>
                                )}
                            </div>
                            <h3 className="font-semibold text-zinc-200 line-clamp-2 min-h-[3rem] text-sm md:text-base group-hover:text-blue-400">{product.name}</h3>
                            <p className="text-xs text-zinc-500 mb-3">{product.brand || 'Genérico'}</p>

                            <div className="flex justify-between items-end mt-auto">
                                <div className="flex flex-col">
                                    <span className="text-xs text-zinc-500">Precio</span>
                                    <span className="text-lg font-bold text-zinc-100">${product.price.toLocaleString()}</span>
                                </div>
                                <div className="text-right">
                                    <span className="text-xs text-zinc-500 block">Stock</span>
                                    <span className={`font-medium ${product.stock <= 10 ? 'text-amber-500' : 'text-zinc-400'}`}>{product.stock}</span>
                                </div>
                            </div>
                        </Card>
                    ))}
                    {filteredProducts.length === 0 && (
                        <div className="col-span-full text-center text-zinc-500 py-12">
                            No se encontraron productos.
                        </div>
                    )}
                </div>
            </div>

            {/* Right: Cart */}
            <div className="w-[400px] flex flex-col bg-zinc-900 rounded-xl border border-zinc-800 shadow-sm h-full">
                <div className="p-4 border-b border-zinc-800 flex items-center gap-2 bg-zinc-900/50">
                    <ShoppingCart className="w-5 h-5 text-zinc-400" />
                    <h2 className="font-bold text-lg text-zinc-200">Carrito de Venta</h2>
                    <Badge className="ml-auto bg-zinc-800 text-zinc-300 hover:bg-zinc-700">{cart.reduce((a, b) => a + b.quantity, 0)} items</Badge>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {cart.map(item => (
                        <div key={item.id} className="flex gap-3 p-3 rounded-lg border border-zinc-800 bg-zinc-950/50 group hover:border-blue-500/30 hover:bg-blue-500/5 transition-colors">
                            <div className="flex-1 overflow-hidden">
                                <div className="font-medium text-sm truncate text-zinc-200">{item.name}</div>
                                <div className="text-xs text-zinc-500 flex gap-2 mt-1">
                                    <span>${item.price.toLocaleString()} un.</span>
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <div className="flex items-center border border-zinc-700 rounded-md bg-zinc-900 h-8">
                                    <button
                                        onClick={() => updateQuantity(item.id, -1)}
                                        className="px-2 hover:bg-zinc-800 text-zinc-400 hover:text-white h-full rounded-l-md transition-colors"
                                    >
                                        <Minus className="w-3 h-3" />
                                    </button>
                                    <span className="w-8 text-center text-sm font-medium text-zinc-200">{item.quantity}</span>
                                    <button
                                        onClick={() => updateQuantity(item.id, 1)}
                                        className="px-2 hover:bg-zinc-800 text-zinc-400 hover:text-white h-full rounded-r-md transition-colors"
                                    >
                                        <Plus className="w-3 h-3" />
                                    </button>
                                </div>
                                <div className="flex flex-col items-end min-w-[60px]">
                                    <span className="font-bold text-sm text-zinc-100">${(item.price * item.quantity).toLocaleString()}</span>
                                    <button
                                        onClick={() => removeFromCart(item.id)}
                                        className="text-red-400 hover:text-red-300 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                    {cart.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-48 text-zinc-600 text-center p-4">
                            <ShoppingCart className="w-12 h-12 mb-2 opacity-20" />
                            <p>El carrito está vacío</p>
                            <p className="text-xs mt-1 text-zinc-500">Escanea un producto o selecciona del catálogo</p>
                        </div>
                    )}
                </div>

                <div className="p-6 border-t border-zinc-800 bg-zinc-900/80 rounded-b-xl space-y-4">
                    <div className="flex justify-between items-baseline mb-2">
                        <span className="text-zinc-400 font-medium">Total a Pagar</span>
                        <span className="text-3xl font-bold text-zinc-100">${total.toLocaleString()}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <Button
                            variant="outline"
                            className="bg-transparent border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white hover:border-zinc-600"
                            onClick={handleQuote}
                            disabled={cart.length === 0}
                        >
                            <FileText className="w-4 h-4 mr-2" />
                            Cotizar
                        </Button>
                        <Button
                            className="bg-emerald-600 hover:bg-emerald-500 text-white border-0 shadow-lg shadow-emerald-900/20"
                            disabled={cart.length === 0}
                        >
                            <Printer className="w-4 h-4 mr-2" />
                            Cobrar
                        </Button>
                    </div>
                </div>
            </div>
            {/* Exit Link fixed position or integrated? For consistency with other pages, maybe a small back button somewhere, but requirement is just styling. The user didn't ask for a back button here specifically, but it's good practice. Given the density, I will stick to the requested styling. */}
        </div>
    )
}
