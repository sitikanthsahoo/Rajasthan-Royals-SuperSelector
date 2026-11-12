"""Build the project explanation PDF. Requires reportlab; app runtime does not."""
from pathlib import Path
import json,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'web/data/dashboard.json').read_text());M=D['meta'];P=json.loads((ROOT/'web/data/profiles.json').read_text())
OUT=ROOT/'output/pdf/SupeRR_Selector_Project_Guide.pdf';OUT.parent.mkdir(parents=True,exist_ok=True)
NAVY=colors.HexColor('#19174f');PINK=colors.HexColor('#c91d7e');MUTED=colors.HexColor('#596176');PALE=colors.HexColor('#fbeaf4');LINE=colors.HexColor('#e7e6f0')
styles=getSampleStyleSheet()
for name,size,lead,color in [('TitleRR',36,41,NAVY),('SectionRR',24,29,NAVY),('SubRR',13,18,PINK),('BodyRR',10,15,NAVY),('SmallRR',8.3,12,MUTED),('CardRR',8.5,12,NAVY)]:
 styles.add(ParagraphStyle(name,fontName='Helvetica-Bold' if name in ('TitleRR','SectionRR','SubRR') else 'Helvetica',fontSize=size,leading=lead,textColor=color,spaceAfter=10))
story=[]
def safe(x):return html.escape(str(x)).replace('≥','&gt;=').replace('–','-').replace('—','-').replace('→','-&gt;')
def para(s,style='BodyRR'):return Paragraph(s,styles[style])
def add(s,style='BodyRR'):story.append(para(s,style))
def heading(k,title,subtitle=None):
 if story:story.append(PageBreak())
 add(k.upper(),'SubRR');add(title,'SectionRR')
 if subtitle:add(subtitle,'SmallRR')
def table(rows,widths=None):
 cells=[[para(safe(c),'SmallRR') for c in row] for row in rows]
 t=Table(cells,colWidths=widths or [487/len(rows[0])]*len(rows[0]),repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('LINEBELOW',(0,0),(-1,0),.8,PINK),('LINEBELOW',(0,1),(-1,-1),.35,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]));story.append(t);story.append(Spacer(1,12))
def box(s):
 t=Table([[para(s,'BodyRR')]],colWidths=[487]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),.5,LINE),('TOPPADDING',(0,0),(-1,-1),14),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),15),('RIGHTPADDING',(0,0),(-1,-1),15)]));story.append(t);story.append(Spacer(1,15))
def screenshot(path):
 from reportlab.lib.utils import ImageReader
 w,h=ImageReader(str(path)).getSize();story.append(Image(str(path),width=487,height=487*h/w));story.append(Spacer(1,12))
def footer(c,doc):
 c.setFillColor(PINK);c.rect(0,824,A4[0],18,fill=1,stroke=0)
 c.setStrokeColor(LINE);c.line(54,45,541,45);c.setFont('Helvetica',8);c.setFillColor(MUTED)
 c.drawString(54,31,'SUPERR SELECTOR  |  PROJECT & SELECTION GUIDE');c.drawRightString(541,31,f'{doc.page:02d}')

add('SUPERR SELECTOR / PROJECT DOCUMENTATION','SubRR');story.append(Spacer(1,55))
add('The selection room.<br/>The logic behind it.','TitleRR')
add('An evidence-led cricket player-selection dashboard','SubRR')
add('A complete explanation of the data pipeline, pressure definition, selection model, dashboard, player intelligence and top-10 recommendations.')
story.append(Spacer(1,25))
table([['DATA WINDOW','MATCHES ANALYSED','LEGAL DELIVERIES'],[f"{M['date_from']} to {M['date_to']}",f"{M['analysed_matches']:,}",f"{M['legal_balls']:,}"]])
box('<b>Decision-support research, not an automatic auction decision.</b><br/>The two lists identify performance under the chosen historical pressure model. Team balance, price, fitness, consent, contracts, board clearance and IPL eligibility require separate checks.')
add('Prepared 11 November 2026. Profile references checked on the same date. Rankings use the supplied dataset, whose dates and identities have not been independently validated. Independent student project; not an official Rajasthan Royals product.','SmallRR')

