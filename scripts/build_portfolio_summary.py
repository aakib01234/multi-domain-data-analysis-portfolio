"""Build the cross-project executive summary PDF."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"reports"/"00_portfolio_executive_summary.pdf"
projects=[
 ("Retail","2,500","Rs 10.04M sales","Electronics leads revenue; Saturday has the strongest average basket.",ROOT/"visualizations/project1_sales/01_category_revenue.png"),
 ("Education","1,200","93.8% pass rate","Attendance and study time associate with performance; 321 students are flagged for review.",ROOT/"visualizations/project2_students/03_attendance_correlation.png"),
 ("Weather","6,576","6 cities / 3 years","Chennai is warmest and wettest in the simulation; seasonal exposure differs sharply by city.",ROOT/"visualizations/project3_weather/03_seasonal_heatmap.png"),
 ("Healthcare","1,800","50.2% favourable","Outcome comparisons require condition/severity stratification and remain descriptive.",ROOT/"visualizations/project4_healthcare/01_treatment_improvement.png"),
 ("Finance","3,910","15.1% portfolio return","The simulated equal-weight portfolio shows 15.6% volatility and -18.0% maximum drawdown.",ROOT/"visualizations/project5_finance/03_risk_return.png")]

def build():
  navy=colors.HexColor('#0F172A'); blue=colors.HexColor('#2563EB'); pale=colors.HexColor('#EFF6FF'); styles=getSampleStyleSheet()
  styles.add(ParagraphStyle(name='T',parent=styles['Title'],fontSize=24,leading=30,alignment=TA_CENTER,textColor=navy)); styles.add(ParagraphStyle(name='H',parent=styles['Heading2'],fontSize=15,leading=19,textColor=blue,spaceBefore=8,spaceAfter=7)); styles.add(ParagraphStyle(name='B',parent=styles['BodyText'],fontSize=9.5,leading=14,textColor=navy,spaceAfter=6))
  doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=17*mm,bottomMargin=16*mm)
  story=[Spacer(1,18*mm),Paragraph("MULTI-DOMAIN DATA ANALYSIS PORTFOLIO",styles['T']),Paragraph("Executive Summary | Five Complete Python Projects",ParagraphStyle(name='S',parent=styles['Heading2'],alignment=TA_CENTER,textColor=blue)),Spacer(1,12*mm)]
  story += [Table([["PROJECTS","5"],["CLEAN RECORDS","15,986"],["VISUALIZATIONS","25"],["AUTOMATED TESTS","15"]],colWidths=[60*mm,70*mm],style=[('BACKGROUND',(0,0),(-1,-1),pale),('TEXTCOLOR',(0,0),(0,-1),blue),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#BFDBFE')),('PADDING',(0,0),(-1,-1),9)]),Spacer(1,13*mm),Paragraph("Portfolio Purpose",styles['H']),Paragraph("This portfolio demonstrates a reproducible workflow from imperfect raw data to validated datasets, descriptive statistics, professional visualizations, responsible interpretation, actionable recommendations, testing, and executive communication.",styles['B']),PageBreak()]
  story += [Paragraph("Cross-Project Overview",styles['H'])]
  table=[["Domain","Clean records","Headline result"]]+[[d,n,k] for d,n,k,_,_ in projects]
  story += [Table(table,colWidths=[35*mm,35*mm,85*mm],style=[('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5E1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('VALIGN',(0,0),(-1,-1),'TOP'),('PADDING',(0,0),(-1,-1),7)]),Spacer(1,8*mm),Paragraph("Shared workflow",styles['H']),Paragraph("Validate schema and quality; clean without overwriting raw data; engineer auditable features; calculate mean, median, correlations, trends, and domain KPIs; visualize evidence; state limitations; test critical logic; generate executive reports.",styles['B']),PageBreak()]
  for domain,records,kpi,insight,img in projects:
    story += [Paragraph(f"{domain} Analysis",styles['H']),Paragraph(f"<b>Scale:</b> {records} cleaned records &nbsp;&nbsp; <b>Headline:</b> {kpi}",styles['B']),Image(str(img),width=172*mm,height=92*mm),Paragraph(f"<b>Interpretation:</b> {insight}",styles['B']),PageBreak()]
  story += [Paragraph("Technical Quality and Responsible Use",styles['H']),Paragraph("Fifteen automated tests reconcile validation, cleaning, feature engineering, classification rules, returns, and KPIs. Fixed seeds make every simulated dataset reproducible, while reusable domain modules separate calculations from presentation.",styles['B']),Paragraph("All data is simulated. Healthcare findings are not clinical guidance; finance findings are not investment advice; weather thresholds are not official warnings; student risk flags require human review. Correlations are associations rather than proof of causality.",styles['B']),Paragraph("Submission Package",styles['H']),Paragraph("Five notebooks, five project reports, twenty-five charts, raw and cleaned data, validation files, reusable Python modules, build scripts, test evidence, complete documentation, presentation deck, demo script, and final checklist.",styles['B'])]
  def footer(canvas,doc): canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#64748B')); canvas.drawString(16*mm,9*mm,'Multi-Domain Data Analysis Portfolio'); canvas.drawRightString(194*mm,9*mm,f'Page {doc.page}'); canvas.restoreState()
  doc.build(story,onFirstPage=footer,onLaterPages=footer); print(f"Created {OUT.name}")

if __name__=='__main__': build()
