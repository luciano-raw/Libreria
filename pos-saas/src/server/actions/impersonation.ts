'use server'

import { db } from '../db'
import { auth } from '@clerk/nextjs/server'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export async function startImpersonation(targetStoreId: string) {
    const { userId } = await auth()
    if (!userId) throw new Error('Unauthorized')

    // 1. Verify Super Admin Status
    const user = await db.user.findUnique({
        where: { id: userId },
        select: { isSuperAdmin: true }
    })

    if (!user?.isSuperAdmin) {
        return { success: false, message: 'No tienes permisos de administrador.' }
    }

    // 2. Verify Target Store Exists
    const store = await db.store.findUnique({
        where: { id: targetStoreId }
    })

    if (!store) {
        return { success: false, message: 'Tienda no encontrada.' }
    }

    // 3. Set Cookie
    const cookieStore = await cookies()
    cookieStore.set('impersonated_store_id', targetStoreId, {
        path: '/',
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production'
    })

    return { success: true }
}

export async function stopImpersonation() {
    const cookieStore = await cookies()
    cookieStore.delete('impersonated_store_id')
    redirect('/')
}
