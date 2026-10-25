import io
import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def _setup_vietnamese_font() -> str:
    """
    Registers a high-quality Unicode font family (Arial/Tahoma/Segoe UI)
    that completely supports Vietnamese diacritics.
    """
    font_candidates = [
        # Windows system fonts
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
        ("C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/tahomabd.ttf"),
        ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"),
        ("C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/calibrib.ttf"),
        # Linux system fonts
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        # Local fonts
        (os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'DejaVuSans.ttf'),
         os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'DejaVuSans-Bold.ttf')),
    ]

    for reg_path, bold_path in font_candidates:
        if os.path.exists(reg_path):
            try:
                font_name = "VietnameseFont"
                bold_name = "VietnameseFont-Bold" if os.path.exists(bold_path) else "VietnameseFont"

                pdfmetrics.registerFont(TTFont(font_name, reg_path))
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                    registerFontFamily(font_name, normal=font_name, bold=bold_name)
                else:
                    registerFontFamily(font_name, normal=font_name, bold=font_name)
                return font_name
            except Exception as e:
                print(f"Failed to register font {reg_path}: {e}")
                continue

    # Fallback to Helvetica if no Vietnamese font found
    print("Warning: No Vietnamese font found, using Helvetica (may not display Vietnamese correctly)")
    return "Helvetica"

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

    font_name = _setup_vietnamese_font()
    bold_font = f"{font_name}-Bold" if f"{font_name}-Bold" in pdfmetrics.getRegisteredFontNames() else font_name

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        fontName=bold_font,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName=font_name,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#334155'),
        spaceAfter=15
    )

    day_header_style = ParagraphStyle(
        'DayHeader',
        fontName=bold_font,
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1D4ED8'),
        spaceBefore=14,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        'TableNormal',
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    header_cell_style = ParagraphStyle(
        'TableHeader',
        fontName=bold_font,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Document Header
    title_text = trip_data.get('title', 'Lịch Trình Du Lịch Thông Minh')
    story.append(Paragraph(f"<b>{title_text}</b>", title_style))
    
    days = trip_data.get('days', [])
    start_date_display = (days[0].get('date') if days and days[0].get('date') else trip_data.get('start_date', '2026-11-01'))
    end_date_display = (days[-1].get('date') if days and days[-1].get('date') else trip_data.get('end_date', '2026-11-07'))

    meta_info = (
        f"<b>Điểm đến:</b> {trip_data.get('destination', 'Điểm đến')} | "
        f"<b>Khởi hành:</b> {trip_data.get('origin', 'Hà Nội')} | "
        f"<b>Thời gian:</b> {start_date_display} đến {end_date_display} | "
        f"<b>Số khách:</b> {trip_data.get('travelers', 2)} người | "
        f"<b>Ngân sách:</b> {trip_data.get('budget', 0):,.0f} {trip_data.get('currency', 'VND')}"
    )
    story.append(Paragraph(meta_info, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=12))

    days = trip_data.get('days', [])
    for day in days:
        day_title = f"Ngày {day.get('day_number')} ({day.get('date')})"
        story.append(Paragraph(f"<b>{day_title}</b>", day_header_style))
        
        table_data = [[
            Paragraph("<b>Thời gian</b>", header_cell_style),
            Paragraph("<b>Hoạt động & Địa điểm</b>", header_cell_style),
            Paragraph("<b>Loại hình</b>", header_cell_style),
            Paragraph("<b>Chi phí dự kiến</b>", header_cell_style)
        ]]
        
        for item in day.get('items', []):
            time_range = f"{item.get('start_time')} - {item.get('end_time')}"
            title = item.get('title', '')
            location = item.get('location', '')
            notes = item.get('notes', '')
            
            desc_text = f"<b>{title}</b>"
            if location:
                desc_text += f"<br/><font color='#64748B' size=8>📍 {location}</font>"
            if notes:
                desc_text += f"<br/><font color='#0284C7' size=8>💡 {notes}</font>"
            
            item_type = item.get('item_type', 'HOẠT ĐỘNG')
            cost = f"{item.get('estimated_cost', 0):,.0f} {trip_data.get('currency', 'VND')}"
            
            table_data.append([
                Paragraph(time_range, normal_style),
                Paragraph(desc_text, normal_style),
                Paragraph(item_type, normal_style),
                Paragraph(cost, normal_style)
            ])
        
        t = Table(table_data, colWidths=[80, 270, 85, 105])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

    # Footer notice
    story.append(Spacer(1, 10))
    notice_style = ParagraphStyle(
        'FooterNotice',
        fontName=font_name,
        fontSize=8,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1
    )
    story.append(Paragraph("Lịch trình được tối ưu hoá và tạo tự động bởi Hệ Thống AI Travel Agent Platform", notice_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