heading('01 / What was built','From match data to a selection case')
add('The project answers: <b>Which batters and bowlers repeatedly outperform their peer context in pivotal T20 situations, and improve relative to their own ordinary-situation baseline?</b>')
table([['Layer','What it contributes'],['Python analysis','Cleans six CSV files, reconstructs pre-delivery state, compares matched contexts and produces ratings, reasons, audits and match evidence.'],['Rankings dashboard','Separate top-10 batter and bowler lists; Combined, IPL and T20I scopes; search, all-eligible view, CSV export and player preview.'],['Player lab','Portrait, country / representation, sourced roster snapshot, activity evidence, sample averages, strike rates, pressure situations and recent match detail.'],['Match explorer','Year, match, innings and over controls; an over-by-over pressure timeline and the reasons assigned before each delivery.'],['Methodology and report','Model definition, exclusions, eligibility explorer, reproducibility notes, a printable report and this project guide.']],[110,377])
add('How a reviewer should use it','SubRR')
add('Choose the role and scope. Read the top-10 list, select a player, and open the player lab. Check the sample size, ordinary versus pressure performance, reasons and alternative ranks. Inspect the recent matches and an individual over. Finally, check external availability and squad needs before making a real selection.')
add('The Combined lists are the default research output. An IPL-only ranking is an alternative historical competition view, not a list of people available to buy. The two top-10 lists are not a balanced playing XI, and the same player may qualify in both roles.')

heading('02 / Data and pipeline','A reproducible path from six files')
table([['Input','Purpose'],['ball_by_ball.csv','Runs off the bat, participants, dismissal details, extras categories, innings sequence, phases and pressure evidence.'],['matches.csv','Dates, teams, innings revisions, stage, result and venue metadata.'],['competitions.csv','Distinguish IPL, T20I and excluded competitions.'],['competition_team_player_mapping.csv','Player identity and historical team affiliations.'],['playing_eleven.csv','Cross-check player IDs against match XIs.'],['teams.csv','Preserved and fingerprinted for provenance; displayed labels come from match and player mappings.']],[180,307])
add('Build sequence','SubRR')
add('1. Read the CSVs and join stable match, competition and player IDs.<br/>2. Check delivery keys, source order, over counts and revised-match metadata.<br/>3. Reconstruct wickets and recent wicket falls before each delivery.<br/>4. Retain identifiable legal deliveries and calculate context-adjusted impacts.<br/>5. Aggregate ordinary and pressure evidence separately for each role and scope.<br/>6. Apply sample gates, shrinkage, percentiles and weighted scoring.<br/>7. Re-run alternative assumptions and generate reasons, JSON, CSVs and the report.')
box(f"<b>Coverage:</b> {M['source_rows']:,} supplied delivery rows and {M['source_matches']} match records become {M['legal_balls']:,} retained legal deliveries across {M['analysed_matches']} analysed matches. {M['pressure_balls']:,} deliveries meet the default pressure threshold.")

heading('03 / Data quality','The exclusions are part of the result')
add('The column named extras1_runs behaves as a category code: ordinary deliveries carry 6, wides 2 and byes 4. Summing it as runs would corrupt totals. The undocumented extras_2_runs field is not interpreted as a run amount. Therefore the analysis uses <b>runs off the bat on retained legal deliveries</b>.')
table([['Check / exclusion','Rows or events'],*[[k.replace('_',' '),f'{v:,}'] for k,v in M['audit'].items()]],[365,122])
add('Counters describe different checks and may overlap. Do not add them as a single exclusion total. Quarantined innings and SHA-256 source fingerprints are stored in reports/data_audit.json.','SmallRR')
add('Duplicate keys are removed; an innings is quarantined for a delivery-sequence gap, an invalid over or more than six identifiable legal balls in an over. IPL and T20I are retained; super overs, revised targets/overs and other competitions are excluded. A valid sequence does not prove that a truncated innings is complete.')
add('A striker dismissal is kept separate from a bowler-credit wicket. Non-striker run-outs are not charged to the striker; run-outs are not credited to the bowler. Credited wicket kinds are Caught, Bowled, LBW, Stump and Hit Wicket. Source non-playing dismissal labels are excluded from striker dismissals.','SmallRR')

