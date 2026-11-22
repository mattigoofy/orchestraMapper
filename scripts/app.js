import { redraw, exportToPNG } from './orchestra.js';
import { initEditor, getEditorMode, renderEditor } from './editor.js';
import { initDropdowns } from './dropdown.js';

export { image_base_url, json_config, cssVar, getRowColor, syncEditorHeight, syncToText};



const IMAGE_BASE_URL_FALLBACK = 'https://raw.githubusercontent.com/mattigoofy/orchestraMapper/main/figs/';
let image_base_url = IMAGE_BASE_URL_FALLBACK;

const json_config = { currentData: null, availableImages: [] };
window.json_config = json_config;

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function getRowColor() {
  return cssVar('--accent-blue');
}

function syncEditorHeight() {
  const canvas = document.getElementById('canvas-container');
  const editor = document.getElementById('editor-container');
  if (canvas && editor) {
    // On small screens the editor sits under the canvas and gets its height from CSS
    if (window.matchMedia('(max-width: 768px)').matches) {
      editor.style.height = '';
      return;
    }
    editor.style.height = canvas.offsetHeight + 'px';
  }
}

function syncToText() {
  document.getElementById('json-editor').value = JSON.stringify(json_config.currentData, null, 2);
}

async function handlePrint(canvasId) {
  const canvas = document.getElementById(canvasId);
  
  // Redraw without background
  await redraw(true);
  
  const dataUrl = canvas.toDataURL('image/png');
  const printWindow = window.open('', '_blank');

  redraw();

  printWindow.document.write(`
    <html><head><title>&#8203;</title>
    <style>
      @page { margin: 0; size: auto; }
      @media print { 
        body { margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        img { max-width: 100%; max-height: 100vh; object-fit: contain; }
      }
    </style>
    </head><body><img src="${dataUrl}" onload="window.print(); window.close();"></body></html>
  `);
  printWindow.document.close();
}

function compressUrl(obj) {
  // Bitmask for booleans: use_images | show_labels | show_row_count | invert
  const flags = (obj.use_images       ? 1 : 0)
              | (obj.show_labels      ? 2 : 0)
              | (obj.show_row_count   ? 4 : 0)
              | (obj.invert           ? 8 : 0);

  // Strip base URL, keep only the suffix
  const image_url_suffix = obj.image_url.startsWith(IMAGE_BASE_URL_FALLBACK)
    ? obj.image_url.slice(IMAGE_BASE_URL_FALLBACK.length)
    : obj.image_url;

  const conductor = [
    obj.conductor.name,
    obj.conductor.color.slice(1), // remove  #
    obj.conductor.image
  ];

  const sections = obj.sections.map(s => [
    s.name,
    s.color.slice(1), // remove #
    s.row,
    s.start_index,
    s.names
  ]);

  const mini = [
    obj.font_size,
    obj.icon_size,
    obj.title,
    flags,
    image_url_suffix,
    obj.date,
    conductor,
    sections
  ];

  return LZString.compressToEncodedURIComponent(JSON.stringify(mini));
}

function decompressUrl(str) {
  const json = LZString.decompressFromEncodedURIComponent(str);
  if (!json) return null;
  const d = JSON.parse(json);

  const flags = d[3];
  const image_url_suffix = d[4];

  const conductor = {
    name:  d[6][0],
    color: "#" + d[6][1],
    image: d[6][2]
  };

  const sections = d[7].map(s => ({
    name:        s[0],
    color:       "#" + s[1],
    row:         s[2],
    start_index: s[3],
    names:       s[4]
  }));

  return {
    font_size:      d[0],
    icon_size:      d[1],
    title:          d[2],
    use_images:     !!(flags & 1),
    show_labels:    !!(flags & 2),
    show_row_count: !!(flags & 4),
    invert:         !!(flags & 8),
    image_url:      image_url_suffix
                      ? IMAGE_BASE_URL_FALLBACK + image_url_suffix
                      : image_url_suffix,
    date:           d[5],
    conductor,
    sections
  };
}

// View mode: show the rendered layout as a plain image (long-press/right-click to save) + download button
function showView() {
  const canvas = document.getElementById('orchestra-canvas');
  canvas.toBlob(blob => {
    const blobUrl = URL.createObjectURL(blob);
    document.getElementById('view-image').src = blobUrl;
    document.getElementById('view-download-btn').addEventListener('click', () => {
      const link = document.createElement('a');
      link.download = 'orchestra.png';
      link.href = blobUrl;
      link.click();
    });
    document.body.classList.add('view-mode');
  }, 'image/png');
}

function handleShare(view = false) {
  let url = location.origin + location.pathname;
  let params = "?json=" + compressUrl(window.json_config.currentData) + (view ? "&view=1" : "");
  let fullUrl = url + params;

  navigator.clipboard.writeText(fullUrl).then(() => {
    const toast = document.createElement('div');
    toast.textContent = '🔗 URL copied!';
    toast.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#333;color:#fff;padding:8px 16px;border-radius:6px;z-index:9999';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  });

  return fullUrl;
}

document.addEventListener('DOMContentLoaded', () => {
  let url_params = new URLSearchParams(location.search);

  // ?compress=<full json>: compress it and continue to the short link (view is kept)
  if (url_params.get('compress') != null) {
    location.replace(location.pathname + '?json=' + compressUrl(JSON.parse(url_params.get('compress'))) + (url_params.get('view') === '1' ? '&view=1' : ''));
    return;
  }

  initEditor();
  initDropdowns();

  if (url_params.size > 0 && url_params.get('json') != null) {
    // console.log(url_params.get('json'));
    window.json_config.currentData = decompressUrl(url_params.get('json'))
    syncToText();
    renderEditor();
    redraw().then(() => {
      if (url_params.get('view') === '1') showView();
    });

  } else {
    // Load data, then render editor
    fetch('./orchestra.json')
      .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then(data => {
        json_config.currentData = data;
        image_base_url = data.image_url ?? IMAGE_BASE_URL_FALLBACK;
        syncToText();
        renderEditor();
        redraw();
      })
      .catch(err => console.error('Error loading orchestra data:', err));
  }

  window.addEventListener('resize', syncEditorHeight);

  document.getElementById('apply-btn').addEventListener('click', () => {
    if (getEditorMode() === 'visual') {
      redraw();
    } else {
      try {
        json_config.currentData = JSON.parse(document.getElementById('json-editor').value);
        redraw();
      } catch (err) {
        alert('Error parsing JSON: ' + err.message);
      }
    }
  });

  document.getElementById('export-btn').addEventListener('click', () => exportToPNG('orchestra-canvas', 'orchestra.png'));
  document.getElementById('print-btn').addEventListener('click', () => handlePrint('orchestra-canvas'));
  document.getElementById('share-btn').addEventListener('click', () => handleShare());
  document.getElementById('share-image-btn').addEventListener('click', () => handleShare(true));
});
