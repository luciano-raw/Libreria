import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

// Colors from python script (adapted to RGB)
const COLORS = {
    primary: [205, 180, 219],
    secondary: [255, 200, 221],
    text_dark: [30, 41, 59],
    text_light: [241, 245, 249],
    header_bg: [205, 180, 219],
    highlight: [162, 210, 255]
}

export async function generateQuotePDF(quote: any) {
    const doc = new jsPDF()

    // --- Header ---
    doc.setFillColor(COLORS.header_bg[0], COLORS.header_bg[1], COLORS.header_bg[2])
    doc.rect(15, 15, 180, 50, 'F')

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(24)
    doc.setTextColor(COLORS.text_dark[0], COLORS.text_dark[1], COLORS.text_dark[2])
    doc.text('Librería Agosto 7', 30, 25)

    doc.setFontSize(18)
    doc.text('COTIZACIÓN', 30, 35)

    // Contact Info
    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.text('Tel: (555) 123-4567', 185, 30, { align: 'right' })
    doc.text('Email: contacto@libreriaagosto7.com', 185, 35, { align: 'right' })
    doc.text('Calle Principal #1234', 185, 40, { align: 'right' })

    let yPos = 70

    // --- Info Client ---
    doc.setFillColor(189, 224, 254) // Info blue
    doc.rect(15, yPos, 180, 8, 'F')
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(12)
    doc.text('INFORMACIÓN DE LA COTIZACIÓN', 20, yPos + 6)

    yPos += 15
    doc.setFontSize(10)
    doc.text(`Cliente: ${quote.clientName}`, 15, yPos)
    doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 105, yPos)

    yPos += 7
    doc.text(`Folio: #${quote.id.slice(0, 8)}`, 15, yPos)

    yPos += 10

    // --- Table ---
    autoTable(doc, {
        startY: yPos,
        head: [['Producto', 'Cant.', 'Precio Unit.', 'Total']],
        body: quote.items.map((item: any) => [
            item.product.name,
            item.quantity,
            `$${Number(item.price).toLocaleString()}`,
            `$${(Number(item.price) * item.quantity).toLocaleString()}`
        ]),
        headStyles: {
            fillColor: [205, 180, 219],
            textColor: [255, 255, 255],
            fontStyle: 'bold'
        },
        styles: {
            fontSize: 9,
            cellPadding: 3
        },
        alternateRowStyles: {
            fillColor: [250, 248, 252]
        }
    })

    // --- Total ---
    // @ts-ignore
    const finalY = doc.lastAutoTable.finalY + 10

    doc.setFillColor(COLORS.highlight[0], COLORS.highlight[1], COLORS.highlight[2])
    doc.rect(130, finalY, 65, 12, 'F')

    doc.setFontSize(14)
    doc.setFont('helvetica', 'bold')
    doc.text('TOTAL:', 140, finalY + 8)
    doc.text(`$${Number(quote.total).toLocaleString()}`, 190, finalY + 8, { align: 'right' })

    // Footer
    doc.setFontSize(8)
    doc.setFont('helvetica', 'italic')
    doc.setTextColor(100, 100, 100)
    doc.text('Cotización válida por 15 días.', 105, 280, { align: 'center' })

    return doc.output('blob')
}
