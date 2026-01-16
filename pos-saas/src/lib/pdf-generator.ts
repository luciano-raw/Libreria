import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

// Professional Zinc Color Palette (RGB)
const COLORS = {
    // Zinc 900 - Header Background
    primary: [24, 24, 27] as [number, number, number],
    // Zinc 800 - Table Header
    secondary: [39, 39, 42] as [number, number, number],
    // Zinc 900 - Dark Text
    text_dark: [24, 24, 27] as [number, number, number],
    // White
    text_light: [255, 255, 255] as [number, number, number],
    // Zinc 100 - Highlight
    highlight: [244, 244, 245] as [number, number, number],
    // Zinc 500 - Secondary Text
    text_muted: [113, 113, 122] as [number, number, number]
}

export async function generateQuotePDF(quote: any) {
    const doc = new jsPDF()

    // Default colors (Zinc) if no store settings
    const primaryColor = quote.store?.pdfPrimaryColor || '#18181b'
    const secondaryColor = quote.store?.pdfSecondaryColor || '#27272a'

    // Convert hex to rgb
    const hexToRgb = (hex: string) => {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? [
            parseInt(result[1], 16),
            parseInt(result[2], 16),
            parseInt(result[3], 16)
        ] : [24, 24, 27];
    }

    const primaryRGB = hexToRgb(primaryColor)
    const secondaryRGB = hexToRgb(secondaryColor)

    // --- Header ---
    // Full width header bar
    doc.setFillColor(primaryRGB[0], primaryRGB[1], primaryRGB[2])
    doc.rect(0, 0, 210, 40, 'F')

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(22)
    doc.setTextColor(COLORS.text_light[0], COLORS.text_light[1], COLORS.text_light[2])
    doc.text(quote.store?.name || 'Librería Agosto 7', 15, 18)

    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.text('Sistema de Cotizaciones', 15, 25)

    // Invoice/Quote Title moved to right
    doc.setFontSize(28)
    doc.setTextColor(255, 255, 255)
    doc.text('COTIZACIÓN', 195, 25, { align: 'right' })

    // Contact Info (Below header)
    doc.setTextColor(COLORS.text_dark[0], COLORS.text_dark[1], COLORS.text_dark[2])
    doc.setFontSize(9)
    // Only show if available, otherwise use defaults
    const phone = quote.store?.phone || '(555) 123-4567'
    const email = quote.store?.email || 'contacto@libreriaagosto7.com'

    doc.text(`Tel: ${phone}`, 195, 50, { align: 'right' })
    doc.text(`Email: ${email}`, 195, 55, { align: 'right' })
    doc.text('Calle Principal #1234', 195, 60, { align: 'right' })

    let yPos = 50

    // --- Client Info Section ---
    doc.setDrawColor(COLORS.secondary[0], COLORS.secondary[1], COLORS.secondary[2])
    doc.setLineWidth(0.5)
    doc.line(15, yPos + 15, 195, yPos + 15)

    yPos += 25

    // Client Name
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.text('CLIENTE:', 15, yPos)
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(14)
    doc.text(quote.clientName || 'Cliente General', 15, yPos + 7)

    // Invoice Details
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.text('DETALLES:', 120, yPos)

    doc.setFont('helvetica', 'normal')
    doc.text(`Fecha:`, 120, yPos + 6)
    doc.text(new Date().toLocaleDateString(), 150, yPos + 6)

    doc.text(`Folio:`, 120, yPos + 12)
    doc.text(`#${quote.id.slice(0, 8).toUpperCase()}`, 150, yPos + 12)

    yPos += 25

    // --- Table ---
    autoTable(doc, {
        startY: yPos,
        head: [['Producto', 'Cant.', 'Precio Unit.', 'Total']],
        body: quote.items.map((item: any) => [
            item.product.name,
            item.quantity,
            `$${Number(item.price).toLocaleString('es-AR', { minimumFractionDigits: 2 })}`,
            `$${(Number(item.price) * item.quantity).toLocaleString('es-AR', { minimumFractionDigits: 2 })}`
        ]),
        headStyles: {
            fillColor: [secondaryRGB[0], secondaryRGB[1], secondaryRGB[2]],
            textColor: COLORS.text_light,
            fontStyle: 'bold',
            halign: 'left'
        },
        columnStyles: {
            0: { cellWidth: 'auto' }, // Product
            1: { cellWidth: 20, halign: 'center' }, // Qty
            2: { cellWidth: 35, halign: 'right' }, // Price
            3: { cellWidth: 35, halign: 'right' }  // Total
        },
        styles: {
            fontSize: 10,
            cellPadding: 4,
            lineColor: [228, 228, 231], // Zinc 200
            lineWidth: 0.1
        },
        alternateRowStyles: {
            fillColor: [250, 250, 250] // Zinc 50
        }
    })

    // --- Total Section ---
    // @ts-ignore
    const finalY = doc.lastAutoTable.finalY + 10

    // Draw a box for totals
    doc.setFillColor(COLORS.highlight[0], COLORS.highlight[1], COLORS.highlight[2])
    doc.rect(130, finalY - 5, 65, 20, 'F')

    doc.setFontSize(12)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(COLORS.text_dark[0], COLORS.text_dark[1], COLORS.text_dark[2])
    doc.text('TOTAL:', 135, finalY + 8)

    doc.setFontSize(14)
    doc.text(`$${Number(quote.total).toLocaleString('es-AR', { minimumFractionDigits: 2 })}`, 190, finalY + 8, { align: 'right' })

    // --- Footer ---
    doc.setFontSize(8)
    doc.setFont('helvetica', 'italic')
    doc.setTextColor(COLORS.text_muted[0], COLORS.text_muted[1], COLORS.text_muted[2])
    doc.text('Gracias por su preferencia.', 105, 275, { align: 'center' })
    doc.text('Cotización válida por 15 días. Documento generado electrónicamente.', 105, 280, { align: 'center' })

    return doc.output('blob')
}
