const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('desktopApi', {
  loadCsv: () => ipcRenderer.invoke('load-csv'),
  openMailto: (mailto) => ipcRenderer.invoke('open-mailto', mailto),
});
