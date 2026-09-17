const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const root = __dirname;
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const ink = '#202D40';
let objects = [];
function add(o) { objects.push(o); }
function p(id,d,fill='none',stroke=ink,strokeWidth=1,extra={}) { add({id,kind:'path',d,fill,stroke,strokeWidth,...extra}); }
function rect(id,x,y,w,h,fill,rx=0,extra={}) { add({id,kind:'rect',x,y,w,h,fill,rx,stroke:'none',strokeWidth:0,...extra}); }
function ellipse(id,x,y,w,h,fill,stroke=ink,strokeWidth=1,extra={}) { add({id,kind:'ellipse',x,y,w,h,fill,stroke,strokeWidth,...extra}); }
function t(id,x,y,w,h,text,fontSize=20,extra={}) { add({id,kind:'text',x,y,w,h,text,fontSize,fontFamily:'Arial',color:ink,align:'center',...extra}); }

rect('formula_background',190,28,457,80,'#F7F7F9',11,{stroke:'#EBEBF0',strokeWidth:0.7,gradient:'#F2F2F6',group:'formula'});
t('holevo_chi',219,44,128,42,'χ(E) = S(',29,{fontFamily:'Times New Roman',italic:true,align:'left',group:'formula'});
t('first_sum',345,40,43,53,'∑',40,{fontFamily:'Cambria Math',group:'formula'});
t('first_sum_index',358,85,19,18,'l',18,{fontFamily:'Times New Roman',italic:true,group:'formula'});
t('ensemble_term',388,45,65,40,'',29,{fontFamily:'Times New Roman',italic:true,align:'left',runs:[{text:'p'},{text:'l',sub:true},{text:' ρ'},{text:'l',sub:true}],group:'formula'});
t('entropy_close',445,45,15,40,')',29,{fontFamily:'Times New Roman',group:'formula'});
t('holevo_minus',462,45,22,40,'−',29,{fontFamily:'Times New Roman',group:'formula'});
t('second_sum',485,40,43,53,'∑',40,{fontFamily:'Cambria Math',group:'formula'});
t('second_sum_index',499,85,19,18,'l',18,{fontFamily:'Times New Roman',italic:true,group:'formula'});
t('entropy_average',529,45,100,40,'',29,{fontFamily:'Times New Roman',italic:true,align:'left',runs:[{text:'p'},{text:'l',sub:true},{text:' S(ρ'},{text:'l',sub:true},{text:')'}],group:'formula'});

// Communication links and arrowheads are separate editable vector objects.
p('alice_input','M 124 253 L 137 253','none','#303C4B',0.9);
p('alice_input_arrow','M 139 253 L 134 250.5 L 135 253 L 134 255.5 Z','#303C4B','none',0);
p('left_classical_link','M 290 252.5 L 355 252.5','none','#253B59',1.5,{dashed:true,dashPattern:'3 3'});
p('right_classical_link','M 485 252.5 L 586 252.5','none','#253B59',1.5,{dashed:true,dashPattern:'3 3'});
p('interception_in','M 295 228 C 320 187 341 170 390 165','none','#243C5D',1.3,{dashed:true,dashPattern:'3 3'});
p('interception_in_tip','M 400 164.5 L 389 160 L 390 170.5 Z','#202D40','none',0);
p('interception_out','M 477 165 C 532 171 546 217 574 229','none','#243C5D',1.3,{dashed:true,dashPattern:'3 3'});
p('interception_out_tip','M 582 231 L 572 224.5 L 571.5 235 Z','#202D40','none',0);

// Bell-state measurement tube, built from vector outlines and ellipses.
p('measurement_soft_shadow','M 159 278 L 272 278 C 282 278 286 282 284 285 L 160 285 C 154 283 154 280 159 278 Z','#26374C','none',0,{opacity:5,group:'measurement'});
p('measurement_cylinder','M 155 221.5 L 276 221.5 C 291 223 291 278 276 281 L 155 281 Z','#F4F7FA','#252E3B',1.15,{gradient:'#BEC7D0',group:'measurement'});
ellipse('measurement_right_cap',264,221.5,23.5,59.5,'#F2F5F8','#28333F',1,{gradient:'#D0D7DF',group:'measurement'});
ellipse('measurement_left_rim',141.5,221.5,28,59.5,'#DCE3EA','#2C3742',1.05,{group:'measurement'});
ellipse('measurement_left_inner_rim',143.5,225,21,53,'#F5F7FA','#43505F',0.8,{group:'measurement'});
ellipse('measurement_aperture',146.5,231.5,12.5,41.5,'#253345','none',0,{group:'measurement'});
p('measurement_rim_glint','M 154 227 C 160 238 161 260 156 274','none','#FFFFFF',1.1,{group:'measurement'});

