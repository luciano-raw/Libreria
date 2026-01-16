
import { db } from '../src/server/db';

async function main() {
    console.log('Searching for the most recent pending user...');

    const user = await db.user.findFirst({
        where: { status: 'PENDING' },
        orderBy: { createdAt: 'desc' },
    });

    if (!user) {
        console.log('No pending users found.');
        return;
    }

    console.log(`Found pending user: ${user.email} (${user.name})`);
    console.log('Approving...');

    await db.user.update({
        where: { id: user.id },
        data: { status: 'APPROVED' },
    });

    console.log(`User ${user.email} has been APPROVED.`);
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await db.$disconnect();
    });
