(function(){
 // Set this to the project root before running.
 var base='C:/Users/DELL/Desktop/PQNet/';
 var input=new File(base+'tmp/overview_edit/overview_working_source.ai');
 var output=new File(base+'Figure/final_overview_figure_v3.ai');
 var pdf=new File(base+'output/pdf/final_overview_figure_v3.pdf');
 var logFile=new File(base+'tmp/overview_edit/edit_log.txt');
 var level=app.userInteractionLevel,d=null;
 function log(s){logFile.encoding='UTF-8';logFile.open('a');logFile.writeln(s);logFile.close();}
 function rgb(hex){var c=new RGBColor();c.red=parseInt(hex.substr(1,2),16);c.green=parseInt(hex.substr(3,2),16);c.blue=parseInt(hex.substr(5,2),16);return c;}
 function id(s){return d.getPageItemFromUuid(s);}
 function text(s,size,font,color){var t=d.textFrames.add();t.contents=s;t.textRange.characterAttributes.textFont=app.textFonts.getByName(font||'ArialMT');t.textRange.characterAttributes.size=size;t.textRange.characterAttributes.fillColor=rgb(color||'#111111');return t;}
 function inkBounds(t){var du=t.duplicate(),ol=du.createOutline(),b=ol.geometricBounds;var copy=[b[0],b[1],b[2],b[3]];ol.remove();return copy;}
 function placeInk(t,cx,cy){var b=inkBounds(t);t.translate(cx-(b[0]+b[2])/2,cy-(b[1]+b[3])/2);}
 function sub(t,n,size,shift){var a=t.characters[n].characterAttributes;a.size=size;a.baselineShift=shift;a.textFont=app.textFonts.getByName('TimesNewRomanPSMT');}
 function pathByName(name){return d.pathItems.getByName(name);}
 function snapshotCurves(){var names=['chart curve independent','chart curve sequential','chart curve burst','chart curve correlated solid','chart curve correlated dashed'];var out=[];for(var j=0;j<names.length;j++){var p=pathByName(names[j]),s=[p.name,p.strokeWidth,p.opacity,p.geometricBounds.join(',')];for(var n=0;n<p.pathPoints.length;n++){var pt=p.pathPoints[n];s.push(pt.anchor.join(','),pt.leftDirection.join(','),pt.rightDirection.join(','));}out.push(s.join('|'));}return out.join('\n');}
 try{
   app.userInteractionLevel=UserInteractionLevel.DONTDISPLAYALERTS;
   d=app.open(input);
   log('OPEN '+d.name+' textFrames='+d.textFrames.length);
   var curvesBefore=snapshotCurves();
   if(id('9329').contents!=='RSA/DSA broken')throw new Error('Unexpected RSA source label');
   if(id('15513').contents!=='I, X, Y, Z')throw new Error('Unexpected Pauli source label');

   // (a): distinguish RSA encryption from digital signatures.
   var rsa=id('9329');rsa.contents='RSA encryption broken';rsa.textRange.characterAttributes.size=8.5;
   placeInk(rsa,151,-133.4);
   var plate=d.pathItems.roundedRectangle(-126.5,108,86,25.5,2,2);plate.name='RSA label contrast panel';plate.filled=true;plate.fillColor=rgb('#741C22');plate.stroked=false;plate.opacity=88;plate.move(rsa,ElementPlacement.PLACEAFTER);
   var cap=id('9343'),oldCap=id('9342');cap.contents='(a) Teleportation with RSA protection';oldCap.remove();placeInk(cap,155.8,-205.9);
   log('EDIT a RSA label and caption');

   // Replace only the outlined phi glyphs; retain existing ket delimiters.
   var ketIds=['9873','10926'];
   for(var k=0;k<ketIds.length;k++){
     var phi=id(ketIds[k]),b=phi.geometricBounds,cx=(b[0]+b[2])/2;
     phi.remove();var psi=text('\u03c8',13,'TimesNewRomanPS-ItalicMT','#111111');psi.name='input state psi '+(k===0?'a':'b');placeInk(psi,cx,-123.8);
   }
   log('EDIT input kets phi to psi');

   // (b): compact memory annotation adjacent to Bob, using defined variables.
   var box=d.pathItems.roundedRectangle(-198,528,58,18.4,2,2);box.name='Bob quantum memory annotation';box.filled=true;box.fillColor=rgb('#F0F5F9');box.stroked=true;box.strokeColor=rgb('#64859F');box.strokeWidth=0.5;
   var memory=text('Quantum memory',6.4,'ArialMT','#24475F');memory.name='Bob quantum memory';placeInk(memory,557,-203.15);
   var condition=text('\u03c4m < Tcoh',7.4,'TimesNewRomanPS-ItalicMT','#24475F');condition.name='memory condition tau_m less than T_coh';
   sub(condition,1,5.1,-1.8);for(var co=6;co<9;co++)sub(condition,co,4.9,-1.8);
   placeInk(condition,557,-211.25);
   log('EDIT b quantum memory condition');

   // (d): one transmitted pair, not a transformation from M1 to M2.
   id('15538').remove();id('15541').remove();
   pathByName('message arrow').remove();pathByName('message arrow tip').remove();
   var pair=text('(M1, M2)',10.2,'TimesNewRomanPS-ItalicMT');pair.name='classical correction bits M1 M2';sub(pair,2,6.6,-2.4);sub(pair,6,6.6,-2.4);placeInk(pair,438.55,-295.9);
   log('EDIT d classical bit pair');

   // (d): the exact correction convention from main.tex Eq. (3).
   var pauli=id('15513');pauli.contents='ZM2XM1';pauli.textRange.characterAttributes.textFont=app.textFonts.getByName('TimesNewRomanPS-ItalicMT');pauli.textRange.characterAttributes.size=10;
   for(var m=1;m<=4;m+=3){pauli.characters[m].characterAttributes.size=6.4;pauli.characters[m].characterAttributes.baselineShift=3.8;}
   sub(pauli,2,4.5,2.3);sub(pauli,5,4.5,2.3);placeInk(pauli,523.4,-295.6);
   log('EDIT d Pauli Z^(M2)X^(M1)');

   // (d): same ensemble notation and index as manuscript Eq. (6).
   var indices=['15493','15491','15488','15480','15478','15475'];
   for(var v=0;v<indices.length;v++){var index=id(indices[v]);if(index.contents!=='l')throw new Error('Unexpected summation index');index.contents='i';}
   var chi=id('15471');chi.contents='\u03c7(\u2130) = S(';chi.characters[2].characterAttributes.textFont=app.textFonts.getByName('CambriaMath');
   // Keep actual U+03C1 rho. A different math font improves its distinction from p.
   var firstRho=id('15479'),secondRho=id('15492');
   if(firstRho.contents.indexOf('\u03c1')<0||secondRho.contents.indexOf('\u03c1')<0)throw new Error('Missing Greek rho');
   firstRho.characters[1].characterAttributes.textFont=app.textFonts.getByName('CambriaMath');
   secondRho.characters[3].characterAttributes.textFont=app.textFonts.getByName('CambriaMath');
   log('EDIT d Holevo: Greek rho U+03C1, script E U+2130, index i');
   if(snapshotCurves()!==curvesBefore)throw new Error('Protected schematic curves changed');
   log('PASS protected schematic curves unchanged');

   var pdfOptions=new PDFSaveOptions();pdfOptions.preserveEditability=true;pdfOptions.embedICCProfile=true;pdfOptions.viewAfterSaving=false;
   d.saveAs(pdf,pdfOptions);log('PDF_SAVED '+pdf.fsName);
   var options=new IllustratorSaveOptions();options.pdfCompatible=true;options.compressed=true;options.embedICCProfile=true;options.embedLinkedFiles=true;
   d.saveAs(output,options);log('AI_SAVED '+output.fsName);
   log('SUCCESS textFrames='+d.textFrames.length+' artboards='+d.artboards.length);
   d.close(SaveOptions.DONOTSAVECHANGES);d=null;return 'SUCCESS';
 }catch(e){log('ERROR '+e.message+' line='+e.line);throw e;}
 finally{if(d){try{d.close(SaveOptions.DONOTSAVECHANGES);}catch(ignore){}}app.userInteractionLevel=level;}
})();