// Pauli correction capsule.
p('correction_shadow','M 605 278 L 710 278 C 719 278 722 282 718 285 L 603 285 Z','#26374C','none',0,{opacity:5,group:'correction'});
p('correction_capsule','M 604 221.5 L 708 221.5 C 727 221.5 728 281 708 281 L 604 281 C 585 281 584 221.5 604 221.5 Z','#F4F7FA','#303845',1.1,{gradient:'#BEC7D0',group:'correction'});
t('pauli_operators',600,235,114,33,'I, X, Y, Z',26,{fontFamily:'Times New Roman',italic:true,group:'correction'});

// Quantum channel wave pairs and curved terminal arrows.
p('quantum_left_return','M 161 292 C 166 310 177 312 191 311','none','#354251',0.9);
p('quantum_left_return_arrow','M 202 311 L 192 306.5 L 192 316 Z','#253244','none',0);
p('quantum_right_return','M 698 292 C 694 306 688 311 679 311','none','#354251',0.9);
p('quantum_right_return_arrow','M 671 311 L 683 306.5 L 683 315.5 Z','#253244','none',0);
p('quantum_wave_left_top','M 208 309 C 233 291 252 291 278 305 C 303 321 319 324 340 315','none','#7286A3',1.2);
p('quantum_wave_left_bottom','M 208 309 C 234 327 255 327 281 311 C 306 295 319 291 340 300','none','#8C9EB8',1);
p('quantum_wave_left_upper_fade','M 278 305 C 303 321 319 324 340 315','none','#E1E7F0',1.2);
p('quantum_wave_left_lower_fade','M 281 311 C 306 295 319 291 340 300','none','#C9D4E4',0.8);
p('quantum_wave_right_top','M 528 301 C 549 290 563 296 587 310 C 612 326 636 325 662 309','none','#8698B3',1.1);
p('quantum_wave_right_bottom','M 528 315 C 549 325 563 319 586 306 C 613 291 635 293 662 309','none','#7589A6',1.15);
p('quantum_wave_right_upper_fade','M 528 301 C 545 293 557 295 568 300','none','#D8E0EB',1.1);
p('quantum_wave_right_lower_fade','M 528 315 C 543 322 556 321 568 315','none','#D8E0EB',1.15);
t('measurement_label',150,165,129,47,'Bell State\nMeasurement',20);
t('correction_label',604,164,101,48,'Pauli\nCorrection',20);
t('alice_label',48,296,76,34,'Alice',24);
t('bob_label',728,296,79,34,'Bob',24);
t('quantum_channel_label',342,302,188,33,'Quantum Channel',22);
t('message_m1',361,234,41,38,'',28,{fontFamily:'Times New Roman',italic:true,align:'left',runs:[{text:'M'},{text:'1',sub:true}]});
t('message_m2',440,234,42,38,'',28,{fontFamily:'Times New Roman',italic:true,align:'left',runs:[{text:'M'},{text:'2',sub:true}]});
p('message_arrow','M 403 252 L 423 252','none','#233044',1.4);
p('message_arrow_tip','M 432 252 L 422 247 L 422 257 Z','#233044','none',0);

const people = JSON.parse(fs.readFileSync(path.join(root,'vector_people.json'),'utf8'));
for (const o of people) {
  o.group = o.id.toLowerCase().includes('alice') ? 'alice' : o.id.toLowerCase().includes('bob') ? 'bob' : 'attacker';
  add(o);
}
const charts = JSON.parse(fs.readFileSync(path.join(root,'vector_charts.json'),'utf8'));
for (const o of charts) {
  o.group = ['independent','sequential','burst','correlated'].find(s => o.id.includes(s));
  if(o.kind==='rect') {o.fill='#F8F8FA';o.gradient='#F2F2F5';}
  add(o);
}

