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
