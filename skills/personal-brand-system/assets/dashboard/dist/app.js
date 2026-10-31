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

// Font Awesome Free 6.7.2 icons, CC BY 4.0; attribution/license in assets/dashboard/icons/LICENSE.txt.
const channelIcons={"linkedin": "<svg class=\"channel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 448 512\" aria-hidden=\"true\" focusable=\"false\"><path fill=\"currentColor\" d=\"M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z\"/></svg>", "youtube": "<svg class=\"channel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 576 512\" aria-hidden=\"true\" focusable=\"false\"><path fill=\"currentColor\" d=\"M549.655 124.083c-6.281-23.65-24.787-42.276-48.284-48.597C458.781 64 288 64 288 64S117.22 64 74.629 75.486c-23.497 6.322-42.003 24.947-48.284 48.597-11.412 42.867-11.412 132.305-11.412 132.305s0 89.438 11.412 132.305c6.281 23.65 24.787 41.5 48.284 47.821C117.22 448 288 448 288 448s170.78 0 213.371-11.486c23.497-6.321 42.003-24.171 48.284-47.821 11.412-42.867 11.412-132.305 11.412-132.305s0-89.438-11.412-132.305zm-317.51 213.508V175.185l142.739 81.205-142.739 81.201z\"/></svg>", "globe": "<svg class=\"channel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 512 512\" aria-hidden=\"true\" focusable=\"false\"><path fill=\"currentColor\" d=\"M352 256c0 22.2-1.2 43.6-3.3 64l-185.3 0c-2.2-20.4-3.3-41.8-3.3-64s1.2-43.6 3.3-64l185.3 0c2.2 20.4 3.3 41.8 3.3 64zm28.8-64l123.1 0c5.3 20.5 8.1 41.9 8.1 64s-2.8 43.5-8.1 64l-123.1 0c2.1-20.6 3.2-42 3.2-64s-1.1-43.4-3.2-64zm112.6-32l-116.7 0c-10-63.9-29.8-117.4-55.3-151.6c78.3 20.7 142 77.5 171.9 151.6zm-149.1 0l-176.6 0c6.1-36.4 15.5-68.6 27-94.7c10.5-23.6 22.2-40.7 33.5-51.5C239.4 3.2 248.7 0 256 0s16.6 3.2 27.8 13.8c11.3 10.8 23 27.9 33.5 51.5c11.6 26 20.9 58.2 27 94.7zm-209 0L18.6 160C48.6 85.9 112.2 29.1 190.6 8.4C165.1 42.6 145.3 96.1 135.3 160zM8.1 192l123.1 0c-2.1 20.6-3.2 42-3.2 64s1.1 43.4 3.2 64L8.1 320C2.8 299.5 0 278.1 0 256s2.8-43.5 8.1-64zM194.7 446.6c-11.6-26-20.9-58.2-27-94.6l176.6 0c-6.1 36.4-15.5 68.6-27 94.6c-10.5 23.6-22.2 40.7-33.5 51.5C272.6 508.8 263.3 512 256 512s-16.6-3.2-27.8-13.8c-11.3-10.8-23-27.9-33.5-51.5zM135.3 352c10 63.9 29.8 117.4 55.3 151.6C112.2 482.9 48.6 426.1 18.6 352l116.7 0zm358.1 0c-30 74.1-93.6 130.9-171.9 151.6c25.5-34.2 45.2-87.7 55.3-151.6l116.7 0z\"/></svg>"};
function channelIcon(url){const host=new URL(url).hostname.toLowerCase();const name=host==="linkedin.com"||host.endsWith(".linkedin.com")?"linkedin":host==="youtube.com"||host.endsWith(".youtube.com")||host==="youtu.be"?"youtube":"globe";return channelIcons[name]}
const channels=(D.channels||[]).filter(c=>{try{const u=new URL(c.url);return ["https:","http:"].includes(u.protocol)&&!u.username&&!u.password}catch{return false}});
$("#channelLinks").innerHTML=channels.map(c=>'<a href="'+esc(c.url)+'" target="_blank" rel="noopener noreferrer">'+channelIcon(c.url)+'<span>'+esc(c.label)+'</span>'+' <span aria-hidden="true">↗</span></a>').join("");
$("#channelLinks").hidden=!channels.length;
const P=D.presentation;
document.title=P.initials+" · Personal Brand";
$(".brand-mark").textContent=P.initials.toLowerCase()+".";
$(".avatar").textContent=P.initials;
$("#leaderRole").textContent=P.role;
$("#purposeText").textContent=P.purpose;
const approvedTenets=P.tenets||[];
$("#overviewTenetsList").innerHTML=approvedTenets.map(t=>"<li>"+esc(t)+"</li>").join("");
$("#overviewTenets").hidden=!approvedTenets.length;
const foundationComplete=D.state.items.length>0&&D.state.items.every(item=>["resolved","not applicable"].includes(item.state));
if(foundationComplete){const b=document.querySelector(".progress-panel .panel-top .badge");b.textContent="Foundation complete";b.classList.remove("review");b.classList.add("accepted")}
$("#readinessTitle").textContent=P.ready?"Ready to put to work":"Ready to begin";
$("#readinessDescription").textContent=foundationComplete?"Your initial foundation is complete. Keep growing it through use and feedback.":P.ready?"Accepted knowledge and assets are available for reuse. Initial onboarding remains open.":"Your knowledge and assets will grow as you work. Start with what matters to you.";
$("#profileButton").dataset.doc=P.profile||"references/leader-welcome.md";
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

