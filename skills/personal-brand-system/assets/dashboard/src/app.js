(() => {
"use strict";
const D=window.PBS_DATA;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let currentDoc="",currentText="",componentFilter="all",assetFilter="current",lastFocus;
const badge=(status,label)=>'<span class="badge '+esc(status)+'">'+esc(label)+'</span>';
$("#leaderName").textContent=D.leader;
$("#crumbName").textContent=D.leader;
$("#snapshotDate").textContent="Snapshot · "+D.date;
$("#sidebarVersion").textContent="Skill v"+D.version;
$("#progressNumber").innerHTML=esc(D.summary.completion_percent)+'<span>%</span>';
$("#progressBar").style.width=D.summary.completion_percent+"%";
$("#resolvedCount").textContent=D.summary.resolved;
$("#remainingCount").textContent=D.summary.remaining;
$("#deferredCount").textContent=D.summary.deferred;
$("#activeTime").textContent=D.summary.active_minutes===null?"Not measured":"≈ "+D.summary.active_minutes+" min";

const P=D.presentation;
document.title=P.initials+" · Personal Brand";
$(".brand-mark").textContent=P.initials.toLowerCase()+".";
$(".avatar").textContent=P.initials;
$("#leaderRole").textContent=P.role;
$("#purposeText").textContent=P.purpose;
$("#readinessTitle").textContent=P.ready?"Ready to put to work":"Ready to begin";
$("#readinessDescription").textContent=P.ready?"Accepted knowledge and assets are available for reuse. Initial onboarding remains open.":"Your knowledge and assets will grow as you work. Start with what matters to you.";
$("#profileButton").dataset.doc=P.profile||"references/kickoff-guide.md";
$("#profileButton").innerHTML=(P.profile?"Read my profile":"Start here")+' <span>↗</span>';
$("#footerBrand").textContent=P.initials+" · Personal Brand";
const milestoneDone=m=>D.state.items.filter(i=>i.id.startsWith(m+".")).every(i=>i.state==="resolved"||i.state==="not applicable");
for(const [id,done,label] of [["identityBadge",milestoneDone("M2"),"Established"],["positioningBadge",milestoneDone("M3"),"Accepted"],["assetsBadge",Boolean(P.profile),"Profile accepted"]]){
 const b=$("#"+id);b.textContent=done?label:"To review";b.className="badge "+(done?"accepted":"review");
}


function metric(c) {
 if(c.metric==="built")return {value:"100%",label:"Initial version built"};
 if(c.metric==="optional")return {value:"Optional",label:"No completion target"};
 const items=D.state.items.filter(i=>c.milestones.includes(i.id.split(".")[0]));
 const groups=[...new Set(items.map(i=>i.id.split(".")[0]))].map(id=>items.filter(i=>i.id.startsWith(id+".")&&i.state!=="not applicable"));
 const active=groups.filter(g=>g.length);
 const value=active.length?Math.round(100*active.reduce((n,g)=>n+g.filter(i=>i.state==="resolved").length/g.length,0)/active.length):0;
 return {value:value+"%",label:c.metricLabel};
}
function components(){
 const q=$("#componentSearch").value.trim().toLowerCase();
 const filtered=D.components.filter(c=>(componentFilter==="all"||componentFilter==="foundation"&&c.foundation||componentFilter==="review"&&c.status==="review"||componentFilter==="optional"&&c.status==="optional")&&[c.title,c.description,c.improve].join(" ").toLowerCase().includes(q));
 $("#componentGrid").innerHTML=filtered.map((c)=>{const m=metric(c);return '<article class="component-card" role="button" tabindex="0" data-component="'+esc(c.id)+'" aria-label="View '+esc(c.title)+'"><div class="card-top"><span class="card-number">'+String(c.number).padStart(2,"0")+'</span>'+badge(c.status==="optional"?"deferred":c.status,c.statusLabel)+'</div><h3>'+esc(c.title)+'</h3><p>'+esc(c.description)+'</p><div class="card-bottom"><div class="metric"><strong>'+esc(m.value)+'</strong><small>'+esc(m.label)+'</small></div><span class="card-link" aria-hidden="true">↗</span></div></article>'}).join("");
 $("#componentEmpty").hidden=filtered.length>0;
}
function assets(){
 const q=$("#assetSearch").value.trim().toLowerCase();
 const filtered=D.assets.filter(a=>(assetFilter==="all"||assetFilter==="current"&&a.status!=="history"||assetFilter===a.status)&&[a.title,a.name,a.category].join(" ").toLowerCase().includes(q));
 $("#assetCount").textContent=filtered.length+" of "+D.assets.length+" files";
 $("#assetList").innerHTML=filtered.map(a=>'<div class="asset-row" role="button" tabindex="0" data-doc="'+esc(a.path)+'" aria-label="Read '+esc(a.title)+'"><span class="asset-icon" aria-hidden="true">▤</span><div><span class="asset-title">'+esc(a.title)+'</span><div class="asset-subtitle">'+esc(a.name)+'</div></div><span class="asset-category">'+esc(a.category)+'</span>'+badge(a.status,a.statusLabel)+'<span class="card-link" aria-hidden="true">↗</span></div>').join("");
 $("#assetList").hidden=filtered.length===0;
 $("#assetEmpty").hidden=filtered.length>0;
}
const open=D.state.items.filter(i=>!["resolved","deferred","not applicable"].includes(i.state));
$("#openCount").textContent=open.length+" items";
$("#openItems").innerHTML=open.map(i=>'<div class="open-item"><span class="open-marker" aria-hidden="true"></span><div><strong>'+esc(i.label)+'</strong><small>'+esc(i.id)+" · "+esc(i.milestone)+" · "+esc(i.state)+(i.evidence?" — "+esc(i.evidence):"")+'</small></div></div>').join("");
$("#deferredWork").innerHTML=D.state.deferred_work.map(s=>"<li>"+esc(s)+"</li>").join("");

function resolveDoc(target,base){
 const u=new URL(target,"https://local/"+base);
 const key=decodeURIComponent(u.pathname.slice(1));
 return D.docs[key]?key:null;
}
function inline(raw,base){
 const tokens=[];
 raw=String(raw).replace(/\[([^\]]+)\]\(([^)]+)\)/g,(_,label,url)=>{
  const key=resolveDoc(url,base);
  let link;
  if(key)link='<a href="#" data-doc="'+esc(key)+'">'+esc(label)+'</a>';
  else if(/^https?:\/\//i.test(url))link='<a href="'+esc(url)+'" target="_blank" rel="noopener">'+esc(label)+' ↗</a>';
  else link=esc(label);
  const token="PBSTOKEN"+tokens.length+"END";tokens.push(link);return token;
 });
 let out=esc(raw).replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/`([^`]+)`/g,"<code>$1</code>");
 tokens.forEach((v,i)=>{out=out.replace("PBSTOKEN"+i+"END",v)});
 return out;
}
function markdown(text,base){
 const lines=text.split(/\r?\n/);let out=[],paragraph=[],list=[],listType="",code=null,table=[];
 const flushP=()=>{if(paragraph.length){out.push("<p>"+inline(paragraph.join(" "),base)+"</p>");paragraph=[]}};
 const flushL=()=>{if(list.length){out.push("<"+listType+">"+list.map(s=>"<li>"+inline(s,base)+"</li>").join("")+"</"+listType+">");list=[];listType=""}};
 const flushT=()=>{if(table.length){const cells=s=>s.trim().replace(/^\||\|$/g,"").split("|").map(s=>inline(s.trim(),base));const rows=table.filter(s=>!/^\s*\|?[\s:|-]+\|?\s*$/.test(s));out.push('<div class="table-wrap"><table>'+rows.map((r,i)=>"<tr>"+cells(r).map(v=>"<"+(i===0?"th":"td")+">"+v+"</"+(i===0?"th":"td")+">").join("")+"</tr>").join("")+"</table></div>");table=[]}};
 for(const line of lines){
 if(line.startsWith("```")){flushP();flushL();flushT();if(code!==null){out.push("<pre><code>"+esc(code.join("\n"))+"</code></pre>");code=null}else code=[];continue}
 if(code!==null){code.push(line);continue}
 if(line.trim().startsWith("|")){flushP();flushL();table.push(line);continue}else flushT();
 const heading=line.match(/^(#{1,6})\s+(.+)$/);const li=line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)$/);
 if(!line.trim()){flushP();flushL();continue}
 if(heading){flushP();flushL();const n=Math.min(heading[1].length,4);out.push("<h"+n+">"+inline(heading[2],base)+"</h"+n+">");continue}
 if(li){flushP();const type=/^\s*\d+\./.test(line)?"ol":"ul";if(listType&&listType!==type)flushL();listType=type;list.push(li[1]);continue}
 if(line.startsWith(">")){flushP();flushL();out.push("<blockquote>"+inline(line.replace(/^>\s?/,""),base)+"</blockquote>");continue}
 if(/^---+$/.test(line)){flushP();flushL();out.push("<hr>");continue}
 flushL();paragraph.push(line);
 }
 flushP();flushL();flushT();if(code!==null)out.push("<pre>"+esc(code.join("\n"))+"</pre>");return out.join("");
}
function showDoc(path,component){
 const doc=D.docs[path];if(!doc)return;
 lastFocus=document.activeElement;
 currentDoc=path;currentText=doc.text;
 $("#detailTitle").textContent=component?component.title:doc.title;
 $("#detailType").textContent=component?"SKILL COMPONENT":"KNOWLEDGE & ASSETS";
 const a=D.assets.find(a=>a.path===path);
 $("#detailStatus").textContent=component?component.improve:(a?a.statusLabel+" · "+a.name+" · Public use requires review":"Local source · "+path);
 $("#detailActions").innerHTML=component?component.docs.filter(p=>D.docs[p]).map((p,i)=>'<button class="secondary" data-doc="'+esc(p)+'">'+esc(i===0?"Main document":D.docs[p].title)+'</button>').join(""):"";
 $("#documentBody").innerHTML=markdown(doc.text,path);
 $("#sourceLink").href=(D.sourcePrefix||"../../../")+path;
 $("#copyFeedback").textContent="";
 const dialog=$("#detailDialog");if(!dialog.open)dialog.showModal();
 dialog.scrollTop=0;
}
function close(){ $("#detailDialog").close();if(lastFocus&&lastFocus.isConnected)lastFocus.focus()}
$("#closeDialog").addEventListener("click",close);
$("#detailDialog").addEventListener("click",e=>{if(e.target===$("#detailDialog"))close()});
$("#copyDocument").addEventListener("click",async()=>{try{await navigator.clipboard.writeText(currentText);$("#copyFeedback").textContent="Copied"}catch{const range=document.createRange();range.selectNodeContents($("#documentBody"));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);$("#copyFeedback").textContent="Text selected. Use Ctrl+C."}});
document.addEventListener("click",e=>{
 const doc=e.target.closest("[data-doc]");if(doc){e.preventDefault();showDoc(doc.dataset.doc);return}
 const c=e.target.closest("[data-component]");if(c){const component=D.components.find(v=>v.id===c.dataset.component);showDoc(component.docs[0],component)}
});
document.addEventListener("keydown",e=>{
 const item=e.target.closest('.component-card[role="button"], .asset-row[role="button"]');
 if(item&&(e.key==="Enter"||e.key===" ")){e.preventDefault();item.click()}
});
function filters(selector,set,render){
 $(selector).addEventListener("click",e=>{const b=e.target.closest("[data-filter]");if(!b)return;$(selector).querySelectorAll("button").forEach(el=>{const active=el===b;el.classList.toggle("active",active);el.setAttribute("aria-pressed",String(active))});set(b.dataset.filter);render()});
}
filters("#componentFilters",v=>componentFilter=v,components);filters("#assetFilters",v=>assetFilter=v,assets);
$("#componentSearch").addEventListener("input",components);$("#assetSearch").addEventListener("input",assets);
$("#refreshInfo").addEventListener("click",()=>showDoc("references/dashboard-guide.md"));
const observer=new IntersectionObserver(entries=>{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];if(visible)document.querySelectorAll(".nav-link").forEach(a=>a.classList.toggle("active",a.getAttribute("href")==="#"+visible.target.id))},{rootMargin:"-10% 0px -55% 0px",threshold:0});
document.querySelectorAll("main>.section").forEach(s=>observer.observe(s));
let fuelFilter="all";
const fuelLabels={ready:"Ready to explore",active:"In progress",usable:"Ready to use",revisit:"Revisit"};
function fuel(){
 const visible=(D.fuel||[]).filter(f=>fuelFilter==="all"||fuelFilter===f.status||fuelFilter==="focus"&&["active","revisit"].includes(f.status));
 $("#fuelGrid").innerHTML=visible.map(f=>'<article class="component-card fuel-card fuel-'+esc(f.status)+'" role="button" tabindex="0" data-doc="'+esc(f.doc)+'" aria-label="Explore '+esc(f.title)+' — '+esc(fuelLabels[f.status])+'"><div class="card-top"><span class="eyebrow">FUEL</span><span class="badge fuel-status '+esc(f.status)+'">'+esc(fuelLabels[f.status])+'</span></div><h3>'+esc(f.title)+'</h3><p>'+esc(f.description)+'</p><div class="card-bottom"><small>'+esc(f.effort)+'</small><span class="card-link" aria-hidden="true">↗</span></div></article>').join("");
 $("#fuelEmpty").hidden=visible.length>0;
}
filters("#fuelFilters",v=>fuelFilter=v,fuel);fuel();
components();assets();
})();
