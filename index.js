const { app, BrowserWindow, ipcMain, shell } = require('electron');
const fs = require('fs/promises');
const path = require('path');

ipcMain.handle('load-csv', () => fs.readFile(path.join(__dirname, 'example_data.csv'), 'utf8'));

ipcMain.handle('open-mailto', async (_event, mailto) => {
  if (typeof mailto !== 'string' || !mailto.toLowerCase().startsWith('mailto:')) {
    throw new Error('Only mailto links can be opened.');
  }
  await shell.openExternal(mailto);
});

function createWindow() {
  const window = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 1100,
    minHeight: 760,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  window.loadFile('app.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});