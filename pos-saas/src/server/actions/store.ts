'use server'

import { db } from '../db'
import { auth, currentUser } from '@clerk/nextjs/server'
import { revalidatePath } from 'next/cache'

export async function createFirstStore(storeName: string) {
    const user = await currentUser()
    if (!user) return { success: false, message: 'No autorizado' }

    try {
        // 1. Check if user already has a store (optional, maybe we allow multiples later)
        const existing = await db.storeUser.findFirst({
            where: { userId: user.id }
        })
        if (existing) {
            return { success: false, message: 'Ya tienes una tienda creada.' }
        }

        // 2. Create the User in our DB if they don't exist yet
        // (We sync basic info from Clerk)
        await db.user.upsert({
            where: { id: user.id },
            update: {},
            create: {
                id: user.id,
                email: user.emailAddresses[0].emailAddress,
                name: `${user.firstName} ${user.lastName}`.trim()
            }
        })

        // 3. Create Store and Link User
        const slug = storeName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')

        // Transaction: Create Store + Create Link (Owner)
        await db.$transaction(async (tx) => {
            const store = await tx.store.create({
                data: {
                    name: storeName,
                    slug: slug + '-' + Math.floor(Math.random() * 1000) // Ensure uniqueness
                }
            })

            await tx.storeUser.create({
                data: {
                    userId: user.id,
                    storeId: store.id,
                    role: 'OWNER'
                }
            })
        })

        revalidatePath('/')
        return { success: true, message: 'Tienda creada exitosamente.' }

    } catch (error) {
        console.error(error)
        return { success: false, message: 'Error al crear la tienda.' }
    }
}

// Helper (duplicated from products.ts for now, ideally shared)
async function getActiveStoreId() {
    const { userId } = await auth()
    if (!userId) throw new Error('Unauthorized')

    const userStore = await db.storeUser.findFirst({
        where: { userId },
        select: { storeId: true }
    })

    if (!userStore) throw new Error('No Store found for this user')
    return userStore.storeId
}

export async function getStoreSettings() {
    try {
        const storeId = await getActiveStoreId()
        const store = await db.store.findUnique({
            where: { id: storeId },
            select: { pdfPrimaryColor: true, pdfSecondaryColor: true } as any
        })
        return { success: true, settings: store }
    } catch (error) {
        return { success: false, message: 'Error retrieving settings' }
    }
}

export async function updateStoreSettings(data: { pdfPrimaryColor: string, pdfSecondaryColor: string }) {
    try {
        const storeId = await getActiveStoreId()

        await db.store.update({
            where: { id: storeId },
            data: {
                pdfPrimaryColor: data.pdfPrimaryColor,
                pdfSecondaryColor: data.pdfSecondaryColor
            }
        })

        revalidatePath('/settings')
        return { success: true, message: 'Configuración actualizada.' }
    } catch (error) {
        return { success: false, message: 'Error updating settings' }
    }
}
