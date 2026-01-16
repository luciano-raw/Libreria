'use server'

import { db } from '../db'
import { auth } from '@clerk/nextjs/server'
import { revalidatePath } from 'next/cache'

export type ProductData = {
    name: string
    barcode?: string | null
    description?: string | null
    brand?: string | null
    price: number
    stock: number
}

// Helper to get the store ID for the current user
// For MVP/Demo, we might need a way to select the active store if the user has multiple.
// For now, we'll assume the user belongs to at least one store and pick the first one,
// or we will pass storeId as an argument if we build a proper dashboard selector.
export async function getActiveStoreId() {
    const { userId } = await auth()
    if (!userId) throw new Error('Unauthorized')

    // Find the first store this user belongs to
    const userStore = await db.storeUser.findFirst({
        where: { userId },
        select: { storeId: true }
    })

    // Basic fallback for logic preservation: if no store, we can't add products.
    if (!userStore) throw new Error('No Store found for this user')
    return userStore.storeId
}

const serializeProduct = (product: any) => ({
    ...product,
    price: product.price.toNumber(),
    cost: product.cost ? product.cost.toNumber() : null,
})

export async function addProduct(data: ProductData) {
    try {
        const storeId = await getActiveStoreId()

        // Mimic Python logic: duplicates check
        if (data.barcode) {
            const existing = await db.product.findFirst({
                where: {
                    storeId,
                    barcode: data.barcode
                }
            })
            if (existing) {
                return { success: false, message: `Error: El código de barras '${data.barcode}' ya existe en esta tienda.` }
            }
        }

        const product = await db.product.create({
            data: {
                storeId,
                name: data.name,
                barcode: data.barcode,
                description: data.description,
                brand: data.brand,
                price: data.price,
                stock: data.stock,
            }
        })

        revalidatePath('/inventory')
        return { success: true, message: `Producto '${product.name}' agregado exitosamente.`, product: serializeProduct(product) }
    } catch (error) {
        console.error(error)
        return { success: false, message: 'Error al agregar producto.' }
    }
}

export async function getProducts(query: string = '') {
    try {
        const storeId = await getActiveStoreId()

        // Mimic Python: search by name (LIKE %)
        const products = await db.product.findMany({
            where: {
                storeId,
                name: { contains: query, mode: 'insensitive' }
            },
            orderBy: { name: 'asc' }
        })

        return { success: true, products: products.map(serializeProduct) }
    } catch (error) {
        return { success: false, message: 'Error al obtener productos', products: [] }
    }
}

export async function updateProduct(id: string, data: ProductData) {
    try {
        const storeId = await getActiveStoreId()

        // Check ownership
        const existing = await db.product.findUnique({
            where: { id, storeId }
        })
        if (!existing) return { success: false, message: 'Producto no encontrado.' }

        // Check barcode conflict if changed
        if (data.barcode && data.barcode !== existing.barcode) {
            const duplicate = await db.product.findFirst({
                where: { storeId, barcode: data.barcode }
            })
            if (duplicate) return { success: false, message: `El código '${data.barcode}' ya está en uso.` }
        }

        await db.product.update({
            where: { id },
            data: {
                name: data.name,
                barcode: data.barcode,
                description: data.description,
                brand: data.brand,
                price: data.price,
                stock: data.stock
            }
        })

        revalidatePath('/inventory')
        return { success: true, message: 'Producto actualizado.' }
    } catch (error) {
        return { success: false, message: 'Error al actualizar.' }
    }
}

export async function deleteProduct(id: string) {
    try {
        const storeId = await getActiveStoreId()

        // Check logic: Python warned about sales. Prisma handles foreign keys with errors usually.
        // Safe delete
        await db.product.delete({
            where: { id, storeId }
        })

        revalidatePath('/inventory')
        return { success: true, message: 'Producto eliminado.' }
    } catch (error) {
        // Catch FK constraint errors
        return { success: false, message: 'No se puede eliminar: El producto tiene ventas asociadas.' }
    }
}
