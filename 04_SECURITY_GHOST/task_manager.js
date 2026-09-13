const tasks = [
    { id: 'TASK_01', description: 'Solana Kontratını X üzerinde paylaş ve etiketle', reward: '100 CFEL' },
    { id: 'TASK_02', description: 'DEX Screener üzerindeki MUCIZEWORK profiline roket (boost) at', reward: '250 CFEL' },
    { id: 'TASK_03', description: 'Gruba 5 aktif Web3 geliştiricisi davet et', reward: '500 CFEL' }
];

function getTaskList() {
    let msg = "🏛️ *MUCIZEWORK TOPLULUK GÖREVLERİ* 🏛️\n\n";
    tasks.forEach((t, i) => {
        msg += `📌 *Görev ${i+1}:* ${t.description}\n🎁 *Ödül:* \`${t.reward}\`\n👉 KOD: \`/claim ${t.id}\`\n\n`;
    });
    msg += "── *Mühür: Yunus Kalkan* ──";
    return msg;
}

module.exports = { getTaskList };
