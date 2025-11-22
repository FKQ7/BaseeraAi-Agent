"""PDF report generation service."""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import base64
import logging
import os

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """PDF report generator."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_fonts()
        self._setup_custom_styles()
    
    def _register_fonts(self):
        """Register Arabic-supporting fonts."""
        try:
            font_paths = [
                'C:/Windows/Fonts/arialuni.ttf',
                'C:/Windows/Fonts/ARIALUNI.TTF',
                'C:/Windows/Fonts/arialuni.TTF',
                'C:/Windows/Fonts/ARIALUNI.ttf',
                'C:/Windows/Fonts/tahoma.ttf',
                'C:/Windows/Fonts/TAHOMA.TTF',
                'C:/Windows/Fonts/tahoma.TTF',
                'C:/Windows/Fonts/TAHOMA.ttf',
                'C:/Windows/Fonts/times.ttf',
                'C:/Windows/Fonts/TIMES.TTF',
                'C:/Windows/Fonts/times.TTF',
                'C:/Windows/Fonts/TIMES.ttf',
                'C:/Windows/Fonts/dejavu/DejaVuSans.ttf',
                'C:/Windows/Fonts/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/TTF/DejaVuSans.ttf',
            ]
            
            windows_fonts_dir = 'C:/Windows/Fonts'
            if os.path.exists(windows_fonts_dir):
                arabic_font_names = ['arialuni', 'tahoma', 'times', 'dejavu']
                for font_name in arabic_font_names:
                    for file in os.listdir(windows_fonts_dir):
                        if file.lower().startswith(font_name.lower()) and file.lower().endswith(('.ttf', '.otf')):
                            font_path = os.path.join(windows_fonts_dir, file)
                            try:
                                pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                                self.arabic_font_name = 'ArabicFont'
                                self.arabic_font_available = True
                                logger.info(f"Registered Arabic font from: {font_path}")
                                return
                            except Exception as e:
                                logger.warning(f"Failed to register font from {font_path}: {e}")
                                continue
            
            arabic_font_registered = False
            
            # Try each font path
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont('ArabicFont', path))
                        arabic_font_registered = True
                        logger.info(f"Registered Arabic font from: {path}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to register font from {path}: {e}")
                        continue
            
            if not arabic_font_registered:
                logger.warning("No Arabic-supporting font found.")
                self.arabic_font_name = 'Helvetica'
                self.arabic_font_available = False
            else:
                self.arabic_font_name = 'ArabicFont'
                self.arabic_font_available = True
                
        except Exception as e:
            logger.error(f"Error registering fonts: {e}")
            self.arabic_font_name = 'Helvetica'
            self.arabic_font_available = False
    
    def _wrap_arabic_text(self, text: str) -> str:
        """Wrap Arabic text with font tag if available."""
        if hasattr(self, 'arabic_font_available') and self.arabic_font_available:
            arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
            import re
            if re.search(arabic_pattern, text):
                arabic_font = self.arabic_font_name if hasattr(self, 'arabic_font_name') else 'Helvetica'
                return f'<font name="{arabic_font}">{text}</font>'
        return text
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        def add_style_if_not_exists(name, style):
            if name not in self.styles.byName:
                self.styles.add(style)
            else:
                existing = self.styles.byName[name]
                for attr in ['fontSize', 'textColor', 'spaceAfter', 'spaceBefore', 'alignment', 'fontName', 'leading']:
                    if hasattr(style, attr):
                        setattr(existing, attr, getattr(style, attr))
        
        add_style_if_not_exists('CustomTitle', ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=self.arabic_font_name if hasattr(self, 'arabic_font_name') else 'Helvetica-Bold'
        ))
        
        add_style_if_not_exists('SectionHeading', ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        add_style_if_not_exists('SubsectionHeading', ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#60a5fa'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        add_style_if_not_exists('ReportBodyText', ParagraphStyle(
            name='ReportBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        add_style_if_not_exists('ReportMetadata', ParagraphStyle(
            name='ReportMetadata',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            spaceAfter=5
        ))
    
    def _format_markdown(self, text: str) -> str:
        """Convert markdown to ReportLab HTML."""
        import re
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
        text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
        
        return text
        
    def generate_report(self, failure_data: dict, ai_response: str, context_used: bool, num_sources: int, photos: list = None) -> BytesIO:
        """Generate PDF report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        story = []
        
        title_text = "Baseera"
        story.append(Paragraph(title_text, self.styles['CustomTitle']))
        story.append(Paragraph("AI Materials Failure Analysis Report", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"<b>Report Generated:</b> {report_date}", self.styles['ReportMetadata']))
        if context_used:
            story.append(Paragraph(f"<b>Knowledge Base Sources:</b> {num_sources} document(s) referenced", self.styles['ReportMetadata']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Failure Case Information", self.styles['SectionHeading']))
        
        case_data = [
            ['Parameter', 'Value'],
            ['Type of Metal', failure_data.get('metal_type', 'Not provided')],
            ['Service Time', failure_data.get('service_time', 'Not provided')],
            ['Environment', failure_data.get('environment', 'Not provided')],
            ['Temperature', failure_data.get('temperature', 'Not provided')],
            ['Mechanical Load', failure_data.get('mechanical_load', 'Not provided')],
        ]
        
        case_table = Table(case_data, colWidths=[2*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        story.append(case_table)
        story.append(Spacer(1, 0.2*inch))
        
        if failure_data.get('notes'):
            story.append(Paragraph("Engineer Notes", self.styles['SubsectionHeading']))
            story.append(Paragraph(failure_data.get('notes'), self.styles['ReportBodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        if photos:
            story.append(Paragraph("Visual Evidence", self.styles['SubsectionHeading']))
            story.append(Paragraph(f"{len(photos)} photo(s) were analyzed as part of this failure case.", self.styles['ReportBodyText']))
            story.append(Spacer(1, 0.1*inch))
            
            for idx, photo in enumerate(photos[:3], 1):
                try:
                    image_data = base64.b64decode(photo.get('data', ''))
                    img = Image(BytesIO(image_data), width=4*inch, height=3*inch)
                    img.hAlign = 'CENTER'
                    story.append(Paragraph(f"<b>Photo {idx}</b>", self.styles['ReportMetadata']))
                    story.append(img)
                    story.append(Spacer(1, 0.1*inch))
                except Exception as e:
                    logger.warning(f"Could not add photo {idx} to PDF: {e}")
                    continue
        
        story.append(PageBreak())
        
        story.append(Paragraph("Failure Analysis", self.styles['SectionHeading']))
        
        lines = ai_response.split('\n')
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_markdown(para_text), self.styles['ReportBodyText']))
                    current_paragraph = []
                continue
            
            if line.startswith('#'):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_markdown(para_text), self.styles['ReportBodyText']))
                    current_paragraph = []
                
                level = len(line) - len(line.lstrip('#'))
                heading_text = line.lstrip('#').strip()
                if level == 1:
                    story.append(Paragraph(heading_text, self.styles['SectionHeading']))
                elif level == 2:
                    story.append(Paragraph(heading_text, self.styles['SubsectionHeading']))
                else:
                    story.append(Paragraph(f"<b>{heading_text}</b>", self.styles['ReportBodyText']))
            elif line.startswith('-') or (line.startswith('*') and not line.startswith('**')):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_markdown(para_text), self.styles['ReportBodyText']))
                    current_paragraph = []
                
                list_text = line.lstrip('-*').strip()
                story.append(Paragraph(f"• {self._format_markdown(list_text)}", self.styles['ReportBodyText']))
            else:
                current_paragraph.append(line)
        
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            story.append(Paragraph(self._format_markdown(para_text), self.styles['BodyText']))
        
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("─" * 60, self.styles['ReportMetadata']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>Baseera AI Materials Failure Analyst</b>", self.styles['ReportMetadata']))
        story.append(Paragraph("Powered by RAG (Retrieval-Augmented Generation) Technology", self.styles['ReportMetadata']))
        if context_used:
            story.append(Paragraph(f"Analysis informed by {num_sources} source(s) from knowledge base", self.styles['ReportMetadata']))
        story.append(Paragraph("This report is generated automatically and should be reviewed by qualified materials engineers.", self.styles['ReportMetadata']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer


def generate_pdf_report(failure_data: dict, ai_response: str, context_used: bool, num_sources: int, photos: list = None) -> BytesIO:
    """Generate PDF report."""
    generator = PDFReportGenerator()
    return generator.generate_report(failure_data, ai_response, context_used, num_sources, photos)

