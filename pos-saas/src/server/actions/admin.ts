'use server'

import { db } from '../db'
import { auth } from '@clerk/nextjs/server'
import { revalidatePath } from 'next/cache'

// Only Super Admin can call these
async function checkSuperAdmin() {
    const { userId } = await auth()
    if (!userId) throw new Error('Unauthorized')

    const user = await db.user.findUnique({ where: { id: userId } })
    if (!user || !user.isSuperAdmin) {
        throw new Error('Forbidden: Super Admin only')
    }
}

const serializeUser = (user: any) => ({
    ...user,
    createdAt: user.createdAt ? user.createdAt.toISOString() : null,
    updatedAt: user.updatedAt ? user.updatedAt.toISOString() : null,
})

export async function approveUser(targetUserId: string) {
    try {
        await checkSuperAdmin()
        await db.user.update({
            where: { id: targetUserId },
            data: { status: 'APPROVED' }
        })
        revalidatePath('/admin')
        return { success: true, message: 'Usuario aprobado.' }
    } catch (error) {
        return { success: false, message: 'Error al aprobar.' }
    }
}

export async function rejectUser(targetUserId: string) {
    try {
        await checkSuperAdmin()
        await db.user.update({
            where: { id: targetUserId },
            data: { status: 'REJECTED' }
        })
        revalidatePath('/admin')
        return { success: true, message: 'Usuario rechazado.' }
    } catch (error) {
        return { success: false, message: 'Error al rechazar.' }
    }
}

export async function suspendUser(targetUserId: string) {
    try {
        await checkSuperAdmin()
        await db.user.update({
            where: { id: targetUserId },
            data: { status: 'SUSPENDED' as any }
        })
        revalidatePath('/admin')
        return { success: true, message: 'Usuario suspendido.' }
    } catch (error) {
        return { success: false, message: 'Error al suspender.' }
    }
}

export async function getPendingUsers() {
    try {
        await checkSuperAdmin()
        const users = await db.user.findMany({
            where: { status: 'PENDING' },
            orderBy: { createdAt: 'desc' }
        })
        return { success: true, users: users.map(serializeUser) }
    } catch (error) {
        console.error(error)
        return { success: false, users: [] }
    }
}

export async function getAllUsers() {
    try {
        await checkSuperAdmin()
        const users = await db.user.findMany({
            orderBy: { createdAt: 'desc' }
        })
        return { success: true, users: users.map(serializeUser) }
    } catch (error) {
        console.error(error)
        return { success: false, users: [] }
    }
}

export async function updateUserRole(userId: string, isSuperAdmin: boolean) {
    try {
        await checkSuperAdmin()
        await db.user.update({
            where: { id: userId },
            data: { isSuperAdmin }
        })
        revalidatePath('/admin')
        return { success: true, message: 'Rol actualizado.' }
    } catch (error) {
        console.error(error)
        return { success: false, message: 'Error al actualizar rol.' }
    }
}

export async function deleteUser(userId: string) {
    try {
        await checkSuperAdmin()
        // Optional: Check if user owns stores and handle accordingly? 
        // For now just delete the user record. Foreign keys might restrict this if not cascaded.
        // Prisma schema usually handles cascades if defined, otherwise we might error.
        // Let's first delete StoreUser relations if needed or assume DB handles it.
        // Looking at schema: StoreUser -> User relation. No onDelete cascade specified in the snippet I saw?
        // Let's check schema again or just try delete. 
        // Actually, schema snippet showed: user User @relation(...) -> no onDelete: Cascade. 
        // We should manually clean up or update schema. 
        // For safety/simplicity in this step, I'll delete StoreUser records first.

        await db.storeUser.deleteMany({ where: { userId } })

        await db.user.delete({
            where: { id: userId }
        })
        revalidatePath('/admin')
        return { success: true, message: 'Usuario eliminado.' }
    } catch (error) {
        console.error(error)
        return { success: false, message: 'Error al eliminar usuario.' }
    }
}
