'use server'

import { db } from '../db'
import { auth } from '@clerk/nextjs/server'
import { getActiveStoreId } from '../auth'

export async function createQuote(data: {
    clientName: string,
    items: { productId: string, quantity: number, price: number }[]
}) {
    const storeId = await getActiveStoreId()
    if (!storeId) throw new Error('Store not found')

    // Calculate total on server side for security
    const total = data.items.reduce((acc, item) => acc + (item.price * item.quantity), 0)
    const roundedTotal = Math.round(total * 100) / 100

    try {
        const quote = await db.quote.create({
            data: {
                storeId,
                clientName: data.clientName,
                total: roundedTotal,
                items: {
                    create: data.items.map(item => ({
                        productId: item.productId,
                        quantity: item.quantity,
                        price: Math.round(item.price * 100) / 100
                    }))
                }
            },
            include: {
                items: {
                    include: { product: true }
                }
            }
        })

        const serializedQuote = {
            ...quote,
            total: Number(quote.total),
            items: quote.items.map(item => ({
                ...item,
                price: Number(item.price),
                product: {
                    ...item.product,
                    price: Number(item.product.price),
                    cost: item.product.cost ? Number(item.product.cost) : null
                }
            }))
        }

        return { success: true, quote: serializedQuote }
    } catch (error: any) {
        console.error('Error creating quote:', error)
        return { success: false, error: error.message || 'Failed to create quote' }
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
                },
                store: true
            }
        })

        const serializedQuotes = quotes.map(quote => ({
            ...quote,
            total: Number(quote.total)
        }))

        return { success: true, quotes: serializedQuotes }
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
                },
                store: true
            }
        })

        if (!quote || quote.storeId !== storeId) {
            return { success: false, error: 'Quote not found' }
        }

        const serializedQuote = {
            ...quote,
            total: Number(quote.total),
            items: quote.items.map(item => ({
                ...item,
                price: Number(item.price),
                product: {
                    ...item.product,
                    price: Number(item.product.price),
                    cost: item.product.cost ? Number(item.product.cost) : null
                }
            }))
        }

        return { success: true, quote: serializedQuote }
    } catch (error) {
        return { success: false, error: 'Error fetching quote' }
    }
}

export async function duplicateQuote(quoteId: string, newClientName: string) {
    const storeId = await getActiveStoreId()
    if (!storeId) return { success: false, error: 'Store not found' }

    if (!newClientName.trim()) return { success: false, error: 'Customer name is required' }

    try {
        const originalQuote = await db.quote.findUnique({
            where: { id: quoteId, storeId },
            include: { items: true }
        })

        if (!originalQuote) return { success: false, error: 'Quote not found' }

        const quote = await db.quote.create({
            data: {
                storeId,
                clientName: newClientName,
                total: originalQuote.total,
                status: 'DRAFT', // Explicitly DRAFT
                items: {
                    create: originalQuote.items.map(item => ({
                        productId: item.productId,
                        quantity: item.quantity,
                        price: item.price
                    }))
                }
            }
        })

        return { success: true, message: 'Quote duplicated successfully' }
    } catch (error: any) {
        console.error('Duplicate Error:', error)
        return { success: false, error: error.message || 'Failed to duplicate quote' }
    }
}

export async function updateQuoteStatus(quoteId: string, status: string) {
    const storeId = await getActiveStoreId()
    if (!storeId) return { success: false, error: 'Store not found' }

    try {
        await db.quote.update({
            where: { id: quoteId, storeId },
            data: { status }
        })
        return { success: true }
    } catch (error) {
        return { success: false, error: 'Failed to update status' }
    }
}

export async function convertQuoteToSale(quoteId: string) {
    const storeId = await getActiveStoreId()
    if (!storeId) return { success: false, error: 'Store not found' }

    try {
        const quote = await db.quote.findUnique({
            where: { id: quoteId, storeId },
            include: { items: true }
        })

        if (!quote) return { success: false, error: 'Quote not found' }
        if (quote.status === 'CONVERTED') return { success: false, error: 'Quote already converted' }

        // Start Transaction
        await db.$transaction(async (tx) => {
            // 1. Verify Stock
            for (const item of quote.items) {
                const product = await tx.product.findUnique({
                    where: { id: item.productId, storeId }
                })
                if (!product || product.stock < item.quantity) {
                    throw new Error(`Insufficient stock for product ID: ${item.productId}`)
                }
            }

            // 2. Create Sale
            const sale = await tx.sale.create({
                data: {
                    storeId,
                    total: quote.total,
                    items: {
                        create: quote.items.map(item => ({
                            productId: item.productId,
                            quantity: item.quantity,
                            price: item.price
                        }))
                    }
                }
            })

            // 3. Deduct Stock
            for (const item of quote.items) {
                await tx.product.update({
                    where: { id: item.productId, storeId },
                    data: { stock: { decrement: item.quantity } }
                })
            }

            // 4. Update Quote Status
            await tx.quote.update({
                where: { id: quoteId },
                data: { status: 'CONVERTED' }
            })
        })

        return { success: true, message: 'Quote converted to sale successfully' }
    } catch (error: any) {
        console.error('Conversion Error:', error)
        return { success: false, error: error.message || 'Failed to convert quote' }
    }
}