heading('04 / Pressure definition','Before the ball. Never after it.')
table([['Signal known before the delivery','Pressure points'],['Overs 1-6 / 7-15 / 16-18 / 19-20','10 / 20 / 60 / 75'],['At least 3 wickets lost by over 10','+30'],['Otherwise, at least 4 wickets lost in overs 11-15','+20'],['At least 2 wickets in the previous 12 legal balls','+20'],['Final, Semi Final, Qualifier or Eliminator','+10']],[365,122])
box('<b>High pressure = score &gt;= 55.</b> Scores are capped at 100. Current-ball runs and wickets do not enter that delivery\'s score; wicket state changes only for the next delivery.')
add('Worked situations','SubRR')
add('<b>Over 5, no collapse:</b> 10 points; ordinary context.<br/><b>Over 5, three wickets lost and two recent wickets:</b> 10 + 30 + 20 = 60; pressure.<br/><b>Over 16 with no recent wickets:</b> 60; pressure.<br/><b>Over 20 in a knockout with two recent wickets:</b> 75 + 20 + 10 = 105, capped at 100.')
add('Why these inputs?','SubRR')
add('They can be reconstructed from this pack without inventing chase targets. Death overs represent finishing passages; wicket losses identify collapses; knockout stages add context. These are transparent modelling choices rather than learned coefficients.')
add('This is not psychological pressure, win probability or exact chase difficulty. A one-sided death over still qualifies. A batting collapse can make bowling easier, so pressure does not imply equal difficulty for both roles. The dashboard keeps these limitations visible.')

heading('05 / Context adjustment','Compare like with like')
add('Each delivery is compared with historical peers sharing competition (IPL/T20I), innings and phase (powerplay 1-6, middle 7-15, death 16-20). Where enough data exists, peers also match year and role: batting position group or pace/spin bowling type.')
table([['Fallback level','Context key'],['Most specific','Competition + phase + innings + year + role group'],['Broader','Competition + phase + innings + role group'],['Broadest','Competition + phase + innings']],[115,372])
add('Use the first group with at least 200 legal balls. If none reaches 200, use the broadest available group. Expected runs and wicket probability come from that group. Batting positions are top order (1-3), middle order (4-7) and lower order (8+).')
box('<b>Batting impact</b> = 0.65 x (runs - expected runs) / run SD<br/>+ 0.35 x (expected dismissal probability - striker dismissal) / wicket SD<br/><br/><b>Bowling impact</b> = 0.65 x (expected runs - runs) / run SD<br/>+ 0.35 x (credited wicket - expected wicket probability) / wicket SD')
add('Runs and wickets are standardized because their natural scales differ. Run SD has a floor of 0.5; wicket SD has a floor of 0.1, avoiding unstable division by tiny variances. A positive value means better than the historical context average.')
add('The 65/35 split is a documented modelling choice. These expectations are calculated from the full retained sample, including the assessed player; this is descriptive comparison, not a held-out forecasting model. Opponent quality, pitch, dew, venue effects and exact chase targets are not explicitly adjusted.','SmallRR')

