import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from typing import Dict, Any

def generate_itinerary_pdf(trip_data: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )
    
    day_header_style = ParagraphStyle(
        'DayHeaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=15,
        spaceAfter=8
    )

    story = []

    # Document Header
    story.append(Paragraph(f"<b>Lịch Trình Du Lịch: {trip_data.get('title', 'Kế Hoạch')}</b>", title_style))
    story.append(Paragraph(
        f"<b>Điểm đến:</b> {trip_data.get('destination')} | "
        f"<b>Thời gian:</b> {trip_data.get('start_date')} đến {trip_data.get('end_date')} | "
        f"<b>Số khách:</b> {trip_data.get('travelers')} | "
        f"<b>Ngân sách:</b> {trip_data.get('budget'):,} {trip_data.get('currency')}",
        subtitle_style
    ))
    
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

    days = trip_data.get('days', [])
    for day in days:
        story.append(Paragraph(f"Ngày {day.get('day_number')} ({day.get('date')})", day_header_style))
        
        table_data = [["Thời gian", "Hoạt động / Địa điểm", "Loại", "Chi phí dự kiến"]]
        
        for item in day.get('items', []):
            time_range = f"{item.get('start_time')} - {item.get('end_time')}"
            title = item.get('title')
            location = item.get('location')
            item_desc = f"<b>{title}</b><br/><font color='#64748B' size=8>{location}</font>"
            item_type = item.get('item_type')
            cost = f"{item.get('estimated_cost', 0):,} {trip_data.get('currency')}"
            
            table_data.append([
                time_range,
                Paragraph(item_desc, styles['Normal']),
                item_type,
                cost
            ])
        
        t = Table(table_data, colWidths=[90, 260, 90, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
