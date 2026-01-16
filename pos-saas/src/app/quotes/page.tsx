'use client'

import { useState, useEffect } from 'react'
import { getQuotes, getQuote } from '@/server/actions/quotes'
import { generateQuotePDF } from '@/lib/pdf-generator'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Search, FileText, Download, Loader2, Eye, Settings } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from 'next/link'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useToast } from '@/hooks/use-toast'

export default function QuotesPage() {
    const [quotes, setQuotes] = useState<any[]>([])
    const [searchQuery, setSearchQuery] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const [selectedQuote, setSelectedQuote] = useState<any | null>(null)
    const [isPreviewOpen, setIsPreviewOpen] = useState(false)
    const { toast } = useToast()

    useEffect(() => {
        loadQuotes()
    }, [])

    async function loadQuotes() {
        setIsLoading(true)
        const res = await getQuotes()
        if (res.success) {
            setQuotes(res.quotes)
        }
        setIsLoading(false)
    }

    const filteredQuotes = quotes.filter(q =>
        q.clientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.id.includes(searchQuery)
    )

    const handleDownloadPDF = async (quote: any) => {

        let fullQuote = quote
        // Fetch full details if items not present (list query might be light)
        if (!quote.items) {
            const res = await getQuote(quote.id)
            if (res.success) fullQuote = res.quote
        }

        const pdfBlob = await generateQuotePDF(fullQuote)
        const url = URL.createObjectURL(pdfBlob)
        const link = document.createElement('a')
        link.href = url
        link.download = `Cotizacion_${fullQuote.clientName.replace(/\s+/g, '_')}_${fullQuote.id.slice(0, 6)}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    const handlePreview = async (quote: any) => {
        const res = await getQuote(quote.id)
        if (res.success) {
            setSelectedQuote(res.quote)
            setIsPreviewOpen(true)
        } else {
            toast({ title: "Error", description: "No se pudieron cargar los detalles.", variant: "destructive" })
        }
    }

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 min-h-screen bg-zinc-950 text-zinc-100">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Historial de Cotizaciones</h1>
                    <p className="text-zinc-400">Gestiona y recupera cotizaciones pasadas.</p>
                </div>
                <div className="flex gap-2">
                    <Link href="/settings">
                        <Button variant="outline" className="border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 hover:text-white">
                            <Settings className="w-4 h-4 mr-2" />
                            Configurar PDF
                        </Button>
                    </Link>
                    <Button variant="outline" className="border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 hover:text-white" onClick={() => window.location.href = '/'}>
                        ← Volver
                    </Button>
                </div>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader className="border-b border-zinc-800 bg-zinc-900/50">
                    <div className="flex items-center gap-4">
                        <div className="relative flex-1 max-w-sm">
                            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-zinc-500" />
                            <Input
                                placeholder="Buscar por cliente..."
                                className="pl-8 bg-zinc-950 border-zinc-800 text-zinc-200 placeholder:text-zinc-600 focus-visible:ring-indigo-500"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
                                <TableHead className="text-zinc-400">Fecha</TableHead>
                                <TableHead className="text-zinc-400">Cliente</TableHead>
                                <TableHead className="text-zinc-400">Items</TableHead>
                                <TableHead className="text-zinc-400">Total</TableHead>
                                <TableHead className="text-right text-zinc-400">Acciones</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoading ? (
                                <TableRow className="border-zinc-800">
                                    <TableCell colSpan={5} className="h-24 text-center">
                                        <Loader2 className="h-6 w-6 animate-spin mx-auto text-zinc-600" />
                                    </TableCell>
                                </TableRow>
                            ) : filteredQuotes.length > 0 ? (
                                filteredQuotes.map((quote) => (
                                    <TableRow key={quote.id} className="border-zinc-800 hover:bg-zinc-800/30 transition-colors">
                                        <TableCell className="text-zinc-400">
                                            {new Date(quote.createdAt).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell className="font-medium text-zinc-200">{quote.clientName}</TableCell>
                                        <TableCell>
                                            <Badge variant="secondary" className="bg-zinc-800 text-zinc-300 hover:bg-zinc-700">
                                                {quote._count?.items || 0} productos
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="font-bold text-zinc-100">
                                            ${Number(quote.total).toLocaleString()}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <div className="flex justify-end gap-2">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => handlePreview(quote)}
                                                    className="text-indigo-400 hover:text-indigo-300 hover:bg-indigo-900/20"
                                                >
                                                    <Eye className="w-4 h-4 mr-2" />
                                                    Ver
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleDownloadPDF(quote)}
                                                    className="border-zinc-700 bg-transparent text-zinc-300 hover:bg-zinc-800 hover:text-white"
                                                >
                                                    <Download className="w-4 h-4 mr-2" />
                                                    PDF
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow className="border-zinc-800">
                                    <TableCell colSpan={5} className="h-32 text-center text-zinc-500">
                                        {searchQuery ? 'No se encontraron cotizaciones.' : 'No hay cotizaciones registradas.'}
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Preview Dialog */}
            <Dialog open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
                <DialogContent className="max-w-3xl bg-zinc-900 border-zinc-800 text-zinc-100">
                    <DialogHeader>
                        <DialogTitle className="text-zinc-100">Detalle de Cotización #{selectedQuote?.id.slice(0, 8)}</DialogTitle>
                    </DialogHeader>
                    {selectedQuote && (
                        <div className="space-y-6">
                            <div className="grid grid-cols-2 gap-4 p-4 bg-zinc-950/50 rounded-lg border border-zinc-800">
                                <div>
                                    <span className="text-sm text-zinc-500 block">Cliente</span>
                                    <span className="font-medium text-lg text-zinc-200">{selectedQuote.clientName}</span>
                                </div>
                                <div className="text-right">
                                    <span className="text-sm text-zinc-500 block">Fecha</span>
                                    <span className="font-medium text-zinc-200">{new Date(selectedQuote.createdAt).toLocaleDateString()}</span>
                                </div>
                            </div>

                            <div className="border border-zinc-800 rounded-lg overflow-hidden">
                                <Table>
                                    <TableHeader className="bg-zinc-900">
                                        <TableRow className="border-zinc-800 hover:bg-zinc-900">
                                            <TableHead className="text-zinc-400">Producto</TableHead>
                                            <TableHead className="text-center text-zinc-400">Cant.</TableHead>
                                            <TableHead className="text-right text-zinc-400">Precio</TableHead>
                                            <TableHead className="text-right text-zinc-400">Subtotal</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {selectedQuote.items.map((item: any) => (
                                            <TableRow key={item.id} className="border-zinc-800 hover:bg-zinc-900/50">
                                                <TableCell className="text-zinc-300">{item.product.name}</TableCell>
                                                <TableCell className="text-center text-zinc-300">{item.quantity}</TableCell>
                                                <TableCell className="text-right text-zinc-300">${Number(item.price).toLocaleString()}</TableCell>
                                                <TableCell className="text-right font-medium text-zinc-200">
                                                    ${(Number(item.price) * item.quantity).toLocaleString()}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>

                            <div className="flex justify-between items-center pt-4 border-t border-zinc-800">
                                <div className="text-sm text-zinc-500">
                                    Total Items: {selectedQuote.items.reduce((acc: any, i: any) => acc + i.quantity, 0)}
                                </div>
                                <div className="text-2xl font-bold text-zinc-100">
                                    Total: ${Number(selectedQuote.total).toLocaleString()}
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-2">
                                <Button variant="outline" onClick={() => setIsPreviewOpen(false)} className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white">Cerrar</Button>
                                <Button onClick={() => handleDownloadPDF(selectedQuote)} className="bg-pink-600 hover:bg-pink-700 text-white border-0">
                                    <Download className="w-4 h-4 mr-2" />
                                    Descargar PDF
                                </Button>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    )
}