heading('06 / Ranking logic','How the top 10 are selected')
add('First require at least <b>60 pressure balls, 60 ordinary balls, and eight pressure matches with six or more pressure balls each</b>. Apply these gates separately within each role and scope. Excluded players remain explainable in the eligibility explorer.')
table([['Component','Calculation before percentile conversion'],['Pressure performance (50%)','Mean pressure impact x pressure balls / (pressure balls + 60).'],['Baseline uplift (30%)','(Mean pressure impact - ordinary impact) x effective sample / (effective sample + 60). Effective sample = P x N / (P + N).'],['Repeatability (20%)','(Above-context qualifying pressure matches + 2) / (qualifying pressure matches + 4). Above-context means total match pressure impact > 0.']],[145,342])
add('Convert each component to a mid-rank percentile among eligible players in that role and scope: <b>100 x (number below + 0.5 x number equal) / population</b>. Ties get identical component percentiles.')
box('<b>Rating = 50% performance percentile + 30% uplift percentile + 20% repeatability percentile.</b><br/>Sort descending by rating, then pressure balls; player ID is the final deterministic tie-break. Take the first 10.')
r=D['rankings']['Combined']['batters'][0];c=r['components']
add(f"Worked example: {safe(r['name'])}",'SubRR')
add(f"0.50 x {c['quality']:.2f} + 0.30 x {c['uplift']:.2f} + 0.20 x {c['consistency']:.2f} = <b>{r['score']:.2f}</b> (rounding shown). This is a relative rating, not a {r['score']:.0f}% chance of success.")

heading('07 / Player metrics','Recent form and situation-specific evidence')
table([['Metric','Definition and reading'],['Sample batting average','Retained legal-ball bat runs / retained striker dismissals. Not official career batting average; non-striker run-outs and excluded deliveries are outside this denominator.'],['Legal-ball batting SR','100 x retained bat runs / retained legal balls. No-balls are excluded, so this is not official strike rate.'],['Sample bowling average','Retained bat runs conceded / credited wickets. Extras excluded; not official bowling average.'],['Bowling strike rate','Retained legal balls / credited wickets.'],['Bat runs per six balls','6 x retained bat runs / legal balls. Not official economy.'],['Zero denominator','Show a dash, not zero or infinity. Absence of evidence is not poor performance.']],[145,342])
add('Pressure situation cards','SubRR')
add('All cards use deliveries already above the pressure threshold. Death overs are 16-20. Wicket-loss situations meet the early/middle collapse conditions. Two recent wickets uses the same rolling 12-legal-ball signal. Knockouts use the listed stage labels. Buckets overlap and cannot be summed. Below 30 balls, the card adds a small-sample cue; this is a display heuristic, not a new selection gate.')
add('Recent matches','SubRR')
add('The latest eight retained appearances in the chosen role and scope are ordered by match date, then match ID. They include matches with no pressure sample. A situation selector changes the per-match pressure evidence while retaining the same recent match list. Full-match sample outcomes and situation-only rates are kept separate. No future matches or live updates are implied.')

heading('08 / Robustness','Would the shortlist survive other assumptions?')
table([['Alternative','What changes'],['Stricter pressure','Threshold rises from 55 to 65; recheck eligibility and rank.'],['Broader pressure','Threshold falls to 50; recheck eligibility and rank.'],['Best match removed','Remove the match with the greatest total pressure impact for each player, then recheck eligibility. Ordinary evidence is unchanged.'],['Performance emphasis','Component weights become 60% / 20% / 20%.'],['Uplift emphasis','Component weights become 40% / 40% / 20%.']],[160,327])
add('The displayed rank range includes the default and all eligible alternative ranks. An asterisk indicates ineligibility in at least one alternative. Missing ranks are not silently assigned a worst position. This range is a sensitivity check, <b>not a confidence interval</b>; peer populations can change between scenarios.')
add('Interpretation limits','SubRR')
add('A high score in a small eligible sample can outrank a famous high-volume player. Review ball counts, peer comparisons, repeatability and sensitivity before treating it as a recruitment recommendation. Role mix is imperfectly adjusted. The model makes no causal claim that pressure improves a player, and does not estimate future form.')
box('Nationality, photographs, fame and IPL availability contribute <b>zero weight</b> to the performance rating. The profile upgrade left every ranking unchanged.')

