'use strict';
// Small, safe renderer for our generated report. Raw HTML is always escaped.
const escapeHTML=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const inline=s=>escapeHTML(s).replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/`([^`]+)`/g,'<code>$1</code>');
function markdown(text){
  const lines=text.split('\n');let out='',list=false;
  for(let i=0;i<lines.length;i++){
    const line=lines[i].trim();
    if(!line){if(list){out+='</ul>';list=false;}continue;}
    if(line.startsWith('|')){
      if(list){out+='</ul>';list=false;}
      const cells=s=>s.split('|').slice(1,-1).map(c=>c.trim());
      out+='<div class="table-wrap"><table><thead><tr>'+cells(line).map(c=>`<th>${inline(c)}</th>`).join('')+'</tr></thead><tbody>';
      i++;while(i+1<lines.length&&lines[i+1].trim().startsWith('|')){i++;out+='<tr>'+cells(lines[i]).map(c=>`<td>${inline(c)}</td>`).join('')+'</tr>';}
      out+='</tbody></table></div>';continue;
    }
    const heading=line.match(/^(#{1,4})\s+(.+)$/);
    if(heading){if(list){out+='</ul>';list=false;}out+=`<h${heading[1].length}>${inline(heading[2])}</h${heading[1].length}>`;continue;}
    if(line.startsWith('- ')||/^\d+\. /.test(line)){if(!list){out+='<ul>';list=true;}out+=`<li>${inline(line.replace(/^(- |\d+\. )/,''))}</li>`;continue;}
    if(list){out+='</ul>';list=false;}out+=`<p>${inline(line)}</p>`;
  }
  return out+(list?'</ul>':'');
}
document.getElementById('print-report').addEventListener('click',()=>window.print());
fetch('data/METHODOLOGY.md').then(r=>{if(!r.ok)throw new Error('Report not found');return r.text();}).then(text=>{document.getElementById('report').innerHTML=markdown(text);}).catch(error=>{document.getElementById('report').textContent='Unable to load report. Start python app.py and rebuild data if necessary. '+error.message;});
