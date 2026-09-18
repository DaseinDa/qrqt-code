// Import the requested vector and save native Illustrator and PDF copies.
// This script only edits its newly opened document.
(function () {
  // Set this to the project root before running.
  var base = 'C:/path/to/PQNet/';
  var source = new File(base + 'drawio_vector/quantum_channel_matched.svg');
  var aiFile = new File(base + 'drawio_vector/quantum_channel_matched.ai');
  var pdfFolder = new Folder(base + 'output/pdf');
  var tempFolder = new Folder(base + 'tmp/pdfs');
  if (!pdfFolder.parent.exists) pdfFolder.parent.create();
  if (!pdfFolder.exists) pdfFolder.create();
  if (!tempFolder.parent.exists) tempFolder.parent.create();
  if (!tempFolder.exists) tempFolder.create();
  var report = new File(base + 'tmp/pdfs/illustrator_conversion.txt');
  report.encoding = 'UTF-8';
  function log(s) { report.open('a'); report.writeln(s); report.close(); }
  var previousLevel = app.userInteractionLevel;
  var doc = null;
  try {
    app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
    log('START Illustrator=' + app.version);
    doc = app.open(source, DocumentColorSpace.RGB);
    log('OPENED artboards=' + doc.artboards.length + ' paths=' + doc.pathItems.length + ' textFrames=' + doc.textFrames.length + ' rasterItems=' + doc.rasterItems.length + ' placedItems=' + doc.placedItems.length);
    for (var i=0; i<doc.textFrames.length; i++) {
      var tf = doc.textFrames[i];
      log('TEXT ' + tf.contents.replace(/[\r\n]/g,' / ') + ' FONT=' + tf.textRange.characterAttributes.textFont.name);
    }
    if (doc.rasterItems.length > 0 || doc.placedItems.length > 0) throw new Error('Unexpected raster or linked content in vector import');
    var pdfOptions = new PDFSaveOptions();
    pdfOptions.preserveEditability = true;
    pdfOptions.generateThumbnails = true;
    pdfOptions.embedICCProfile = true;
    pdfOptions.viewAfterSaving = false;
    doc.saveAs(new File(base + 'output/pdf/quantum_channel_matched.pdf'), pdfOptions);
    log('PDF_SAVED');
    var aiOptions = new IllustratorSaveOptions();
    aiOptions.pdfCompatible = true;
    aiOptions.compressed = true;
    aiOptions.embedLinkedFiles = true;
    aiOptions.embedICCProfile = true;
    doc.saveAs(aiFile, aiOptions);
    log('AI_SAVED path=' + aiFile.fsName);
    doc.close(SaveOptions.DONOTSAVECHANGES);
    doc = null;
    log('SUCCESS');
    return 'SUCCESS';
  } catch(e) {
    log('ERROR ' + e.message + ' line=' + e.line);
    if(doc) { try {doc.close(SaveOptions.DONOTSAVECHANGES);}catch(ignore){} }
    throw e;
  } finally {
    app.userInteractionLevel = previousLevel;
  }
})();
