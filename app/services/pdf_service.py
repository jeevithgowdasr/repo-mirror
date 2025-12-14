from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from io import BytesIO
from typing import Dict, Any, List
from datetime import datetime

class PDFService:
    def create_report(self, 
                      repo_url: str, 
                      score_data: Dict[str, Any], 
                      summary: str, 
                      roadmap: List[str]) -> BytesIO:
        """
        Generates a PDF report using ReportLab and returns it as an in-memory BytesIO object.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        # Custom Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        )
        h2_style = ParagraphStyle(
            'ReportH2',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#34495e')
        )
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.leading = 14
        
        # Build Story
        story = []
        
        # --- Header ---
        story.append(Paragraph("GitHub Repository Audit Report", title_style))
        story.append(Paragraph(f"<b>Target Repository:</b> {repo_url}", normal_style))
        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", normal_style))
        story.append(Spacer(1, 20))
        
        # --- Executive Summary ---
        story.append(Paragraph("1. Executive Summary", h2_style))
        
        # Score Table
        score = score_data.get("total_score", 0)
        level = score_data.get("level", "Unknown")
        
        score_color = colors.green if score >= 80 else (colors.orange if score >= 50 else colors.red)
        
        data = [
            ['Final Score', 'Classification'],
            [f'{score}/100', level]
        ]
        t = Table(data, colWidths=[2.5*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('TEXTCOLOR', (0, 1), (0, 1), score_color), # Score color
            ('FONTSIZE', (0, 1), (-1, 1), 16),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        # Assessor Note
        story.append(Paragraph("<b>Assessor's Note:</b>", normal_style))
        story.append(Paragraph(summary, normal_style))
        story.append(Spacer(1, 20))
        
        # --- Detailed Breakdown ---
        story.append(Paragraph("2. Dimensional Analysis", h2_style))
        
        breakdown = score_data.get("breakdown", {})
        
        table_data = [['Category', 'Score', 'Findings']]
        
        for category, details in breakdown.items():
            cat_score = f"{details.get('score', 0)}/{details.get('max_score', 20)}"
            
            # Format reasons into a single string with bullets
            reasons = details.get('reasons', [])
            reasons_text = "<br/>".join([f"• {r}" for r in reasons])
            
            # Add Paragraph object to cell to allow wrapping/bolding
            p_reasons = Paragraph(reasons_text, normal_style)
            
            table_data.append([category, cat_score, p_reasons])
            
        t2 = Table(table_data, colWidths=[1.5*inch, 1.0*inch, 4.0*inch])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t2)
        
        # --- Roadmap ---
        story.append(PageBreak())
        story.append(Paragraph("3. Remediation Roadmap", h2_style))
        story.append(Paragraph("Prioritized list of high-impact improvements:", normal_style))
        story.append(Spacer(1, 10))
        
        for idx, step in enumerate(roadmap, 1):
             # roadmap items might be strings or "Title: Desc"
             # Assuming simple string for now: "Title: Desc"
             if ":" in step:
                 title, desc = step.split(":", 1)
                 text = f"<b>{idx}. {title}:</b> {desc}"
             else:
                 text = f"<b>{idx}.</b> {step}"
                 
             story.append(Paragraph(text, normal_style))
             story.append(Spacer(1, 8))
             
        # --- Footer ---
        story.append(Spacer(1, 40))
        story.append(Paragraph("<i>Generated by Repository Mirror - AI Engineering Auditor</i>", ParagraphStyle('Footer', parent=normal_style, alignment=1, textColor=colors.grey)))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
