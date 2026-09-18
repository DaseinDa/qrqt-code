(function(){
 // Set this to the project root before running.
 var base='C:/Users/DELL/Desktop/PQNet/';
 var source=new File(base+'tmp/overview_edit/v4_working_source.ai');
 var output=new File(base+'Figure/final_overview_figure_v4.ai');
 var pdf=new File(base+'output/pdf/final_overview_figure_v4.pdf');
 var logFile=new File(base+'tmp/overview_edit/v4_font_edit_log.txt');
 var level=app.userInteractionLevel,d=null;
 function log(s){logFile.encoding='UTF-8';logFile.open('a');logFile.writeln(s);logFile.close();}
 function id(s){return d.getPageItemFromUuid(s);}
 function ink(t){var b=t.geometricBounds;return [b[0],b[1],b[2],b[3]];}
 function center(t){var b=ink(t);return [(b[0]+b[2])/2,(b[1]+b[3])/2];}
 function place(t,x,y){var c=center(t);t.translate(x-c[0],y-c[1]);}
 function union(a,b){return [Math.min(a[0],b[0]),Math.max(a[1],b[1]),Math.max(a[2],b[2]),Math.min(a[3],b[3])];}
 function copyStyle(target,reference){var r=reference.textRange.characterAttributes;var fontName=r.textFont.name,size=r.size,hs=r.horizontalScale,vs=r.verticalScale,tracking=r.tracking,shift=r.baselineShift;var a=target.textRange.characterAttributes;a.textFont=app.textFonts.getByName(fontName);a.size=size;a.horizontalScale=hs;a.verticalScale=vs;a.tracking=tracking;a.baselineShift=shift;}
 function curves(){var names=['chart curve independent','chart curve sequential','chart curve burst','chart curve correlated solid','chart curve correlated dashed'],all=[];for(var k=0;k<names.length;k++){var p=d.pathItems.getByName(names[k]),v=[p.name,p.strokeWidth,p.opacity,p.geometricBounds.join(',')];for(var n=0;n<p.pathPoints.length;n++){var pt=p.pathPoints[n];v.push(pt.anchor.join(','),pt.leftDirection.join(','),pt.rightDirection.join(','));}all.push(v.join('|'));}return all.join('\n');}
 function title(bodyId,openerId,content,targetY){
  log('BEGIN TITLE '+bodyId);
  var t=id(bodyId),bounds=ink(t);
  if(openerId){var opener=id(openerId);bounds=union(bounds,ink(opener));opener.remove();}
  var cx=(bounds[0]+bounds[2])/2,cy=targetY===null?(bounds[1]+bounds[3])/2:targetY;
  if(t.contents!==content)t.contents=content;copyStyle(t,id('12519'));
  // Match the untouched (c) caption: Arial regular opening bracket, bold caption body.
  t.characters[0].characterAttributes.textFont=app.textFonts.getByName('ArialMT');
  place(t,cx,cy);t.name='overview caption '+content.substr(1,1);
  log('TITLE '+content+' size='+t.textRange.characterAttributes.size+' horizontalScale='+t.textRange.characterAttributes.horizontalScale);
 }
 try{
  app.userInteractionLevel=UserInteractionLevel.DONTDISPLAYALERTS;d=app.open(source);
  if(id('12519').contents!=='c) Joint Threat Model'||id('15487').contents!=='i'||id('15531').contents!=='Quantum Channel')throw new Error('Unexpected v3 source objects');
  var protectedCurves=curves();
  var cTitleBefore=id('12519').contents+'|'+id('12519').geometricBounds.join(',')+'|'+id('12518').geometricBounds.join(',');
  log('OPEN '+d.name);

  title('9343',null,'(a) Teleportation with RSA protection',-205.9);
  title('12505','12504','(b) QRQT Framework',-205.9);
  title('12521','12520','(d) Information-Theoretic Security',null);
  id('12505').translate(0,id('9343').geometricBounds[1]-id('12505').geometricBounds[1]);
  id('12521').translate(0,id('12519').geometricBounds[1]-id('12521').geometricBounds[1]);

  var personIds=['15527','15529'];
  for(var p=0;p<personIds.length;p++){var person=id(personIds[p]),oldCenter=center(person);copyStyle(person,id('9345'));place(person,oldCenter[0],oldCenter[1]);log('PERSON '+person.contents+' size='+person.textRange.characterAttributes.size);}

  var channel=id('15531'),channelCenter=center(channel);channel.contents='QUANTUM CHANNEL';copyStyle(channel,id('12503'));place(channel,channelCenter[0],channelCenter[1]);log('CHANNEL '+channel.contents+' size='+channel.textRange.characterAttributes.size);

  var rhoIndex=id('15487'),referenceIndex=id('15485'),originalLeft=rhoIndex.geometricBounds[0];copyStyle(rhoIndex,referenceIndex);var rb=rhoIndex.geometricBounds,refb=referenceIndex.geometricBounds;rhoIndex.translate(originalLeft-rb[0],refb[1]-rb[1]);
  log('RHO SUBSCRIPT i size='+rhoIndex.textRange.characterAttributes.size+' horizontalScale='+rhoIndex.textRange.characterAttributes.horizontalScale);

  if(curves()!==protectedCurves)throw new Error('Protected curve geometry changed');
  if(cTitleBefore!==id('12519').contents+'|'+id('12519').geometricBounds.join(',')+'|'+id('12518').geometricBounds.join(','))throw new Error('Protected c caption changed');
  log('PASS protected curve geometry and c caption unchanged');
  var pdfOptions=new PDFSaveOptions();pdfOptions.preserveEditability=true;pdfOptions.embedICCProfile=true;pdfOptions.viewAfterSaving=false;d.saveAs(pdf,pdfOptions);log('PDF_SAVED '+pdf.fsName);
  var aiOptions=new IllustratorSaveOptions();aiOptions.pdfCompatible=true;aiOptions.compressed=true;aiOptions.embedICCProfile=true;aiOptions.embedLinkedFiles=true;d.saveAs(output,aiOptions);log('AI_SAVED '+output.fsName);
  log('SUCCESS textFrames='+d.textFrames.length);d.close(SaveOptions.DONOTSAVECHANGES);d=null;
  return 'SUCCESS: v4 AI and PDF saved, four priority typography changes applied.';
 }catch(e){log('ERROR '+e.message+' line='+e.line);throw e;}
 finally{if(d){try{d.close(SaveOptions.DONOTSAVECHANGES);}catch(ignore){}}app.userInteractionLevel=level;}
})();
