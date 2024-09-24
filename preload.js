const { contextBridge } = require('electron');
const axios = require('axios');
const keytar = require('keytar');
const io = require('socket.io-client');

// Expose APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    axiosGet: axios.get,
    keytarGetPassword: keytar.getPassword,
    keytarSetPassword: keytar.setPassword,
    ioConnect: io,
});