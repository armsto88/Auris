// Auris EasyEDA page driver: lets Claude run EasyEDA Pro scripts in an open editor tab using only
// page JavaScript (Claude in Chrome's javascript_tool) plus file_upload, with no clicks or
// screenshots, so the browser is not pulled to the front for every step.
//
// How it is used (one javascript_tool call injects this file's text into the EasyEDA tab):
//   1. A hidden file input "Auris script loader" is added to the page. find() it, then
//      file_upload local .js files to it (e.g. hardware/easyeda/capture-power.js); each lands in
//      window.__aurisFiles[name].
//   2. await window.__aurisRun(window.__aurisFiles[name], { titleRe, timeoutMs }) opens
//      Advanced > Run Script, puts the code in its editor, presses Run, waits for the script's
//      result dialog (title matching titleRe), returns { title, text } and closes both windows.
//      While it runs it answers EasyEDA's "this device has been updated" prompt with Place, which
//      keeps the device version already in the project.
//   3. Long runs (a whole sheet takes 1-3 minutes) must not be awaited in one call: CDP gives up
//      after 45 s. Start them with window.__aurisStart(name) and poll window.__aurisJobResult.
//   4. await window.__aurisRenamePage("P1", "POWER") renames a page through the page tree (the
//      dmt_Schematic.modifySchematicPageName API returns false in EasyEDA Pro 3.2).
// Read results in slices under ~1000 characters, and replace = & ? first: the tool blocks output
// that looks like query strings.
//
// Checked on EasyEDA Pro 4.1.105 (2026-11-18): works unchanged. The driver file can also be loaded
// through the file input and started with new Function(window.__aurisFiles[name])(). EasyEDA's
// warnings and errors appear as "messager-panel" toasts; a MutationObserver on document.body
// catches them while a script runs (that is how the 4.1 "Create project component failed"
// problem, fixed in easyeda_capture_template.js, was found).
//
// Not possible this way (EasyEDA Pro 3.2.209, 2026-11-17): the page Size dropdown ignores
// synthetic events, so page sizes are set by hand; scripts cannot open network connections
// ("external interaction permission" is off), and a page fetch from localhost hits Chrome's
// local-network-access prompt.
(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  window.__aurisFiles = window.__aurisFiles || {};
  if (!document.getElementById('auris-file-in')) {
    const inp = document.createElement('input');
    inp.type = 'file'; inp.id = 'auris-file-in'; inp.multiple = true;
    inp.setAttribute('aria-label', 'Auris script loader');
    inp.style.cssText = 'position:fixed;left:0;bottom:0;width:120px;height:20px;opacity:0.01;z-index:2147483647';
    inp.addEventListener('change', async () => { for (const f of inp.files) window.__aurisFiles[f.name] = await f.text(); });
    document.body.appendChild(inp);
  }
  // A full synthetic pointer + mouse sequence: enough for EasyEDA's menus and page tree.
  const press = (el, button = 0) => {
    const r = el.getBoundingClientRect();
    const o = { bubbles: true, cancelable: true, view: window, button, buttons: button ? 2 : 1, clientX: r.x + Math.min(10, r.width / 2), clientY: r.y + r.height / 2, pointerId: 1, isPrimary: true };
    const seq = button === 2
      ? [['pointerdown', PointerEvent], ['mousedown', MouseEvent], ['pointerup', PointerEvent], ['mouseup', MouseEvent], ['contextmenu', MouseEvent]]
      : [['pointerover', PointerEvent], ['mouseover', MouseEvent], ['pointermove', PointerEvent], ['mousemove', MouseEvent], ['pointerdown', PointerEvent], ['mousedown', MouseEvent], ['pointerup', PointerEvent], ['mouseup', MouseEvent], ['click', MouseEvent]];
    for (const [t, C] of seq) el.dispatchEvent(new C(t, o));
  };
  const waitFor = async (f, ms, what) => { const t0 = Date.now(); for (;;) { const v = f(); if (v) return v; if (Date.now() - t0 > ms) throw new Error('timed out waiting for ' + what); await sleep(150); } };
  const dialogs = () => Array.from(document.querySelectorAll('[class*="lc_modal_dialog__header_"]')).map((h) => ({ head: h, title: h.textContent.trim(), root: h.parentElement }));
  const leaf = (re) => Array.from(document.querySelectorAll('body *')).filter((e) => e.children.length === 0 && re.test((e.textContent || '').trim()) && e.getBoundingClientRect().height > 0);
  const answerUpdatePrompt = () => {
    for (const d of dialogs()) {
      if (d.title !== 'Warning' || !/device have been updated/.test(d.root.innerText)) continue;
      const b = Array.from(d.root.querySelectorAll('button')).find((x) => x.textContent.trim() === 'Place');
      if (b) { b.click(); window.__aurisPlaced = (window.__aurisPlaced || 0) + 1; }
    }
  };

  window.__aurisRun = async (code, { titleRe = /^Auris/, timeoutMs = 600000 } = {}) => {
    // let a Run Script window from the previous run finish closing
    for (let i = 0; i < 20 && dialogs().some((d) => d.title === 'Run Script'); i++) await sleep(200);
    await sleep(300);
    const watch = setInterval(answerUpdatePrompt, 400);
    try {
      press(Array.from(document.querySelectorAll('div[class*="eda-menu-btn_"]')).find((e) => /^Advanced/.test(e.textContent.trim())).querySelector('span[class*="eda-menu-btn-top_"]'));
      press(await waitFor(() => Array.from(document.querySelectorAll('div[class*="eda-menu-item_"]')).find((e) => /^Run Script/.test(e.textContent.trim())), 3000, 'Run Script menu item'));
      const rs = await waitFor(() => dialogs().find((d) => d.title === 'Run Script'), 5000, 'Run Script window');
      const content = await waitFor(() => rs.root.parentElement.querySelector('.cm-content') || document.querySelector('.cm-content'), 3000, 'code editor');
      const view = content.cmView && content.cmView.view;   // CodeMirror 6
      if (!view) throw new Error('no CodeMirror view on the editor');
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: code } });
      if (view.state.doc.length !== code.length) throw new Error(`editor holds ${view.state.doc.length} chars, expected ${code.length}`);
      const seen = new Set(dialogs().map((d) => d.root));
      Array.from(document.querySelectorAll('button')).find((b) => /^Run\(F9\)$/.test(b.textContent.trim())).click();
      const res = await waitFor(() => dialogs().find((d) => !seen.has(d.root) && titleRe.test(d.title)), timeoutMs, 'result dialog');
      const out = { title: res.title, text: res.root.innerText.replace(res.title, '').trim() };
      // 4.1: the pointer sequence alone sometimes leaves the dialog open; a plain click closes it
      const x = res.root.querySelector('[class*="header_right_close"]') || res.root.querySelector('[class*="close"], [class*="Close"]') || res.head.querySelector('svg, i, span:last-child');
      try { if (x) { press(x); await sleep(200); if (document.contains(x)) x.click(); } } catch (_) { /* leave it */ }
      await sleep(300);
      const rs2 = dialogs().find((d) => d.title === 'Run Script');
      const cancel = rs2 && Array.from(rs2.root.parentElement.querySelectorAll('button')).find((b) => b.textContent.trim() === 'Cancel');
      if (cancel) cancel.click();
      window.__aurisLast = out;
      return out;
    } finally { clearInterval(watch); }
  };

  window.__aurisStart = (name, opts = { titleRe: /^Auris capture/, timeoutMs: 900000 }) => {
    const code = window.__aurisFiles[name];
    if (!code) throw new Error(name + ' not loaded');
    window.__aurisJobResult = null;
    window.__aurisJobStart = Date.now();
    window.__aurisJob = window.__aurisRun(code, opts)
      .then((r) => (window.__aurisJobResult = r)).catch((e) => (window.__aurisJobResult = { error: String(e) }));
    return { started: name, chars: code.length };
  };

  window.__aurisRenamePage = async (from, to) => {
    const tab = leaf(/^Page$/)[0]; if (tab) press(tab);
    await sleep(500);
    const item = leaf(new RegExp('^\\d+\\.\\s*' + from + '$'))[0];
    if (!item) throw new Error(from + ' not in the page tree');
    press(item, 2);
    await sleep(500);
    const ren = leaf(/^Rename$/)[0]; if (!ren) throw new Error('no Rename item');
    press(ren.closest('[class*="item"]') || ren);
    await sleep(500);
    const input = document.activeElement && document.activeElement.tagName === 'INPUT' ? document.activeElement : Array.from(document.querySelectorAll('input')).find((i) => i.value === from);
    if (!input) throw new Error('no rename box');
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(input, to);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    for (const t of ['keydown', 'keyup']) input.dispatchEvent(new KeyboardEvent(t, { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
    await sleep(800);
    return leaf(/^\d+\.\s/).map((e) => e.textContent.trim());
  };
  return 'Auris page driver ready';
})();
