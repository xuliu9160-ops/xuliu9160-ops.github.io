"""Render the CV from the same profile and paper data used by the website."""
import argparse
import json
import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, Image

parser = argparse.ArgumentParser()
parser.add_argument('--data-json', required=True)
parser.add_argument('--output', default='files/Jiaxu_Liu_CV.pdf')
args = parser.parse_args()
data = json.loads(Path(args.data_json).read_text())
p, papers = data['profile'], data['papers']
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)

# Embed an open serif family so PDF readers render and extract the same text.
font_dirs = [Path(os.environ.get('CV_FONT_DIR', 'scripts/fonts')),
             Path('/usr/share/fonts/truetype/liberation'),
             Path('/usr/share/fonts/truetype/liberation2')]
font_dir = next((d for d in font_dirs if (d/'LiberationSerif-Regular.ttf').exists()), None)
if font_dir is None:
    raise SystemExit('Install fonts-liberation or set CV_FONT_DIR to its font directory.')
for font_name, suffix in [('CVSerif','Regular'), ('CVSerif-Bold','Bold'), ('CVSerif-Italic','Italic'), ('CVSerif-BoldItalic','BoldItalic')]:
    pdfmetrics.registerFont(TTFont(font_name, str(font_dir/f'LiberationSerif-{suffix}.ttf')))
pdfmetrics.registerFontFamily('CVSerif',normal='CVSerif',bold='CVSerif-Bold',italic='CVSerif-Italic',boldItalic='CVSerif-BoldItalic')

def txt(s):
    return escape(str(s).replace('\u2013', '-').replace('\u2014', '-').replace('\u2011', '-'))

def authors(s):
    s = re.sub(r'</?strong>', lambda m: '<b>' if m.group() == '<strong>' else '</b>', s)
    return s

ink = colors.HexColor('#171b20')
muted = colors.HexColor('#48505a')
link_color = '#235577'
styles = {
    'name': ParagraphStyle('name', fontName='CVSerif-Bold', fontSize=23, leading=26, alignment=TA_LEFT, textColor=ink, spaceAfter=4),
    'contact': ParagraphStyle('contact', fontName='Times-Roman', fontSize=9.5, leading=12, alignment=TA_LEFT, textColor=muted),
    'heading': ParagraphStyle('heading', fontName='Times-Bold', fontSize=11, leading=13, textColor=ink, spaceBefore=10, spaceAfter=3, keepWithNext=True),
    'body': ParagraphStyle('body', fontName='Times-Roman', fontSize=10.2, leading=12.7, textColor=ink, spaceAfter=2),
    'small': ParagraphStyle('small', fontName='Times-Roman', fontSize=9.5, leading=11.5, textColor=muted, spaceAfter=2),
    'date': ParagraphStyle('date', fontName='Times-Roman', fontSize=9.5, leading=12.7, alignment=TA_RIGHT, textColor=muted),
    'bullet': ParagraphStyle('bullet', fontName='Times-Roman', fontSize=10.2, leading=12.7, textColor=ink, leftIndent=10, firstLineIndent=-7, spaceAfter=2),
}
for style in styles.values():
    style.fontName = style.fontName.replace('Times-Roman','CVSerif').replace('Times-Bold','CVSerif-Bold')
def para(s, style='body'):
    return Paragraph(s, styles[style])

margin = 43
width = A4[0] - 2 * margin - 12  # Account for the document frame's inner padding.
story = []
def section(title):
    story.extend([para(title.upper(), 'heading'), HRFlowable(width='100%', thickness=.45, color=colors.HexColor('#a7afb7'), spaceAfter=5)])

def row(left, right):
    t = Table([[para(left), para(txt(right), 'date')]], colWidths=[width-164,164])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    return t

header_text = [
    para(txt(p['name']), 'name'),
    para('Undergraduate Researcher | Wenzhou-Kean University', 'contact'),
    para(f'<link href="mailto:{p["email"]}" color="{link_color}">{txt(p["email"])}</link>  |  <link href="https://{p["github"]}.github.io/" color="{link_color}">{p["github"]}.github.io</link>', 'contact'),
    para(f'<link href="https://github.com/{p["github"]}" color="{link_color}">GitHub: {p["github"]}</link>', 'contact'),
]
portrait_path = Path(__file__).resolve().parents[1] / 'images' / 'portrait.jpg'
portrait = Image(str(portrait_path), width=76, height=76, kind='proportional')
header = Table([[header_text, portrait]], colWidths=[width-90,90])
header.setStyle(TableStyle([
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ('ALIGN',(1,0),(1,0),'RIGHT'),
    ('LEFTPADDING',(0,0),(-1,-1),0),
    ('RIGHTPADDING',(0,0),(-1,-1),0),
    ('TOPPADDING',(0,0),(-1,-1),0),
    ('BOTTOMPADDING',(0,0),(-1,-1),0),
]))
story.append(header)

section('Education')
e = p['education']
story.append(row(f'<b>{txt(e["institution"])}</b>', e['dates']))
story.append(para(f'{txt(e["degree"])} in {txt(e["major"])}'))
story.append(para(f'GPA: {txt(e["gpa"])}'))

section('Research Interests')
story.append(para(' · '.join(txt(x) for x in p['interests'])))

section('Research Experience')
for item in p['experience']:
    group = [row(f'<b>{txt(item["role"])}</b>', item['dates'])]
    institution = txt(item['institution'])
    if item['group']: institution += ' | ' + txt(item['group'])
    group.append(para(institution))
    group.append(para(txt(item['advisor']), 'small'))
    group += [para('- '+txt(b), 'bullet') for b in item['bullets']]
    group.append(Spacer(1,4))
    story.append(KeepTogether(group))

section('Accepted Publications')
for paper in papers['accepted']:
    group = [para('<b>'+txt(paper['title'])+'</b>'), para(authors(paper['authors']))]
    group.append(para(f'<i>{txt(paper["venue"])}</i> ({txt(paper["status"])}).  <link href="https://{p["github"]}.github.io{paper["manuscript"]}" color="{link_color}">Paper</link> | <link href="{paper["code"]}" color="{link_color}">Code</link>', 'small'))
    story.append(KeepTogether(group))

section('Manuscripts')
for paper in papers['manuscripts']:
    story.append(KeepTogether([para('<b>'+txt(paper['title'])+'</b>'), para(authors(paper['authors'])), para('Completed manuscript; '+txt(paper['status']).lower()+'.', 'small'), Spacer(1,4)]))

section('Honors and Awards')
a = p['award']
story.append(row('<b>'+txt(a['name'])+'</b>', a['dates']))
story.append(para(txt(a['institution'])))

def footer(canvas, doc):
    canvas.setTitle('Jiaxu Liu - Academic CV')
    canvas.setAuthor('Jiaxu Liu')
    canvas.setSubject('Education, research experience, publications, and honors')
    canvas.setFont('CVSerif',8)
    canvas.setFillColor(muted)
    canvas.drawCentredString(A4[0]/2,24,str(doc.page))

doc = SimpleDocTemplate(str(out),pagesize=A4,leftMargin=margin,rightMargin=margin,topMargin=35,bottomMargin=35)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
