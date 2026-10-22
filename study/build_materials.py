"""Build report sources and figures from saved pilot evidence.

Requires reportlab, python-docx, Pillow and pdftoppm for authoring only.
The simulation itself remains standard-library-only.
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT/'progress'
FIGURES = PROGRESS/'figures'
TMP = ROOT/'tmp'/'progress_artifacts'
POPPLER = Path('/Users/huangzhenxuan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm')
BLUE = colors.HexColor('#185C91')
ORANGE = colors.HexColor('#AC581D')
COURSE_COLORS = [BLUE, ORANGE, colors.HexColor('#367A55')]


def read_csv(name):
    with (PROGRESS/'results'/name).open() as f: return list(csv.DictReader(f))


SUMMARY = {(r['scenario'], r['condition'], r['metric']): r for r in read_csv('summary.csv')}
PAIRED = {(r['scenario'], r['metric']): r for r in read_csv('paired_summary.csv')}


def mean(scenario, arm, metric): return float(SUMMARY[scenario, arm, metric]['mean'])
def fmt(value, digits=4): return f'{value:.{digits}f}'
def pair(scenario, metric): return float(PAIRED[scenario, metric]['mean_difference'])


def text(d, x, y, value, size=10, color=colors.black, anchor='start'):
    d.add(String(x, y, value, fontName='Helvetica', fontSize=size, fillColor=color, textAnchor=anchor))


def line_panel(d, origin, size, title, series, xlimits, ylimits, xsteps, ysteps, palette=None):
    x, y = origin; w, h = size
    p = LinePlot(); p.x=x+40; p.y=y+30; p.width=w-53; p.height=h-62
    p.data=[points for _, points in series]
    p.xValueAxis.valueMin, p.xValueAxis.valueMax=xlimits
    p.xValueAxis.valueSteps=xsteps
    p.yValueAxis.valueMin, p.yValueAxis.valueMax=ylimits
    p.yValueAxis.valueSteps=ysteps
    for axis in [p.xValueAxis, p.yValueAxis]:
        axis.labels.fontName='Helvetica'; axis.labels.fontSize=8
        axis.strokeColor=colors.HexColor('#9BA8B3')
    p.yValueAxis.visibleGrid=True
    p.yValueAxis.gridStrokeColor=colors.HexColor('#E1E7EB')
    for i in range(len(series)):
        p.lines[i].strokeColor=(palette or [BLUE,ORANGE])[i]
        p.lines[i].strokeWidth=1.8
        p.lines[i].symbol=makeMarker('FilledCircle')
        p.lines[i].symbol.size=3.8
    d.add(p)
    text(d,x+8,y+h-14,title,11)
    return p


def legend(d, entries, y=8):
    x=55
    for label,color in entries:
        d.add(Line(x,y+3,x+17,y+3,strokeColor=color,strokeWidth=2))
        text(d,x+22,y,label,9)
        x+=125


def export_figure(name, drawing):
    FIGURES.mkdir(parents=True,exist_ok=True); TMP.mkdir(parents=True,exist_ok=True)
    pdf=TMP/f'{name}.pdf'
    renderPDF.drawToFile(drawing,str(pdf))
    renderSVG.drawToFile(drawing,str(FIGURES/f'{name}.svg'))
    binary=str(POPPLER) if POPPLER.exists() else 'pdftoppm'
    subprocess.run([binary,'-singlefile','-r','160','-png',str(pdf),str(FIGURES/name)],check=True,capture_output=True)


def build_figures():
    ns=[30,60,90]
    d=Drawing(600,235)
    for i,(metric,title) in enumerate([('mean_utility','Allocated course value'),('mean_net_utility','Value after switching costs')]):
        series=[(arm,[(n,mean(f'baseline_N{n}',arm,metric)) for n in ns]) for arm in ['visible','hidden']]
        line_panel(d,(i*300,17),(300,218),title,series,(25,95),(0,1),ns,[0,.25,.5,.75,1])
    legend(d,[('Visible',BLUE),('Hidden',ORANGE)])
    export_figure('utility_by_competition',d)

    d=Drawing(600,220)
    series=[(arm,[(n,mean(f'baseline_N{n}',arm,'switches')) for n in ns]) for arm in ['visible','hidden']]
    line_panel(d,(15,15),(570,205),'Mean total course changes per run',series,(25,95),(0,100),ns,[0,25,50,75,100])
    legend(d,[('Visible',BLUE),('Hidden',ORANGE)])
    export_figure('switches_by_competition',d)

    rounds=read_csv('rounds.csv'); groups=defaultdict(list)
    for r in rounds:
        if r['scenario']=='baseline_N60' and r['phase'] in ['initial','after_decisions']:
            groups[r['condition'],int(r['course']),int(r['round'])].append(int(r['pending']))
    d=Drawing(600,245)
    for i,arm in enumerate(['visible','hidden']):
        series=[(str(j),[(t,statistics.mean(groups[arm,j,t])) for t in range(13)]) for j in range(3)]
        line_panel(d,(i*300,20),(300,225),f'{arm.capitalize()} pending requests',series,(0,12),(0,45),[0,3,6,9,12],[0,15,30,45],COURSE_COLORS)
    legend(d,[(f'Course {chr(65+j)}',c) for j,c in enumerate(COURSE_COLORS)])
    export_figure('pending_trajectories',d)

    flows=read_csv('flows.csv'); counts=defaultdict(list)
    for r in flows:
        if r['scenario']=='baseline_N60' and int(r['round'])<=3:
            counts[r['condition'],int(r['course'])].append(int(r['arrivals']))
    # Sum first three ticks within each seed, then average over 30 seeds.
    bar_data=[tuple(sum(counts[arm,j])/30 for j in range(3)) for arm in ['visible','hidden']]
    d=Drawing(600,185); b=VerticalBarChart()
    b.x=58;b.y=36;b.width=500;b.height=115;b.data=bar_data
    b.categoryAxis.categoryNames=['A','B','C'];b.categoryAxis.labels.fontSize=9
    b.valueAxis.valueMin=0;b.valueAxis.valueMax=max(10,math_ceiling(max(max(x) for x in bar_data),5))
    b.valueAxis.labels.fontSize=8;b.valueAxis.visibleGrid=True
    b.valueAxis.gridStrokeColor=colors.HexColor('#E1E7EB')
    b.bars[0].fillColor=BLUE;b.bars[1].fillColor=ORANGE
    b.groupSpacing=20;b.barSpacing=4
    d.add(b);text(d,10,169,'Switch arrivals before the first approval batch',11)
    legend(d,[('Visible',BLUE),('Hidden',ORANGE)],y=8)
    export_figure('switch_destinations',d)

    d=Drawing(600,120)
    labels=[['Observe allowed','information'],['Estimate benefits','and choose'],['Commit changes','with new timestamps'],['Approve if','batch is due'],['Record state','and continue']]
    for i,lines in enumerate(labels):
        x=4+i*120
        d.add(Rect(x,42,108,58,rx=5,ry=5,fillColor=colors.HexColor('#EDF3F7'),strokeColor=colors.HexColor('#889EAE')))
        text(d,x+54,77,lines[0],9,anchor='middle');text(d,x+54,62,lines[1],9,anchor='middle')
        if i<4:
            d.add(Line(x+109,71,x+117,71,strokeColor=BLUE,strokeWidth=1.5))
            d.add(Polygon([x+119,71,x+114,74,x+114,68],fillColor=BLUE,strokeColor=BLUE))
    text(d,300,19,'All choices use a shared tick-start snapshot; approvals occur after commits.',9,anchor='middle')
    export_figure('event_flow',d)


def math_ceiling(value,step):
    import math
    return step*math.ceil(value/step)


def inline(p,value):
    token=re.compile(r'\*\*[^*]+\*\*|\*[^*]+\*|https?://[^\s]+')
    pos=0
    for m in token.finditer(value):
        if m.start()>pos: p.add_run(value[pos:m.start()])
        s=m.group()
        if s.startswith('**'): p.add_run(s[2:-2]).bold=True
        elif s.startswith('*'): p.add_run(s[1:-1]).italic=True
        else:
            url=s.rstrip('.,'); rid=p.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
            h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rid)
            r=OxmlElement('w:r');pr=OxmlElement('w:rPr');co=OxmlElement('w:color');co.set(qn('w:val'),'185C91');pr.append(co);r.append(pr)
            t=OxmlElement('w:t');t.text=url;r.append(t);h.append(r);p._p.append(h)
            if len(url)<len(s):p.add_run(s[len(url):])
        pos=m.end()
    if pos<len(value):p.add_run(value[pos:])
    if re.search(r'[\u3400-\u9fff]',value):
        for r in p.runs:
            r.font.name='Arial Unicode MS'
            fonts=r._element.get_or_add_rPr().rFonts
            for attr in ['ascii','hAnsi','eastAsia','cs']:
                fonts.set(qn('w:'+attr),'Arial Unicode MS')


class Material:
    def __init__(self,title):
        self.doc=Document();self.md=[];self.title=title
        sec=self.doc.sections[0];sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
        sec.top_margin=Inches(.65);sec.bottom_margin=Inches(.65);sec.left_margin=Inches(.76);sec.right_margin=Inches(.76)
        sec.footer_distance=Inches(.3)
        for name in ['Normal','Title','Heading 1','Heading 2','Caption']:
            s=self.doc.styles[name];s.font.name='Arial';s.font.color.rgb=RGBColor(0,0,0)
            rf=s.element.get_or_add_rPr();fonts=rf.find(qn('w:rFonts'))
            if fonts is None:fonts=OxmlElement('w:rFonts');rf.insert(0,fonts)
            fonts.set(qn('w:ascii'),'Arial');fonts.set(qn('w:hAnsi'),'Arial');fonts.set(qn('w:eastAsia'),'Arial Unicode MS')
            pr=s.element.get_or_add_pPr()
            for b in list(pr.findall(qn('w:pBdr'))):pr.remove(b)
        s=self.doc.styles['Normal'];s.font.size=Pt(10.5);s.paragraph_format.line_spacing=1.12;s.paragraph_format.space_after=Pt(6)
        for name,size in [('Title',18),('Heading 1',14),('Heading 2',11)]:
            s=self.doc.styles[name];s.font.size=Pt(size);s.font.bold=True;s.paragraph_format.keep_with_next=True
            s.paragraph_format.space_before=Pt(8);s.paragraph_format.space_after=Pt(6)
        self.doc.styles['Caption'].font.size=Pt(9)
        self.doc.styles['Caption'].paragraph_format.space_after=Pt(6)
        footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        r=footer.add_run('COMP1110 | ');r.font.size=Pt(8)
        fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
        self.h(title,0)

    def h(self,value,level=1):
        p=self.doc.add_paragraph(style='Title' if level==0 else f'Heading {level}')
        inline(p,value)
        self.md.append('#'*(level+1)+' '+value+'\n')

    def p(self,value,style=None):
        p=self.doc.add_paragraph(style=style);inline(p,value);self.md.append(value+'\n');return p

    def bullet(self,value):self.p('- '+value)

    def page(self):self.doc.add_page_break();self.md.append('\n<!-- page break -->\n')

    def table(self,headers,rows,widths=None):
        t=self.doc.add_table(rows=1,cols=len(headers));t.autofit=False
        widths=widths or [6.75/len(headers)]*len(headers)
        for j,w in enumerate(widths):t.columns[j].width=Inches(w)
        for i,row in enumerate([headers]+list(rows)):
            cells=t.rows[0].cells if i==0 else t.add_row().cells
            trpr=cells[0]._tc.getparent().get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
            if i==0:trpr.append(OxmlElement('w:tblHeader'))
            for j,(cell,value) in enumerate(zip(cells,row)):
                cell.width=Inches(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.06
                inline(p,str(value))
                for r in p.runs:r.font.size=Pt(9.2);r.bold=True if i==0 else r.bold
                tcpr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
                for side in ['top','left','bottom','right']:
                    b=OxmlElement('w:'+side);b.set(qn('w:val'),'single');b.set(qn('w:color'),'D9D9D9');b.set(qn('w:sz'),'4');borders.append(b)
                tcpr.append(borders)
                mar=OxmlElement('w:tcMar')
                for side,val in [('top',65),('bottom',65),('start',85),('end',85)]:
                    x=OxmlElement('w:'+side);x.set(qn('w:w'),str(val));x.set(qn('w:type'),'dxa');mar.append(x)
                tcpr.append(mar)
                if i==0 or i%2==0:
                    shd=OxmlElement('w:shd');shd.set(qn('w:fill'),'EAF0F5' if i==0 else 'F8FAFB');tcpr.append(shd)
        self.md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |')
        self.md.extend('| '+' | '.join(str(v) for v in row)+' |' for row in rows);self.md.append('')
        self.doc.add_paragraph().paragraph_format.space_after=Pt(0)

    def figure(self,name,caption,width=6.65):
        p=self.doc.add_paragraph();p.paragraph_format.space_after=Pt(2)
        p.add_run().add_picture(str(FIGURES/f'{name}.png'),width=Inches(width))
        self.p(caption,'Caption');self.md.append(f'![{caption}](figures/{name}.png)\n')

    def save(self,name):
        self.doc.core_properties.title=self.title;self.doc.core_properties.author='COMP1110 Project Team'
        self.doc.save(PROGRESS/f'{name}.docx')
        (PROGRESS/f'{name}.md').write_text('\n'.join(self.md)+'\n')


def report():
    m=Material('Queue Position Visibility in HKU Common Core Course Selection')
    m.p('**Interim research progress report | 20 October 2026**')
    m.p('Team: [Member 1], [Member 2], [Member 3], [Member 4], [Member 5]')
    m.h('Progress and preliminary findings')
    m.p('We have implemented and checked a small synthetic simulation of the question in our Project Plan: how does seeing one\'s queue position change course-selection decisions and the distribution of requests? The completed pilot has 300 runs, arranged as 150 visible/hidden pairs. The results show a trade-off: more rank information can improve placement while inducing extra changes that reduce net utility under an assumed cost.')
    rows=[]
    for n in [30,60,90]:
        s=f'baseline_N{n}'
        rows.append([str(n),f"{mean(s,'visible','placement_rate'):.1%} / {mean(s,'hidden','placement_rate'):.1%}",
                     f"{mean(s,'visible','switches'):.1f} / {mean(s,'hidden','switches'):.1f}",
                     f"{mean(s,'visible','mean_net_utility'):.4f} / {mean(s,'hidden','mean_net_utility'):.4f}"])
    m.table(['Students','Placement V / H','Changes V / H','Net utility V / H'],rows,[.7,1.7,1.7,2.65])
    m.p('V = visible; H = hidden. Entries are means across 30 matched seeds; each run has 45 seats. Utilities are synthetic preference units per original student, including those left unplaced. Values rounded for presentation; complete precision is retained in CSV files.')
    m.p(f"At N=60, visible students obtained mean allocated-course value {mean('baseline_N60','visible','mean_utility'):.4f}, compared with {mean('baseline_N60','hidden','mean_utility'):.4f} when rank was hidden. After deducting change costs, the comparison became {mean('baseline_N60','visible','mean_net_utility'):.4f} versus {mean('baseline_N60','hidden','mean_net_utility'):.4f}. The small average value gain was not consistent across seeds: only {PAIRED['baseline_N60','mean_utility']['positive_pairs']} of 30 paired raw-utility differences were positive.")
    m.h('Completed work',2)
    m.bullet('Specified queue states, timestamp surrender, allowed information, belief rules, decision order and output definitions.')
    m.bullet('Checked an analytic two-person example and 15 automated tests; exported decision, event, student, flow and round records.')
    m.bullet('Completed the main 180 runs and 120 sensitivity runs; rechecked eight references and official HKU rules.')
    m.p('The findings are conditional on this model. No real student records were used, and no effect on actual SIS/server congestion has been measured.')

    m.page();m.h('Model and event order')
    m.p('The model represents the ordinary FCFS selection period. Public HKU guidance provides the institutional basis; one-course demand, utility values and the precise event schedule are our simplifying assumptions (HKU Common Core, n.d.-a, n.d.-b).')
    m.table(['Setting','Implemented value'],[
        ['Courses and capacities','A, B, C; 15 seats each; fixed throughout a run'],
        ['Students and initial preference','N = 30, 60 or 90; favourite probabilities 0.60, 0.25, 0.15'],
        ['Course values','Favourite = 1; alternatives independently Uniform(0.3, 0.8)'],
        ['Revision effort cost','0.05 per actual switch; 0.15 in the higher-cost check'],
        ['Timing','12 ticks; approval after ticks 3, 6, 9 and 12'],
        ['Expected departures','0.10 before the next approval, used only as a belief'],
        ['Rank refresh','Every tick; every third tick in the slower-refresh check']],[1.7,5.05])
    m.figure('event_flow','Figure 1. Decisions are computed before any switch is committed. The sequence repeats for 12 ticks.')
    m.p('Students submit to their favourites initially; a seeded permutation supplies their timestamps. Only pending students revise. All revisions use the tick-start snapshot, then a shared random commit order gives new timestamps. Approval takes the earliest requests up to capacity. Full courses accept no new requests, but existing pending requests are retained until final expiry.')
    m.p('Approved students do not drop in this baseline. There are no later arrivals or external random withdrawals. Consequently, new places stop appearing once all seats are filled. The 15-seat setting is a scaled example: HKU\'s real under-20-enrolment cancellation rule is explicitly omitted and is not represented by these capacities.')

    m.page();m.h('How information changes a decision')
    m.p('Both arms know vacancies and their approval status. Visible agents additionally know their own latest disclosed rank. They never observe the true queue for an alternative course. A rank is tied to its course and invalidated on switching; between refreshes a retained rank may be stale.')
    m.p('For own rank r and v vacancies, the next-approval forecast is **g(r,v) = P[Binomial(r-1, 1-rho) < v]**. Rho is the subjective probability that someone ahead leaves before that batch. Real departures are generated by other agents\' decisions, so this forecast may be wrong.')
    m.p('Hidden agents estimate pending demand as lambda_j = max(0, N*s_j - a_j), where s_j is the synthetic favourite share and a_j is publicly inferable approvals. With m = max(1, ceil(lambda_current)), they average g over ranks 1 through m. Both arms forecast a new alternative request using P[Poisson(lambda_j*(1-rho)) < v_j]. These are explicit heuristics, not calibrated HKU admission probabilities or optimal Bayesian strategies.')
    m.p('An agent switches only if value(alternative)*forecast(alternative) - cost exceeds value(current)*forecast(current). Ties stay. This decision concerns the next batch, not a full forward-looking equilibrium. We separately measure final realised utility.')
    m.h('Hand calculation checked against the program',2)
    m.p('A and B each have one seat. S values A=10, B=5 and pays cost 1; the other student stays with A. Set rho=0. The two initial orders are equally likely. Hidden S estimates a 50% chance at A, so staying is worth 5 versus 4 for switching.')
    m.table(['Actual rank of S','Visible choice and net result','Hidden choice and net result'],[
        ['1','Stay at A: 10','Stay at A: 10'],
        ['2','Switch to B: 5 - 1 = 4','Stay at A, no seat: 0'],
        ['Equal-weight expectation','(10 + 4)/2 = 7','(10 + 0)/2 = 5']],[1.2,2.8,2.75])
    m.p('This constructed example shows that useful information can improve a decision. It is checked in the same engine using controlled inputs. Its values and fixed second student differ from the larger pilot; it is not a general proof that visibility improves outcomes.')

    m.page();m.h('Outcomes across competition levels')
    m.figure('utility_by_competition','Figure 2. Mean raw and net preference utility versus N. Each point averages 30 seeds; the total capacity remains 45. Lines connect tested settings only.')
    m.figure('switches_by_competition','Figure 3. Mean total course changes per run. More changes can help obtain a seat or add effort costs; counts alone do not establish irrational behaviour.')
    m.p(f"At N=30, both arms placed every student and their mean utilities were almost identical. At N=90, visible agents made {mean('baseline_N90','visible','switches'):.1f} changes versus {mean('baseline_N90','hidden','switches'):.1f}; mean net utility was {mean('baseline_N90','visible','mean_net_utility'):.4f} versus {mean('baseline_N90','hidden','mean_net_utility'):.4f}. Scarcity and the cost assumption therefore matter to the information/outcome relationship.")
    m.p(f"For N=60, the SD of the 30 paired raw-utility differences was {float(PAIRED['baseline_N60','mean_utility']['sd_across_pairs']):.4f}, larger than their mean difference of {pair('baseline_N60','mean_utility'):.4f}. We report both the mean and variation; the data do not establish a stable universal welfare gain. These are Monte Carlo outcomes under chosen assumptions, not statistical estimates from HKU students.")

    m.page();m.h('Application distribution and switching flows')
    m.figure('pending_trajectories','Figure 4. Mean pending requests at N=60. Tick 0 is initial; later observations are after changes but before that tick\'s approval. The first approval is after tick 3. Approved students are no longer counted in these queues.')
    m.figure('switch_destinations','Figure 5. Mean switch-arrival events to each course in ticks 1-3, averaged over 30 runs. Repeated arrivals by the same student count as separate events.')
    m.p('The exported flow counts identify where changes go, while the queue trajectories identify whether those changes accumulate. Together they allow us to investigate concentration on alternatives. They do not reveal whether real students herd.')
    m.p('Pending HHI is also exported, but it can rise merely because a small number of unsuccessful students remain in one queue. For that reason, we do not interpret a high peak HHI as sufficient evidence of harmful herding. We retain total pending counts, capacities and actual inflows/outflows for the same observation phase.')

    m.page();m.h('Sensitivity checks and limitations')
    rows=[]
    for s,label in [('baseline_N60','Baseline'),('higher_cost_N60','Cost 0.15'),('slower_rank_N60','Refresh every 3 ticks')]:
        rows.append([label,f"{mean(s,'visible','switches'):.1f}",f"{mean(s,'hidden','switches'):.1f}",
                     f"{mean(s,'visible','mean_net_utility'):.4f}",f"{mean(s,'hidden','mean_net_utility'):.4f}"])
    m.table(['N=60 setting','V changes','H changes','V net','H net'],rows,[2.15,1.05,1.05,1.25,1.25])
    m.p(f"Raising the change cost reduced switching in both arms but did not remove the net-utility disadvantage of visibility in that tested setting. Changing rank refresh to every third tick reduced visible-arm changes and reversed the sign of the mean visible-minus-hidden net comparison. Only {PAIRED['slower_rank_N60','mean_net_utility']['positive_pairs']} of the 30 slower-refresh paired net differences were positive, however, so this mean reversal is not a reliable recommendation for every population.")
    m.p('Raw utility is the value of the assigned course, zero if unplaced, averaged over all original students. Net utility subtracts every actual switching cost, including costs paid by those eventually unplaced. All generated course values are positive, so acceptable placement equals placement. Neither metric is an observed measure of real satisfaction.')
    m.p('The operation index is scheduled status checks + 2*switches. Rank refreshes are separately counted only in the visible arm. The schedule is imposed and public vacancy/status metadata are supplied every tick. The index omits initial requests and backend work; slower imposed checking mechanically reduces part of it. It cannot establish real traffic, latency or SIS congestion.')
    m.h('Main obstacles and next experiments',2)
    m.table(['Limitation','Consequence and planned check'],[
        ['No real queue logs or measured beliefs','Treat results as conditional; vary prior multiplier 0.5/1.5 and rho 0/0.3.'],
        ['Static forecasts and correlated actions','Compare sequential decisions with the present shared-snapshot design.'],
        ['Synthetic values and a single desired seat','Vary alternative values to 0.1-0.4 and 0.6-0.9; report multiple-course omission.'],
        ['No strategic drops after approval','Add an explicit withdrawal/arrival extension separately; no hidden withdrawal process in this pilot.']],[1.95,4.8])
    m.p('The follow-up scenarios above are specified but not included in the 300 completed runs. No personal data are collected. Any later student survey would require consent and careful handling of responses.')

    m.page();m.h('Literature and mechanism audit')
    source_notes=[
        ('HKU selection guidance','HKU Common Core (n.d.-a) documents ordinary August timestamped FCFS, position/vacancy visibility, periodic approval, CCTM priority exceptions and a separate auto-ballot add/drop period. It establishes procedure, not behavioural effects. Exact FCFS batch times are not stated.'),
        ('HKU FAQ','HKU Common Core (n.d.-b) clarifies surrender of queue position, full-class closure and approved-course drop/add. Therefore one-course demand and frozen approved allocations are model simplifications, not HKU restrictions. The exact interaction of pending approvals and reopening remains unspecified.'),
        ('Course allocation and manipulation','Budish and Cantillon (2012) use theory and Harvard field data to identify manipulation and welfare costs in a course draft, while the draft can outperform its studied alternative. The paper does not isolate personal FCFS rank visibility.'),
        ('Matching mechanisms','Diebold et al. (2014) review stable matching and include a field experiment. This supports mechanism/incentive analysis; it is not an evaluation of a rank-display treatment in the present model.'),
        ('Strategic adjustments','Romero-Medina and Triossi (2024) study conditional acceptance and repeated adjustment. Their adjustment mechanism differs from HKU drop/rejoin, including restrictions on dropping allocated courses. It supports examining revisions, not importing their conclusions.'),
        ('Information and search','Arteaga et al. (2022) study personalised placement-risk feedback in Chile and New Haven using experimental/quasi-experimental designs. Feedback can help search and placement. New Haven uses truncated DA; the settings are not university FCFS queues.'),
        ('Information and distributions','Sato and Shirakawa (2025) theoretically connect disclosure of admissions priorities with application distributions. They do not empirically study repeated course-queue revision or the present timestamp mechanism.'),
        ('Feedback in another queueing setting','Zou et al. (2026) simulate information quality, frequency and adoption in Hong Kong emergency departments. This motivates robustness checks but supplies no direct evidence about course selection or SIS performance.')]
    for title,body in source_notes:m.p('**'+title+'.** '+body)
    m.p('The 20 October targeted search found limited direct evidence on the joint combination of personal rank visibility, FCFS timestamps, loss of a surrendered position and repeated course revision. This is not an exhaustive review or a claim of first discovery. The separate source audit records URLs, access limits and adjacent studies; some articles were checked through abstracts/primary records rather than a full-text reading.')

    m.page();m.h('Reproducibility and references')
    m.p('The 15 checks cover analytic probabilities, tie handling, capacity, timestamp surrender, the worked example, paired population identity, repeatability, hidden information boundaries, course-specific rank-cache invalidation, synchronous action and export/flow conservation. The saved manifest records 300 runs, 150 pairs and file hashes.')
    m.p('Run from the workspace root: **python3 -m unittest discover -s study/tests -v**, then **python3 -m study.run_study --output progress/results**. The simulator requires only standard Python 3.10+. Defaults and each scenario\'s effective configuration are saved in resolved_config.json.')
    m.p('Evidence: runs.csv and students.csv contain final outcomes; decisions.csv contains policy inputs/forecasts; events.csv records switches, approvals and expiry; rounds.csv and flows.csv support the figures. summary.csv and paired_summary.csv retain variation and pairwise comparisons. See study/README.md and study/model_spec.md for definitions.')
    m.h('References',2)
    refs=(ROOT/'proposal.md').read_text().split('## References\n',1)[1].strip().split('\n\n')
    for ref in refs:
        p=m.p(ref)
        p.paragraph_format.left_indent=Inches(.17);p.paragraph_format.first_line_indent=Inches(-.17)
        for r in p.runs:r.font.size=Pt(9)
    m.p('Official web guidance and citation metadata rechecked 20 October 2026. The original Project Plan remains unchanged; this report records the subsequent implementation and pilot.')
    m.save('progress_report')


def tutorial():
    m=Material('Tutorial Progress Briefing')
    m.p('**English answers and Chinese explanation | 20 October 2026**')
    m.p('Use the statements below after reviewing the model and saved results as a group. They describe completed artefacts and do not assign unverified past work to particular members.')
    m.h('1 What was the last thing your team accomplished')
    a1=(f"Our most recent completed task was a matched pilot of the simulation in our proposal. We specified the queue rules, added visible and hidden rank conditions, and checked the program against a hand-calculated example. We then completed 300 runs. In the 60-student baseline, the visible condition produced {mean('baseline_N60','visible','switches'):.1f} course changes per run, compared with {mean('baseline_N60','hidden','switches'):.1f} under hidden ranks. Placement was slightly higher, but net utility after change costs was lower. This is a preliminary finding within our synthetic model, rather than evidence about actual HKU student behaviour.")
    m.p(a1)
    m.h('2 What is the next task your team plans to undertake')
    a2=('Our next task is to test whether these patterns survive changes to the belief assumptions. We will vary how students estimate course demand and the likelihood that people ahead leave. We will also compare simultaneous decisions with students acting one at a time. Each comparison will use the same synthetic students in both information conditions. This should help us distinguish a result that depends on one forecasting rule from a pattern that persists across several reasonable settings.')
    m.p(a2)
    m.h('3 Are there any obstacles your team has encountered')
    a3=('The main obstacle is that we do not have real HKU queue logs or measured student beliefs, so we cannot calibrate the probability estimates directly. We have made those estimates explicit and started sensitivity checks. We also simplify the system to one requested course per student and stop strategic changes after approval. These assumptions keep the model manageable, but limit its realism. We can compare outcomes inside the model; we cannot infer actual SIS congestion from the number of simulated operations.')
    m.p(a3)
    m.p(f'Approximate answer lengths: {len(a1.split())}, {len(a2.split())}, {len(a3.split())} words. Rehearse each for about 30-45 seconds and keep the units clear: changes per complete run, not changes per student.')

    m.page();m.h('中文讲解与数字口径')
    m.h('第一题的回答逻辑',2)
    m.p('先说最近完成了什么：把 proposal 里的想法做成了可运行的模型，再完成了配对试验。接着给一个实际结果，并立即说明结果只属于合成模型。不要声称已经观察或证明了真实 HKU 学生的行为。')
    m.table(['数字','准确含义'],[
        ['300 次运行','5 个情景 × 2 种信息条件 × 30 个种子；不是 300 名真实学生。'],
        [f"{mean('baseline_N60','visible','switches'):.1f} 与 {mean('baseline_N60','hidden','switches'):.1f}",'60 人基准情景中，每次完整运行的平均改选总次数。'],
        [f"{mean('baseline_N60','visible','placement_rate'):.1%} 与 {mean('baseline_N60','hidden','placement_rate'):.1%}",'可见组与隐藏组的平均获批比例；总名额为 45。'],
        [f"{mean('baseline_N60','visible','mean_net_utility'):.4f} 与 {mean('baseline_N60','hidden','mean_net_utility'):.4f}",'扣除每次 0.05 改选成本后的平均净收益，包含最终没选到课的人。'],
        [f"{PAIRED['slower_rank_N60','mean_net_utility']['positive_pairs']} / 30",'慢更新情景中，可见组净收益高于隐藏组的配对数；平均差变正不代表每次都更好。']],[1.35,5.4])
    m.h('第二题的回答逻辑',2)
    m.p('我们已完成成本提高和排名慢更新两个初步检查。下一步改的是学生怎样猜测录取机会，以及学生是否同时行动。每次只改变一个条件，保持两组的学生和偏好一致，才能解释变化来自哪里。')
    m.h('第三题的回答逻辑',2)
    m.p('障碍是没有真实队列记录和学生信念数据，所以模型不能直接校准。我们采取的处理是公开假设并检查不同假设下的结果。10% 是学生预测“前面的人可能离开”的信念参数；程序没有强迫 10% 的学生随机退课。')
    m.p('在模型中，同一轮先算完所有学生的决定，再按共享随机顺序提交改选，最后才审批。已获批者停止改选；真实 HKU 允许获批后 drop/add，所以这是需要明确讲出的简化。')
    m.p('最容易混淆的三件事：排位不是录取概率；模型偏好分不是现实满意度调查；模拟操作数不是 SIS 服务器负载。')

    m.page();m.h('Likely follow up questions')
    questions=[
        ('What exactly differs between the conditions?','Only access to the latest own queue rank. Public vacancies, course values, decision rules, initial students and random commit order are matched. Neither arm receives the true queue for another course.'),
        ('How do hidden students make a decision?','They use the synthetic course-popularity prior to estimate pending demand, treat their possible positions as equally likely, and average the next-batch admission forecasts. This is a documented heuristic, not an empirically measured belief.'),
        ('Does seeing rank make students irrational?','We have not tested that claim. Every modeled switch improves estimated next-batch benefit at the time of choice. Realised benefit can be worse because forecasts omit future responses and many students act together.'),
        ('Does visibility help at all?','Yes in the controlled two-student example. In the 60-person baseline it slightly improves placement on average. However, extra changes can offset value gains when we deduct the assumed effort cost.'),
        ('Have you demonstrated herding?','We have recorded course-level inflows, outflows and queue trajectories that allow us to examine concentration. A long queue or a high HHI by itself is insufficient, especially when very few students remain pending.'),
        ('Why not use real data?','No administrative queue or server logs have been supplied. Synthetic data let us compare exactly matched information conditions. Obtaining real logs or a consented survey would be a separate data-access task.'),
        ('Is the 15-seat setup an actual HKU course?','No. It is a scaled model setting. The real low-enrolment cancellation rule is excluded, as are multiple-course bundles and special priority windows. We study a mechanism, not an exact reproduction of a course.'),
        ('Why did slower rank updates reduce changes?',f"In this tested setting agents responded less often to a newly disclosed rank. After changing course, an old rank is invalidated until the next query. The mean net comparison reversed, but only {PAIRED['slower_rank_N60','mean_net_utility']['positive_pairs']} of 30 paired comparisons favoured visibility; this is not a universal policy recommendation.")]
    for q,a in questions:m.p('**'+q+'**');m.p(a)
    m.p('中文提醒：若被问到概率公式，打开研究进度报告的第三页；若被问到比较是否公平，说明两组使用相同学生、初始顺序和按轮次固定的提交顺序。')

    m.page();m.h('TA feedback record')
    m.p('Meeting date and time: ____________________   TA: ____________________')
    m.p('Attendees: _________________________________________________________')
    m.table(['Question for the TA','Actual feedback and agreed action'],[
        ['Is the one-course and pending-only revision scope suitable?','\n\n'],
        ['Is the stated belief rule technically sufficient at COMP1110 level?','\n\n'],
        ['Which robustness comparison should be prioritised next?','\n\n'],
        ['Any change needed for the Final Report or presentation?','\n\n']],[3,3.75])
    m.table(['Action after meeting','Owner','Due date','Evidence / status'],[
        ['____________________','____________','__________','____________'],
        ['____________________','____________','__________','____________'],
        ['____________________','____________','__________','____________']],[2.8,1.15,1.15,1.65])
    m.h('Actual contribution record to be confirmed by the group',2)
    m.table(['Member','Current planned responsibility','Actual work and date'],[
        ['[Member 1]','HKU rules and limitations','___________________'],
        ['[Member 2]','Literature and output definitions','___________________'],
        ['[Member 3]','Beliefs and information comparison','___________________'],
        ['[Member 4]','Simulation and reproducibility','___________________'],
        ['[Member 5]','Figures and tutorial coordination','___________________']],[1.15,3.15,2.45])
    m.p('Complete this page after the actual meeting. Task ownership and past contributions must be confirmed by members; the prepared artefacts do not establish who personally completed each task.')
    m.save('tutorial_briefing')


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--documents-only',action='store_true')
    args=parser.parse_args()
    PROGRESS.mkdir(exist_ok=True)
    if not args.documents_only:build_figures()
    report();tutorial()
    print('Built two Word/Markdown documents from saved CSVs.' if args.documents_only else 'Built five vector/PNG figures and two Word/Markdown documents from saved CSVs.')


if __name__=='__main__':main()
