const fs = require('fs');
const path = require('path');
const xml = require('C:/Users/DELL/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/xml-js');
const root = __dirname;
const out = 'quantum_channel_matched';
function serializeSafe(value, options) {
  const data=structuredClone(value);
  function walk(node) {
    if(!node||typeof node!=='object')return;
    for(const [key,val] of Object.entries(node)) {
      if(key==='_attributes'||key==='attributes') {
        for(const name of Object.keys(val))val[name]=String(val[name]).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      } else walk(val);
    }
  }
  walk(data);
  return xml.js2xml(data,options);
}
const palette = {
  purpleLight:'#715DA6', purpleDark:'#342E63', purpleRim:'#5F5190',
  blueLight:'#418DC8', blueDark:'#2970AB', greenLight:'#2DA962', greenDark:'#218C5A',
  cyan:'#46BFDB', channelBlue:'#09478B', skin:'#DFAC8B', hair:'#313635',
  formula:'#E5EAEE', formulaBorder:'#939392', lavender:'#EAE5F2',
  outline:'#3E3B3D', text:'#111111', threat:'#93272C'
};
const changes = new Map();
const set = (id, attrs) => changes.set(id, {...changes.get(id),...attrs});
const source = fs.readFileSync(path.join(root,'quantum_channel.drawio'),'utf8');
const doc = xml.xml2js(source,{compact:true});
const model = doc.mxfile.diagram.mxGraphModel;
const cells = model.root.mxCell;
for(const cell of cells) {
  const a = cell._attributes, id=a.id;
  if(a.value) set(id,{fontColor:palette.text});
  if(id.startsWith('chart_panel_')) set(id,{fillColor:palette.lavender,gradientColor:null,strokeColor:'#A49FAA',strokeWidth:1});
  if(id.startsWith('chart_axes_')) set(id,{strokeColor:'#203A50',strokeWidth:1.15});
  if(id.startsWith('chart_axis_tip_')) set(id,{fillColor:'#203A50'});
  if(id.startsWith('chart_curve_')) set(id,{strokeColor:'#4C3B76',strokeWidth:1.4});
  if(id.startsWith('quantum_wave_')) set(id,{strokeColor:id.includes('fade')?'#93DCEC':id.includes('top')?palette.channelBlue:palette.cyan,strokeWidth:id.includes('fade')?1.6:1.8});
  if(id.startsWith('interception_')) set(id,id.endsWith('_tip')?{fillColor:palette.threat}:{strokeColor:palette.threat,strokeWidth:1.5});
}
set('chart_curve_correlated_dashed',{strokeColor:'#418DC8',strokeWidth:1.05});
set('formula_background',{fillColor:palette.formula,gradientColor:null,strokeColor:palette.formulaBorder,strokeWidth:1.3});
set('measurement_cylinder',{fillColor:palette.purpleLight,gradientColor:palette.purpleDark,strokeColor:'#302445',strokeWidth:1.3});
set('measurement_right_cap',{fillColor:'#A48CCB',gradientColor:'#67518F',strokeColor:'#302445',strokeWidth:1.15});
set('measurement_left_rim',{fillColor:palette.purpleRim,gradientColor:'#3B305D',strokeColor:'#302445',strokeWidth:1.3});
set('measurement_left_inner_rim',{fillColor:'#AD9DD0',gradientColor:'#78629D',strokeColor:'#302445',strokeWidth:1.1});
set('measurement_aperture',{fillColor:'#28203F'});
set('measurement_rim_glint',{strokeColor:'#DCD2ED',strokeWidth:1.2});
set('measurement_soft_shadow',{fillColor:'#514164',opacity:8});
set('correction_capsule',{fillColor:palette.purpleLight,gradientColor:palette.purpleDark,strokeColor:'#302445',strokeWidth:1.3});
set('correction_shadow',{fillColor:'#514164',opacity:8});
set('pauli_operators',{fontColor:'#FFFFFF'});
for(const id of ['left_classical_link','right_classical_link','alice_input','message_arrow'])set(id,{strokeColor:'#594284'});
for(const id of ['alice_input_arrow','message_arrow_tip'])set(id,{fillColor:'#594284'});
for(const id of ['quantum_left_return','quantum_right_return'])set(id,{strokeColor:palette.channelBlue,strokeWidth:1.2});
for(const id of ['quantum_left_return_arrow','quantum_right_return_arrow'])set(id,{fillColor:palette.channelBlue});
set('alice_hair_back',{fillColor:palette.hair});
set('alice_left_curl',{fillColor:'#252D2C'});
set('alice_right_curl',{fillColor:'#252D2C'});
set('alice_face',{fillColor:palette.skin});
set('alice_neck',{fillColor:'#D49D7B'});
set('alice_neck_shadow',{fillColor:'#B78368'});
set('alice_torso',{fillColor:palette.greenLight,gradientColor:palette.greenDark});
set('alice_shoulder_shade',{fillColor:'#278954'});
set('bob_head',{fillColor:palette.blueLight,gradientColor:palette.blueDark});
set('bob_crown',{fillColor:palette.blueLight,opacity:0});
set('bob_left_ear',{fillColor:'#3885BF'});
set('bob_right_ear',{fillColor:'#3885BF'});
set('bob_chin',{fillColor:'#2B71AB',opacity:0});
set('bob_torso',{fillColor:palette.blueLight,gradientColor:palette.blueDark});
set('bob_left_shoulder',{fillColor:'#2E79B3',opacity:0});
set('bob_right_shoulder',{fillColor:'#2E79B3',opacity:0});
set('attacker_body',{fillColor:'#374651',strokeColor:'#222D37'});
set('attacker_left_arm',{fillColor:'#394B58',strokeColor:'#24313B'});
set('attacker_right_arm',{fillColor:'#30404E',strokeColor:'#24313B'});
set('attacker_hood',{fillColor:'#374651',strokeColor:'#202B35'});
set('attacker_hood_highlight',{fillColor:'#788893'});
set('attacker_hood_right',{fillColor:'#263845'});
set('attacker_face_shadow',{fillColor:'#101820'});
set('attacker_face',{fillColor:'#C39579'});
set('attacker_left_lapel',{fillColor:'#546674',strokeColor:'#24313B'});
set('attacker_right_lapel',{fillColor:'#435664',strokeColor:'#24313B'});
set('attacker_chest',{fillColor:'#243442'});
set('attacker_laptop_back',{fillColor:'#717E8B',gradientColor:'#5F6875',strokeColor:'#26323E'});
set('attacker_laptop_base',{fillColor:'#485763',strokeColor:'#25323C'});
set('attacker_laptop_logo',{fillColor:'#D1D5DE',strokeColor:'#6D7783'});

