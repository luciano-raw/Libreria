'use server'

import { db } from './db'
import { auth } from '@clerk/nextjs/server'
import { cookies } from 'next/headers'

export async function getActiveStoreId() {
    const { userId } = await auth()
    if (!userId) throw new Error('Unauthorized')

    // 1. Check for Impersonation Cookie
    const cookieStore = await cookies()
    const impersonatedStoreId = cookieStore.get('impersonated_store_id')?.value

    if (impersonatedStoreId) {
        // Security Check: Is the real user actually a Super Admin?
        // We fetch the user directly to be sure.
        const currentUser = await db.user.findUnique({
            where: { id: userId },
            select: { isSuperAdmin: true }
        })

        if (currentUser?.isSuperAdmin) {
            return impersonatedStoreId
        }
        // If not admin, ignore cookie (safeguard)
    }

    // 2. Normal Flow
    const userStore = await db.storeUser.findFirst({
        where: { userId },
        select: { storeId: true }
    })

    if (!userStore) throw new Error('No Store found for this user')
    return userStore.storeId
}

export async function isImpersonating() {
    const cookieStore = await cookies()
    return !!cookieStore.get('impersonated_store_id')?.value
}