heading('09 / Dashboard','A professional selection workspace')
screenshot(ROOT/'docs/ui-dark.jpg')
add('RR-inspired pink and navy, Montserrat typography, a persistent navigation rail, clear metric cards and an evidence panel keep the selection task central. Light and dark modes apply to panels, charts and reports. The saved theme follows the device preference until the user chooses a mode.','SmallRR')
add('Ranking controls','SubRR')
add('Switch batters/bowlers and Combined/IPL/T20I, search all eligible players, preview a selected player, expand the eligible list or export the current scope\'s top 10. Comparison charts show ordinary versus pressure rates and the relationship between rating and evidence volume. Amber Pakistan representation badges request availability review without removing rows.')

heading('10 / Player intelligence','Identity, evidence and availability together')
screenshot(ROOT/'docs/player-lab.jpg')
add('The player header includes a portrait, country or international representation, playing style, a dated IPL roster reference when verified, last appearance in the selected sample, and source links. Teams found in historical mappings are expandable and are not presented as current contracts.','SmallRR')
add(f"Coverage: {len(P['players'])} externally sourced profiles with portrait URLs, including all 20 Combined shortlist players. Other players show initials and explicit unverified fields. Portraits load from publishers online; a failed image falls back to initials. Roster references are snapshots, not a guaranteed current contract or fitness assessment.")
add('Pakistan participation flag','SubRR')
add('The flag is triggered by Pakistan international-team representation in the supplied mapping, not by names, religion, ancestry or birthplace. Pakistan players remain ranked. IPL participation has been restricted in practice, but passport exceptions exist; actual registration, board clearance and eligibility require an individual check. The UI links to sourced reporting and does not call every such player permanently banned.')

def shortlist(role):
 heading('11 / Selection output' if role=='batters' else '13 / Selection output',f'Top 10 {role}', 'Combined IPL + T20I research ranking; availability is a separate decision.')
 rows=[['#','Player','Rating','P. balls','P. matches','Range']]
 for r in D['rankings']['Combined'][role][:10]:rows.append([r['rank'],r['name'],f"{r['score']:.2f}",r['pressure']['balls'],r['pressure_matches'],f"{r['sensitivity'][0]}-{r['sensitivity'][1]}"+('*' if r['sensitivity_missing'] else '')])
 table(rows,[35,164,63,67,75,83])
 add('* Ineligible in one or more alternatives. All rows satisfy the default evidence gates. The range is not a confidence interval.','SmallRR')
 if role=='bowlers':add('Mohammad Nawaz, Sufiyan Muqeem, Shadab Khan and Abrar Ahmed have Pakistan representation in the supplied pack and are marked for individual IPL availability review. Their performance scores are unchanged.')
 add('Why these names?','SubRR')
 add('The shortlist is generated from the same JSON data as the dashboard and CSV export. The following pages explain each player using measured pressure performance, wicket or dismissal evidence, uplift against their own baseline and consistency across qualifying matches. No selection is based on reputation alone.')
def cases(role):
 for start in (0,5):
  heading('12 / Selection reasons' if role=='batters' else '14 / Selection reasons',f'{role.title()}: positions {start+1}-{start+5}')
  for r in D['rankings']['Combined'][role][start:start+5]:
   title=f"{r['rank']:02d}  {safe(r['name'])}  |  Rating {r['score']:.2f}"
   body=' '.join(safe(x) for x in r['reasons'])
   note=f"Sample: {r['pressure']['balls']} pressure balls; {r['pressure_matches']} qualifying matches. Alternative rank range {r['sensitivity'][0]}-{r['sensitivity'][1]}; ineligible in {r['sensitivity_missing']}/5 alternatives."
   if 'Pakistan' in r['teams']:note+=' Pakistan representation: review IPL availability separately.'
   story.append(KeepTogether([para(title,'SubRR'),para(body,'CardRR'),para(note,'SmallRR'),Spacer(1,7)]))
shortlist('batters');cases('batters');shortlist('bowlers');cases('bowlers')

