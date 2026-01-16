'use server'

import { db } from '../db'
import { auth } from '@clerk/nextjs/server'
import { getActiveStoreId } from './products'

export async function createQuote(data: {
    clientName: string,
    items: { productId: string, quantity: number, price: number }[]
}) {
    const storeId = await getActiveStoreId()
    if (!storeId) throw new Error('Store not found')

    // Calculate total on server side for security
    const total = data.items.reduce((acc, item) => acc + (item.price * item.quantity), 0)

    try {
        const quote = await db.quote.create({
            data: {
                storeId,
                clientName: data.clientName,
                total,
                items: {
                    create: data.items.map(item => ({
                        productId: item.productId,
                        quantity: item.quantity,
                        price: item.price
                    }))
                }
            },
            include: {
                items: {
                    include: { product: true }
                }
            }
        })
        return { success: true, quote }
    } catch (error) {
        console.error('Error creating quote:', error)
        return { success: false, error: 'Failed to create quote' }
    }
}

export async function getQuotes() {
    const storeId = await getActiveStoreId()
    if (!storeId) return { success: false, quotes: [] }

    try {
        const quotes = await db.quote.findMany({
            where: { storeId },
            orderBy: { createdAt: 'desc' },
            include: {
                _count: {
                    select: { items: true }
                }
            }
        })
        return { success: true, quotes }
    } catch (error) {
        return { success: false, quotes: [] }
    }
}

export async function getQuote(id: string) {
    const storeId = await getActiveStoreId()
    try {
        const quote = await db.quote.findUnique({
             where: { id },
             include: {
                 items: {
                     include: { product: true }
                 }
             }
        })
        
        if (!quote || quote.storeId !== storeId) {
            return { success: false, error: 'Quote not found' }
        }

        return { success: true, quote }
    } catch (error) {
        return { success: false, error: 'Error fetching quote' }
    }
}
