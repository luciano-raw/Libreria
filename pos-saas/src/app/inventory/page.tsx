import { getProducts } from '@/server/actions/products'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import Link from 'next/link'

export default async function InventoryPage() {
  const { products } = await getProducts()

  return (
    <div className="p-8 max-w-7xl mx-auto min-h-screen bg-zinc-950 text-zinc-100">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-zinc-100">Inventario</h2>
          <p className="text-zinc-400">Gestiona tus productos y stock.</p>
        </div>
        <Link href="/inventory/new">
          <Button className="bg-emerald-600 text-white hover:bg-emerald-700 shadow-lg shadow-emerald-900/20 border-0">
            + Agregar Producto
          </Button>
        </Link>
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
            {products && products.length > 0 ? (
              products.map((product) => (
                <TableRow key={product.id} className="border-zinc-800 hover:bg-zinc-800/30 transition-colors">
                  <TableCell className="font-mono text-zinc-500 font-medium">{product.barcode || '-'}</TableCell>
                  <TableCell className="text-zinc-200 font-medium">{product.name}</TableCell>
                  <TableCell className="text-zinc-400">{product.brand || '-'}</TableCell>
                  <TableCell className="text-right text-zinc-100 font-bold">${Number(product.price).toFixed(2)}</TableCell>
                  <TableCell className="text-right">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${product.stock <= 5
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                      {product.stock}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white hover:bg-zinc-800">Editar</Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow className="border-zinc-800">
                <TableCell colSpan={6} className="h-32 text-center text-zinc-500">
                  <div className="flex flex-col items-center justify-center">
                    <span className="mb-2 text-lg">📦</span>
                    No hay productos. ¡Agrega el primero!
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="mt-8">
        <Link href="/">
          <Button variant="outline" className="border-zinc-800 text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100">
            ← Volver al Inicio
          </Button>
        </Link>
      </div>
    </div>
  )
}