heading('15 / Engineering','Run, reproduce and verify')
table([['File / area','Responsibility'],['app.py','Local HTTP server; run py app.py from the project directory.'],['analysis/build.py','Standard-library CSV cleaning, context model, rankings, audits and exports.'],['analysis/player_details.py','Overall sample metrics, latest eight role appearances and overlapping situation aggregates.'],['analysis/enrich_profiles.py','Public official IPL roster/profile refresh with cached HTML and explicit source URLs.'],['analysis/international_profiles.py','Verified ICC and Cricbuzz references for shortlist players outside the IPL feed.'],['web/app.js + player-lab.js','Rendering, routing, filters, selected-player state and profile/evidence UI.'],['web/styles.css + royals.css + player-lab.css','Layout, responsive UI, theme palettes and player-intelligence styling.'],['web/data/','dashboard.json, player_details.json, profiles.json and individual match evidence files.'],['tests/','Cricket rules, context/ranking boundaries, output checks and chronological/situation metric tests.']],[190,297])
add('Commands','SubRR')
add('<font face="Courier">py app.py<br/>py -m analysis.build --data-dir data/raw<br/>py -m unittest discover -s tests<br/>py -m analysis.enrich_profiles<br/>py -m analysis.international_profiles</font>','SmallRR')
add('The app and analysis use the Python standard library and plain browser JavaScript. Profile refresh needs internet; analysis does not. PDF regeneration additionally requires ReportLab and runs docs/build_project_guide.py. Do not commit temporary scraped HTML caches or redistribute third-party portraits as if they were owned assets.','SmallRR')

heading('16 / Verification and sources','What is verified, and what remains open')
add('Checks performed','SubRR')
add('17 automated analysis tests pass, including new chronology, zero-denominator, role/scope isolation and overlapping-situation checks. Every ranking was compared against the prior version and is identical. JavaScript syntax checks passed. Browser checks covered portrait loading, selecting a player and opening the lab, country/availability flags, recent situation changes, and responsive dark/light layouts. The PDF was rendered for visual inspection.')
add('Source responsibilities','SubRR')
table([['Source','Used for'],['User-supplied six CSVs','All model inputs, historical scores, recent matches and pressure evidence. Source fingerprints are in reports/data_audit.json.'],['iplt20.com player profiles','139 official IPL profile snapshots: nationality, role, portrait references and displayed franchise. Checked 11 November 2026.'],['icc-cricket.com player profiles','Eight international profiles: portraits and dated appearance-year evidence. Checked 11 November 2026.'],['Cricbuzz profile','Abrar Ahmed portrait and profile reference. No external career stats are mixed into model rates.'],['Cricbuzz participation reporting','Pakistan IPL participation context and passport exceptions; no claim of an unconditional permanent prohibition.']],[155,332])
add('Primary entry points and policy context','SubRR')
for url,label in [('https://www.iplt20.com/teams','Official IPL teams and linked player profiles'),('https://www.icc-cricket.com/rankings/57935/mohammad-nawaz','Example ICC profile and appearance-year evidence'),('https://www.cricbuzz.com/cricket-news/140773/mohammad-amir-rules-out-entering-ipl-auction','IPL registration context, Mohammad Amir and passport exceptions'),('https://www.rajasthanroyals.com/','UI inspiration: official Rajasthan Royals website')]:add(f'<a href="{url}" color="#c91d7e">{label}</a>','SmallRR')
add('Each sourced player card links to its exact profile. The complete machine-readable source manifest is web/data/profiles.json; it records source URL, publisher label and check date. External facts can change after that date.','SmallRR')
add('Before real-world use','SubRR')
add('Add a licensed, regularly updated scorecard and roster feed; validate team totals and official averages; include venue/opposition and chase context; test on future held-out matches; and add human scouting, injury/fitness confirmation, price and squad-composition checks. These are future improvements, not capabilities claimed by this version.','SmallRR')

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=54,bottomMargin=62,title='SupeRR Selector - Project and Selection Guide',author='SupeRR Selector Project')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