function parsePath(d) {
  const tokens=d.match(/[MLCQZ]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?/g);
  const out=[];const counts={M:2,L:2,C:6,Q:4,Z:0};
  for(let i=0;i<tokens.length;) {const cmd=tokens[i++];if(!(cmd in counts))throw new Error('Invalid path command '+cmd);const n=counts[cmd];out.push({cmd,v:tokens.slice(i,i+n).map(Number)});i+=n;}
  return out;
}
function bounds(o) {
  if(o.kind!=='path')return {x:o.x,y:o.y,w:o.w,h:o.h};
  const pts=parsePath(o.d).flatMap(p=>p.v);const xs=pts.filter((_,i)=>i%2===0),ys=pts.filter((_,i)=>i%2===1);
  return {x:Math.min(...xs),y:Math.min(...ys),w:Math.max(1,Math.max(...xs)-Math.min(...xs)),h:Math.max(1,Math.max(...ys)-Math.min(...ys))};
}
const num=n=>Number(n.toFixed(4));
function stencil(o,b) {
  const body=parsePath(o.d).map(p=>{
    const v=p.v.map((n,i)=>num(n-(i%2===0?b.x:b.y)));
    if(p.cmd==='M'||p.cmd==='L')return `<${p.cmd==='M'?'move':'line'} x="${v[0]}" y="${v[1]}"/>`;
    if(p.cmd==='C')return `<curve x1="${v[0]}" y1="${v[1]}" x2="${v[2]}" y2="${v[3]}" x3="${v[4]}" y3="${v[5]}"/>`;
    if(p.cmd==='Q')return `<quad x1="${v[0]}" y1="${v[1]}" x2="${v[2]}" y2="${v[3]}"/>`;
    return '<close/>';
  }).join('');
  const paint=o.fill==='none'?'stroke':o.stroke==='none'?'fill':'fillstroke';
  const xml=`<shape name="${esc(o.id)}" w="${num(b.w)}" h="${num(b.h)}" aspect="variable" strokewidth="inherit"><connections/><background/><foreground><linecap cap="round"/><linejoin join="round"/><path>${body}</path><${paint}/></foreground></shape>`;
  return zlib.deflateRawSync(Buffer.from(encodeURIComponent(xml),'utf8')).toString('base64');
}
function textHtml(o) {
  const content=o.runs?o.runs.map(r=>r.sub?`<sub style="font-size:65%;font-style:${/^\d+$/.test(r.text)?'normal':'italic'}">${esc(r.text)}</sub>`:esc(r.text)).join(''):esc(o.text).replace(/\n/g,'<br>');
  return `<div style="line-height:1.15;white-space:nowrap;${o.italic?'font-style:italic;':''}">${content}</div>`;
}
const groupMap=new Map();
for(const o of objects.filter(o=>o.group)) {
  const b=bounds(o),g=groupMap.get(o.group);
  if(!g)groupMap.set(o.group,{x:b.x,y:b.y,right:b.x+b.w,bottom:b.y+b.h});
  else {g.x=Math.min(g.x,b.x);g.y=Math.min(g.y,b.y);g.right=Math.max(g.right,b.x+b.w);g.bottom=Math.max(g.bottom,b.y+b.h);}
}
let cells=['<mxCell id="0"/>','<mxCell id="1" parent="0"/>'];
const emittedGroups=new Set();
for(const o of objects) {
  if(o.group&&!emittedGroups.has(o.group)) {
    const g=groupMap.get(o.group);
    cells.push(`<mxCell id="group_${o.group}" value="" style="group;" vertex="1" connectable="0" parent="1"><mxGeometry x="${num(g.x)}" y="${num(g.y)}" width="${num(g.right-g.x)}" height="${num(g.bottom-g.y)}" as="geometry"/></mxCell>`);emittedGroups.add(o.group);
  }
  const b=bounds(o),g=o.group?groupMap.get(o.group):{x:0,y:0};
  let style;
  if(o.kind==='text')style=`text;html=1;whiteSpace=wrap;overflow=visible;align=${o.align||'center'};verticalAlign=middle;fillColor=none;strokeColor=none;fontColor=${o.color};fontFamily=${o.fontFamily||'Arial'};fontSize=${o.fontSize};fontStyle=${o.italic?2:0};spacing=0;resizable=1;`;
  else {
    const shape=o.kind==='path'?`stencil(${stencil(o,b)})`:o.kind==='ellipse'?'ellipse':'rectangle';
    style=`shape=${shape};fillColor=${o.fill||'none'};strokeColor=${o.stroke||'none'};strokeWidth=${o.strokeWidth??1};`;
    if(o.rx)style+=`rounded=1;absoluteArcSize=1;arcSize=${o.rx*2};`;
    if(o.gradient)style+=`gradientColor=${o.gradient};gradientDirection=south;`;
    if(o.dashed)style+=`dashed=1;dashPattern=${o.dashPattern||'3 4'};`;
    if(o.opacity!==undefined)style+=`opacity=${o.opacity};`;
  }
  cells.push(`<mxCell id="${esc(o.id)}" value="${o.kind==='text'?esc(textHtml(o)):''}" style="${esc(style)}" vertex="1" parent="${o.group?'group_'+o.group:'1'}"><mxGeometry x="${num(b.x-g.x)}" y="${num(b.y-g.y)}" width="${num(b.w)}" height="${num(b.h)}" as="geometry"/></mxCell>`);
}
const mxfile=`<?xml version="1.0" encoding="UTF-8"?>\n<mxfile host="app.diagrams.net" agent="Editable vector reconstruction" version="29.0.0"><diagram id="quantum-channel" name="Quantum Channel"><mxGraphModel dx="832" dy="509" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="832" pageHeight="509" math="0" shadow="0" background="#FCFCFE"><root>${cells.join('\n')}</root></mxGraphModel></diagram></mxfile>`;
fs.writeFileSync(path.join(root,'quantum_channel.drawio'),mxfile);

