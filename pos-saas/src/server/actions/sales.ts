'use server'

import { db } from '../db'
import { auth } from '@clerk/nextjs/server'
import { getActiveStoreId } from '../auth'

export type CartItem = {
    productId: string
    quantity: number
    price: number // Price at the moment of sale
}

export async function registerSale(cart: CartItem[], total: number, paymentMethod: string = 'CASH') {
    const { userId } = await auth()
    if (!userId) {
        return { success: false, message: 'No autorizado' }
    }

    try {
        // 1. Get Store ID
        const storeId = await getActiveStoreId()

        // 2. Perform Transaction (Prisma $transaction)
        // This ensures either EVERYTHING succeeds or NOTHING does (rolling back stock changes)
        const saleResult = await db.$transaction(async (tx) => {

            // A. Create Sale Record
            const sale = await tx.sale.create({
                data: {
                    storeId,
                    total,
                    paymentMethod
                }
            })

            // B. Process Items (Create SaleItem AND Update Stock)
            for (const item of cart) {
                // Validation: Check stock before selling?
                // Python code didn't explicitly check before, but SQL might fail if check constraints existed.
                // We will check here for better UX.
                const product = await tx.product.findUnique({ where: { id: item.productId } })

                if (!product) throw new Error(`Producto ID ${item.productId} no encontrado.`)
                if (product.stock < item.quantity) {
                    throw new Error(`Stock insuficiente para '${product.name}'. Disponible: ${product.stock}`)
                }

                // Create Detail
                await tx.saleItem.create({
                    data: {
                        saleId: sale.id,
                        productId: item.productId,
                        quantity: item.quantity,
                        price: item.price
                    }
                })

                // Update Stock (Decrement)
                await tx.product.update({
                    where: { id: item.productId },
                    data: {
                        stock: { decrement: item.quantity }
                    }
                })
            }

            return sale
        })

        return { success: true, message: 'Venta registrada exitosamente.', saleId: saleResult.id }

    } catch (error: any) {
        console.error(error)
        return { success: false, message: error.message || 'Error al procesar la venta.' }
    }
}
