'use server'

import { db } from '@/server/db'
import { auth } from '@clerk/nextjs/server'
import { revalidatePath } from 'next/cache'
import { getActiveStoreId } from '@/server/auth'

export type CartItemInput = {
    productId: string
    quantity: number
    price: number
}

export async function processSale(items: CartItemInput[], paymentMethod: string) {
    const { userId } = await auth()
    if (!userId) return { success: false, message: 'No autenticado' }

    try {
        // 1. Get Store (Handles Impersonation)
        const storeId = await getActiveStoreId()
        // getActiveStoreId throws if no store found, but let's wrap or handle if needed
        // The helper throws 'No Store found for this user' or 'Unauthorized'. 
        // We can catch those specific errors or just let the main catch handle it.
        // However, the original code returned a specifc object for missing store.
        // Let's rely on the try/catch block to return the error message.

        const total = items.reduce((acc, item) => acc + (item.price * item.quantity), 0)

        // Transaction to ensure atomicity (Stock deduction + Sale creation)
        const sale = await db.$transaction(async (tx) => {
            // A. Check Stock First
            for (const item of items) {
                const product = await tx.product.findUnique({ where: { id: item.productId } })
                if (!product) throw new Error(`Producto no encontrado: ${item.productId}`)
                if (product.stock < item.quantity) {
                    throw new Error(`Stock insuficiente para ${product.name}. Disponible: ${product.stock}`)
                }
            }

            // B. Create Sale Header
            const newSale = await tx.sale.create({
                data: {
                    storeId: storeId,
                    total: total,
                    paymentMethod: paymentMethod,
                }
            })

            // C. Create Sale Items and Deduct Stock
            for (const item of items) {
                await tx.saleItem.create({
                    data: {
                        saleId: newSale.id,
                        productId: item.productId,
                        quantity: item.quantity,
                        price: item.price
                    }
                })

                await tx.product.update({
                    where: { id: item.productId },
                    data: { stock: { decrement: item.quantity } }
                })
            }

            return newSale
        })

        revalidatePath('/sales')
        revalidatePath('/sales/history')
        revalidatePath('/inventory') // Stock changed

        return { success: true, saleId: sale.id }

    } catch (error: any) {
        return { success: false, message: error.message || 'Error al procesar la venta' }
    }
}

export async function getSalesHistory() {
    const { userId } = await auth()
    if (!userId) return { success: false, sales: [] }

    try {
        const storeId = await getActiveStoreId()

        const sales = await db.sale.findMany({
            where: { storeId: storeId },
            orderBy: { createdAt: 'desc' },
            include: {
                items: {
                    include: { product: true }
                }
            },
            take: 100 // Limit for now
        })

        // Serialize Decimal to number/string if needed, but client components might handle it better if we map
        // Prisma returns Decimal which can't be passed to client directly sometimes
        const safeSales = sales.map(s => ({
            ...s,
            total: Number(s.total),
            items: s.items.map(i => ({
                ...i,
                price: Number(i.price),
                product: {
                    ...i.product,
                    price: Number(i.product.price),
                    cost: i.product.cost ? Number(i.product.cost) : null
                }
            }))
        }))

        return { success: true, sales: safeSales }
    } catch (error) {
        console.error("Error fetching sales history:", error)
        return { success: false, sales: [] }
    }
}