function localKey(target,base){
 try{const u=new URL(target,"https://local/"+base);if(u.origin!=="https://local")return null;return decodeURIComponent(u.pathname.slice(1))}catch{return null}
}
function resolveDoc(target,base){const key=localKey(target,base);return key&&D.docs[key]?key:null}
function fileHref(key){return (D.sourcePrefix||"../../../")+key.split("/").map(encodeURIComponent).join("/")}
function inline(raw,base){
 const tokens=[];
 raw=String(raw).replace(/(!?)\[([^\]]*)\]\(([^)]+)\)/g,(_,image,label,url)=>{
  const key=localKey(url,base),file=key&&(D.files||{})[key];let link;
  if(image&&file&&file.preview)link='<img class="asset-preview" src="'+esc(file.preview)+'" alt="'+esc(label)+'">';
  else if(key&&D.docs[key])link='<a href="#" data-doc="'+esc(key)+'">'+esc(label)+'</a>';
  else if(file)link='<a href="'+esc(fileHref(key))+'" target="_blank" rel="noopener">'+esc(label)+' ↗</a>';
  else if(/^https?:\/\//i.test(url)&&!image)link='<a href="'+esc(url)+'" target="_blank" rel="noopener">'+esc(label)+' ↗</a>';
  else link=esc(label);
  const token="PBSTOKEN"+tokens.length+"END";tokens.push(link);return token;
 });
 let out=esc(raw).replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/`([^`]+)`/g,"<code>$1</code>");
 tokens.forEach((v,i)=>{out=out.replace("PBSTOKEN"+i+"END",v)});return out;
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
const updateDialog=$("#updateViewDialog");
$("#updateViewButton").addEventListener("click",()=>{ $("#updateCopyFeedback").textContent="";updateDialog.showModal() });
$("#closeUpdateView").addEventListener("click",()=>{updateDialog.close();$("#updateViewButton").focus()});
updateDialog.addEventListener("click",e=>{if(e.target===updateDialog){updateDialog.close();$("#updateViewButton").focus()}});
$("#copyUpdateRequest").addEventListener("click",async()=>{const request=$("#updateViewRequest");try{await navigator.clipboard.writeText(request.value);$("#updateCopyFeedback").textContent="Copied. Paste this into your AI conversation."}catch{request.focus();request.select();$("#updateCopyFeedback").textContent="Request selected. Copy it and paste into your AI conversation."}});
$("#openUpdateHelp").addEventListener("click",()=>{updateDialog.close();showDoc("references/dashboard-guide.md")});
$("#reloadSnapshot").addEventListener("click",()=>window.location.reload());
$("#refreshInfo").addEventListener("click",()=>showDoc("references/dashboard-guide.md"));
// Views stay in one offline file; hash navigation supports deep links and Back.
const sections=[...document.querySelectorAll("main>.section")];
function showView(focus=false){
 if(location.hash==="#main")return;
 const requested=location.hash.slice(1),id=sections.some(s=>s.id===requested)?requested:"overview";
 sections.forEach(s=>{s.hidden=s.id!==id;s.classList.toggle("is-active",s.id===id)});
 document.querySelectorAll(".nav-link").forEach(a=>{const active=a.getAttribute("href")==="#"+id;a.classList.toggle("active",active);if(active)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current")});
 if(focus){const heading=document.querySelector("#"+id+" h1, #"+id+" h2");heading.setAttribute("tabindex","-1");heading.focus({preventScroll:true});window.scrollTo(0,0)}
}
window.addEventListener("hashchange",()=>showView(true));showView();
const knowledgeDocs=[["references/personal-brand-kb.md","Your brand knowledge","Your goals, story, contribution and preferences."],["references/voice-style-guide.md","Your voice guide","Accepted examples and guidance for work that sounds like you."],["references/visual-style-guide.md","Your visual style","Saved typography, colors and visual choices."]].filter(([path])=>D.docs[path]);
$("#knowledgeGrid").innerHTML=knowledgeDocs.map(([path,title,description])=>'<article class="component-card" role="button" tabindex="0" data-doc="'+esc(path)+'"><h3>'+esc(title)+'</h3><p>'+esc(description)+'</p><div class="card-bottom"><span>Open saved knowledge</span><span aria-hidden="true">↗</span></div></article>').join("");
let fuelFilter="all";
const fuelLabels={ready:"Ready to explore",active:"In progress",usable:"Ready to use",revisit:"Revisit"};
function fuel(){
 const visible=(D.fuel||[]).filter(f=>fuelFilter==="all"||fuelFilter===f.status||fuelFilter==="focus"&&["active","revisit"].includes(f.status));
 $("#fuelGrid").innerHTML=visible.map(f=>'<article class="component-card fuel-card fuel-'+esc(f.status)+'" role="button" tabindex="0" data-doc="'+esc(f.doc)+'" aria-label="Explore '+esc(f.title)+' — '+esc(fuelLabels[f.status])+'"><div class="card-top"><span class="eyebrow">FUEL</span><span class="badge fuel-status '+esc(f.status)+'">'+(f.status==="usable"?'<span aria-hidden="true">✓ </span>':"")+esc(fuelLabels[f.status])+'</span></div><h3>'+esc(f.title)+'</h3><p>'+esc(f.description)+'</p><div class="card-bottom"><small>'+esc(f.effort)+'</small><span class="card-link" aria-hidden="true">↗</span></div></article>').join("");
 $("#fuelEmpty").hidden=visible.length>0;
}
filters("#fuelFilters",v=>fuelFilter=v,fuel);fuel();
components();assets();
})();
