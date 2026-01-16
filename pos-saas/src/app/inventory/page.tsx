import { getProducts } from '@/server/actions/products'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import InventoryClient from './inventory-client'

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

      <InventoryClient initialProducts={products} />
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
