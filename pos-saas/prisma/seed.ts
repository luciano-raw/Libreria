
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
    console.log('🌱 Arrancando el seeding...')

    // 1. Crear Tienda Inicial (si no existe)
    const storeName = 'Librería Central'
    let store = await prisma.store.findFirst({
        where: { name: storeName }
    })

    if (!store) {
        store = await prisma.store.create({
            data: {
                name: storeName,
                slug: 'libreria-central'
            }
        })
        console.log(`✅ Tienda creada: ${store.name}`)
    } else {
        console.log(`ℹ️ La tienda ${store.name} ya existe.`)
    }

    // 2. Definir Productos de Ejemplo (Librería)
    const products = [
        // Libros
        { name: 'Cien Años de Soledad', description: 'Gabriel García Márquez', price: 15000, cost: 9000, stock: 20, category: 'Libros', brand: 'Sudamericana', barcode: '9789500722096' },
        { name: 'El Principito', description: 'Antoine de Saint-Exupéry', price: 8500, cost: 4500, stock: 50, category: 'Libros', brand: 'Salamandra', barcode: '9788414450001' },
        { name: '1984', description: 'George Orwell', price: 12000, cost: 7000, stock: 15, category: 'Libros', brand: 'Debolsillo', barcode: '9788499890944' },
        { name: 'Harry Potter y la Piedra Filosofal', description: 'J.K. Rowling', price: 21000, cost: 14000, stock: 30, category: 'Libros', brand: 'Salamandra', barcode: '9788478884452' },

        // Papelería
        { name: 'Cuaderno A4 Rayado', description: 'Tapa dura 84 h', price: 4500, cost: 2500, stock: 100, category: 'Papelería', brand: 'Rivadavia', barcode: '779000000001' },
        { name: 'Lapicera Azul', description: 'Birome trazo fino', price: 800, cost: 300, stock: 500, category: 'Papelería', brand: 'Bic', barcode: '779000000002' },
        { name: 'Lápiz Negro HB', description: 'Caja x12', price: 1200, cost: 500, stock: 200, category: 'Papelería', brand: 'Faber-Castell', barcode: '779000000003' },
        { name: 'Resma A4', description: '500 hojas 75g', price: 6500, cost: 4800, stock: 80, category: 'Papelería', brand: 'Autor', barcode: '779000000004' },
        { name: 'Marcadores Colores', description: 'Set x10 lavables', price: 3500, cost: 1800, stock: 40, category: 'Papelería', brand: 'Maped', barcode: '779000000005' },

        // Mochilas / Varios
        { name: 'Mochila Escolar Básica', description: 'Poliester resistente', price: 35000, cost: 20000, stock: 10, category: 'Varios', brand: 'Jansport', barcode: '779000000006' },
    ]

    // 3. Insertar Productos
    for (const p of products) {
        const existing = await prisma.product.findFirst({
            where: {
                storeId: store.id,
                barcode: p.barcode
            }
        })

        if (!existing) {
            await prisma.product.create({
                data: {
                    storeId: store.id,
                    name: p.name,
                    description: p.description,
                    price: p.price,
                    cost: p.cost,
                    stock: p.stock,
                    category: p.category,
                    brand: p.brand,
                    barcode: p.barcode
                }
            })
            console.log(`➕ Producto agregado: ${p.name}`)
        }
    }

    console.log('✅ Base de datos poblada exitosamente.')
}

main()
    .catch((e) => {
        console.error(e)
        process.exit(1)
    })
    .finally(async () => {
        await prisma.$disconnect()
    })
