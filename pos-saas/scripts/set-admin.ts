
import { db } from '../src/server/db';

async function main() {
    const email = process.argv[2];

    if (!email) {
        console.error('Please provide an email address.');
        process.exit(1);
    }

    console.log(`Looking for user with email: ${email}...`);

    const user = await db.user.findUnique({
        where: { email },
    });

    if (!user) {
        console.error('User not found.');
        process.exit(1);
    }

    console.log(`Found user: ${user.name} (${user.id})`);
    console.log('Promoting to Super Admin...');

    await db.user.update({
        where: { id: user.id },
        data: { isSuperAdmin: true },
    });

    console.log('Success! User is now a Super Admin.');
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await db.$disconnect();
    });
