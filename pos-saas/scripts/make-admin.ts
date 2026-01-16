
// Run this with: npx tsx scripts/make-admin.ts <email>
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
    const email = process.argv[2]
    if (!email) {
        console.error('Please provide an email.')
        process.exit(1)
    }

    console.log(`Making ${email} a Super Admin...`)

    // Upsert user (in case they haven't logged in yet, prepopulate it)
    // Note: ID must be known if creating, but usually we update existing.
    // For safety, we only update existing.

    const user = await prisma.user.findUnique({
        where: { email }
    })

    if (!user) {
        console.error('User not found. Log in via the app first to create the record.')
        process.exit(1)
    }

    await prisma.user.update({
        where: { id: user.id },
        data: {
            isSuperAdmin: true,
            status: 'APPROVED'
        }
    })

    console.log('Success! User is now Super Admin.')
}

main()