let defs=[],svg=[];
for(const o of objects) {
  let fill=o.fill||'none';
  if(o.gradient) {const id='gradient_'+o.id;defs.push(`<linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${o.fill}"/><stop offset="1" stop-color="${o.gradient}"/></linearGradient>`);fill=`url(#${id})`;}
  const attrs=`fill="${fill}" stroke="${o.stroke||'none'}" stroke-width="${o.strokeWidth??1}" stroke-linecap="round" stroke-linejoin="round"${o.dashed?` stroke-dasharray="${(o.dashPattern||'3 4').split(' ').map(Number).map(n=>n*(o.strokeWidth||1)).join(' ')}"`:''}${o.opacity!==undefined?` opacity="${o.opacity/100}"`:''}`;
  if(o.kind==='path')svg.push(`<path id="${o.id}" d="${o.d}" ${attrs}/>`);
  else if(o.kind==='rect')svg.push(`<rect id="${o.id}" x="${o.x}" y="${o.y}" width="${o.w}" height="${o.h}" rx="${o.rx||0}" ${attrs}/>`);
  else if(o.kind==='ellipse')svg.push(`<ellipse id="${o.id}" cx="${o.x+o.w/2}" cy="${o.y+o.h/2}" rx="${o.w/2}" ry="${o.h/2}" ${attrs}/>`);
  else {
    const xx=o.align==='left'?o.x:o.align==='right'?o.x+o.w:o.x+o.w/2;
    const anchor=o.align==='left'?'start':o.align==='right'?'end':'middle';
    const lines=(o.text||'').split('\n');
    const base=o.y+o.h/2+o.fontSize*.34;
    let textContent=o.runs?o.runs.map(r=>r.sub?`<tspan baseline-shift="sub" font-size="65%" font-style="${/^\d+$/.test(r.text)?'normal':'italic'}">${esc(r.text)}</tspan>`:esc(r.text)).join(''):lines.map((line,i)=>`<tspan x="${xx}" y="${num(base+(i-(lines.length-1)/2)*o.fontSize*1.15)}">${esc(line)}</tspan>`).join('');
    svg.push(`<text id="${o.id}" x="${xx}" y="${num(base)}" text-anchor="${anchor}" font-family="${esc(o.fontFamily||'Arial')}" font-size="${o.fontSize}" fill="${o.color}"${o.italic?' font-style="italic"':''}>${textContent}</text>`);
  }
}
const svgText=`<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="832" height="509" viewBox="0 0 832 509" content="${esc(mxfile)}"><title>Quantum channel with Bell state measurement and Pauli correction</title><desc>Editable vector reconstruction. Holevo information, Alice and Bob, intercepted classical communication, quantum channel, and four noise profiles. All figures are vector paths and editable text; no raster images.</desc><defs>${defs.join('')}</defs><rect width="832" height="509" fill="#FCFCFE"/>${svg.join('\n')}</svg>`;
fs.writeFileSync(path.join(root,'quantum_channel.svg'),svgText);
fs.writeFileSync(path.join(root,'components.json'),JSON.stringify(objects,null,2));
console.log(JSON.stringify({objects:objects.length,groups:groupMap.size,drawioBytes:Buffer.byteLength(mxfile),svgBytes:Buffer.byteLength(svgText)}));
