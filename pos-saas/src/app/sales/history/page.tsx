import { getSalesHistory } from '@/server/actions/sales'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ArrowLeft, Calendar, CreditCard, DollarSign } from 'lucide-react'
import Link from 'next/link'

export default async function SalesHistoryPage() {
    const res = await getSalesHistory()
    const sales = res.success ? res.sales : []

    return (
        <div className="min-h-screen bg-zinc-950 p-8 text-zinc-100">
            <div className="max-w-5xl mx-auto space-y-6">
                <div className="flex items-center gap-4">
                    <Link href="/sales" className="p-2 hover:bg-zinc-800 rounded-full transition-colors text-zinc-400 hover:text-white">
                        <ArrowLeft className="w-6 h-6" />
                    </Link>
                    <h1 className="text-3xl font-bold">Historial de Ventas</h1>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="bg-zinc-900 border-zinc-800">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-zinc-400">Ventas Registradas</CardTitle>
                            <Calendar className="w-4 h-4 text-zinc-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-zinc-100">{sales.length}</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900 border-zinc-800">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-zinc-400">Ingresos Totales (Histórico)</CardTitle>
                            <DollarSign className="w-4 h-4 text-emerald-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-emerald-500">
                                ${sales.reduce((acc: number, sale: any) => acc + Number(sale.total), 0).toLocaleString()}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <Card className="bg-zinc-900 border-zinc-800">
                    <CardHeader>
                        <CardTitle>Transacciones Recientes</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader className="border-zinc-800">
                                <TableRow className="border-zinc-800 hover:bg-transparent">
                                    <TableHead className="text-zinc-400">Fecha</TableHead>
                                    <TableHead className="text-zinc-400">ID Venta</TableHead>
                                    <TableHead className="text-zinc-400">Método</TableHead>
                                    <TableHead className="text-zinc-400">Items</TableHead>
                                    <TableHead className="text-right text-zinc-400">Total</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {sales.length > 0 ? (
                                    sales.map((sale: any) => (
                                        <TableRow key={sale.id} className="border-zinc-800 hover:bg-zinc-800/50">
                                            <TableCell className="font-medium text-zinc-300">
                                                {new Date(sale.createdAt).toLocaleDateString()} <span className="text-zinc-500 text-xs ml-1">{new Date(sale.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                            </TableCell>
                                            <TableCell className="text-zinc-500 text-xs font-mono">
                                                {sale.id.slice(0, 8).toUpperCase()}
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="outline" className={`
                                                    ${sale.paymentMethod === 'CASH' ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10' : ''}
                                                    ${sale.paymentMethod === 'CARD' ? 'border-blue-500/30 text-blue-400 bg-blue-500/10' : ''}
                                                    ${sale.paymentMethod === 'TRANSFER' ? 'border-purple-500/30 text-purple-400 bg-purple-500/10' : ''}
                                                `}>
                                                    {sale.paymentMethod === 'CASH' ? 'Efectivo' : sale.paymentMethod === 'CARD' ? 'Tarjeta' : 'Transferencia'}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="text-zinc-400 text-sm">
                                                {sale.items.reduce((acc: number, i: any) => acc + i.quantity, 0)} productos
                                            </TableCell>
                                            <TableCell className="text-right font-bold text-zinc-100">
                                                ${Number(sale.total).toLocaleString()}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={5} className="text-center py-8 text-zinc-500">
                                            No hay ventas registradas.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
