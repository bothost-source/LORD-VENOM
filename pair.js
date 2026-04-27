const { 
    default: makeWASocket, 
    useMultiFileAuthState, 
    delay, 
    makeCacheableSignalKeyStore,
    DisconnectReason 
} = require("@whiskeysockets/baileys");
const pino = require("pino");

const phoneNumber = process.argv[2];

async function startPairing() {
    // Saves sessions in a folder named after the phone number
    const { state, saveCreds } = await useMultiFileAuthState(`./sessions/${phoneNumber}`);
    
    const sock = makeWASocket({
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, pino({ level: "fatal" })),
        },
        printQRInTerminal: false,
        logger: pino({ level: "fatal" }),
        browser: ["Ubuntu", "Chrome", "20.0.04"],
    });

    if (!sock.authState.creds.registered) {
        await delay(2000);
        const code = await sock.requestPairingCode(phoneNumber);
        // The Python script looks for these exact "VENOM" tags
        console.log(`VENOM_CODE_START:${code}:VENOM_CODE_END`);
    }

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === "open") {
            console.log("SUCCESS: LORD-VENOM LINKED");
            process.exit(0);
        }
        if (connection === "close") {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            if (!shouldReconnect) process.exit(1);
        }
    });
}

startPairing();