function parseStyle(s) {
  const entries=s.split(';').filter(Boolean).map(e=>{const i=e.indexOf('=');return i<0?[e,null]:[e.slice(0,i),e.slice(i+1)];});
  return new Map(entries);
}
for(const cell of cells) {
  const change=changes.get(cell._attributes.id);
  if(!change)continue;
  const style=parseStyle(cell._attributes.style||'');
  for(const [k,v] of Object.entries(change))v===null?style.delete(k):style.set(k,String(v));
  cell._attributes.style=Array.from(style,([k,v])=>v===null?k:`${k}=${v}`).join(';')+';';
}
model._attributes.background='#FFFFFF';
doc.mxfile.diagram._attributes.name='Panel d — Matched palette';
const drawio=serializeSafe(doc,{compact:true,spaces:2});
fs.writeFileSync(path.join(root,out+'.drawio'),drawio);

// Native SVG text and paths stay editable. The SVG background is transparent.
const svgDoc=xml.xml2js(fs.readFileSync(path.join(root,'quantum_channel.svg'),'utf8'),{compact:false});
const svg=svgDoc.elements.find(e=>e.name==='svg');
svg.attributes.content=drawio;
svg.elements=svg.elements.filter(e=>!(e.name==='rect'&&!e.attributes.id&&e.attributes.width==='832'&&e.attributes.height==='509'));
const defs=svg.elements.find(e=>e.name==='defs');
const stop = (offset,color) => ({type:'element',name:'stop',attributes:{offset,'stop-color':color}});
for(const el of svg.elements) {
  const id=el.attributes?.id, change=changes.get(id);
  if(!change)continue;
  const a=el.attributes;
  if(change.fontColor!==undefined)a.fill=change.fontColor;
  if(change.fillColor!==undefined)a.fill=change.fillColor;
  if(change.strokeColor!==undefined)a.stroke=change.strokeColor;
  if(change.strokeWidth!==undefined)a['stroke-width']=String(change.strokeWidth);
  if(change.opacity!==undefined)a.opacity=String(change.opacity/100);
  if(change.gradientColor===null) {
    defs.elements=defs.elements.filter(e=>e.attributes?.id!=='gradient_'+id);
  } else if(change.gradientColor) {
    const gradientId='gradient_'+id;
    let grad=defs.elements.find(e=>e.attributes?.id===gradientId);
    if(!grad) {
      grad={type:'element',name:'linearGradient',attributes:{id:gradientId,x1:'0',y1:'0',x2:'0',y2:'1'}};
      defs.elements.push(grad);
    }
    grad.elements=[stop('0',change.fillColor),stop('1',change.gradientColor)];
    a.fill=`url(#${gradientId})`;
  }
  if(a['stroke-dasharray']&&change.strokeWidth) {
    const cell=cells.find(c=>c._attributes.id===id),style=parseStyle(cell._attributes.style);
    a['stroke-dasharray']=(style.get('dashPattern')||'3 4').split(' ').map(n=>Number(n)*change.strokeWidth).join(' ');
  }
}
const description=svg.elements.find(e=>e.name==='desc');
description.elements=[{type:'text',text:'Editable vector reconstruction recolored to match the reference figure: purple devices, green Alice, blue Bob, cyan quantum links, lavender plots, gray formula card, and a transparent canvas. All components are vectors and native text.'}];
fs.writeFileSync(path.join(root,out+'.svg'),serializeSafe(svgDoc,{compact:false,spaces:0}));
fs.writeFileSync(path.join(root,out+'_palette.json'),JSON.stringify(palette,null,2));
console.log(JSON.stringify({updatedCells:changes.size,totalCells:cells.length,files:[out+'.drawio',out+'.svg'],transparentSvg:true}));
