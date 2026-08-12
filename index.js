const { Client, GatewayIntentBits, AttachmentBuilder } = require('discord.js');
const { createCanvas, loadImage } = require('@napi-rs/canvas');
const fs = require('fs');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

const DATA_FILE = './levels.json';

function loadData() {
    if (!fs.existsSync(DATA_FILE)) fs.writeFileSync(DATA_FILE, '{}');
    return JSON.parse(fs.readFileSync(DATA_FILE));
}

function saveData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 4));
}

client.on('ready', () => {
    console.log(`Bot ${client.user.tag} adıyla cam gibi net tasarımıyla aktif!`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot || !message.guild) return;

    let data = loadData();
    let userId = message.author.id;

    if (!data[userId]) data[userId] = { xp: 0, level: 1 };

    data[userId].xp += 15;
    let currentXp = data[userId].xp;
    let currentLevel = data[userId].level;
    let neededXp = currentLevel * 100;

    if (currentXp >= neededXp) {
        data[userId].level += 1;
        data[userId].xp = 0;
        message.channel.send(`Tebrikler ${message.author}, **Seviye ${data[userId].level}** oldun! 🎉`);
    }

    saveData(data);

    // !rank Komutu
    if (message.content.startsWith('!rank')) {
        let target = message.mentions.users.first() || message.author;
        let targetData = data[target.id] || { xp: 0, level: 1 };
        
        let cXp = targetData.xp;
        let cLvl = targetData.level;
        let reqXp = cLvl * 100;

        let sorted = Object.keys(data).sort((a,b) => (data[b].level * 100 + data[b].xp) - (data[a].level * 100 + data[a].xp));
        let userRank = sorted.indexOf(target.id) + 1 || 1;

        // --- ULTRA HD TASARIM ---
        const canvas = createCanvas(1860, 560);
        const ctx = canvas.getContext('2d');

        // 1. Dış Çerçeve Koyu Gri Kutu
        ctx.fillStyle = '#18191c';
        ctx.beginPath();
        ctx.roundRect(0, 0, 1860, 560, 40);
        ctx.fill();

        // 2. İç Siyah Kart Kutu (MEE6 Stili)
        ctx.fillStyle = '#0f0f10';
        ctx.beginPath();
        ctx.roundRect(50, 50, 1760, 460, 30);
        ctx.fill();

        // 3. Profil Resmi Ve Yeşil Durum Simgesi
        try {
            const avatarURL = target.displayAvatarURL({ extension: 'png', size: 512 });
            const avatar = await loadImage(avatarURL);

            // Dairesel Profil Resmi Maskesi
            ctx.save();
            ctx.beginPath();
            ctx.arc(260, 280, 140, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.clip();
            ctx.drawImage(avatar, 120, 140, 280, 280);
            ctx.restore();

            // Avatar Siyah Çerçeve
            ctx.beginPath();
            ctx.arc(260, 280, 140, 0, Math.PI * 2, true);
            ctx.lineWidth = 8;
            ctx.strokeStyle = '#000000';
            ctx.stroke();

            // Yeşil Durum (Online) Simgesi
            ctx.beginPath();
            ctx.arc(360, 360, 38, 0, Math.PI * 2, true);
            ctx.fillStyle = '#23a55a';
            ctx.fill();
            ctx.lineWidth = 12;
            ctx.strokeStyle = '#0f0f10';
            ctx.stroke();
        } catch (e) {
            console.log("Avatar yüklenirken hata oluştu:", e);
        }

        // 4. Kullanıcı Adı
        ctx.fillStyle = '#ffffff';
        ctx.font = '500 52px sans-serif';
        ctx.fillText(target.username, 440, 230);

        // 5. RÜTBE ve Devasa Beyaz Rakam (#44)
        ctx.fillStyle = '#aaaaaa';
        ctx.font = '38px sans-serif';
        ctx.fillText('RÜTBE', 980, 140);
        
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 110px sans-serif';
        ctx.fillText(`#${userRank}`, 1120, 140);

        // 6. SEVİYE ve Birebir Turuncu Rakam (12)
        ctx.fillStyle = '#ff7b00';
        ctx.font = '38px sans-serif';
        ctx.fillText('SEVİYE', 1420, 140);
        
        ctx.font = 'bold 110px sans-serif';
        ctx.fillText(`${cLvl}`, 1590, 140);

        // 7. XP Metni
        ctx.fillStyle = '#aaaaaa';
        ctx.font = '36px sans-serif';
        ctx.fillText(`${cXp} / ${reqXp} XP`, 1400, 240);

        // 8. XP ÇUBUĞU (En Sağdan 6px Boşluk)
        const maxBarWidth = 1364;
        const barWidth = Math.min((cXp / reqXp) * maxBarWidth, maxBarWidth);

        // Arka Plan Çubuğu
        ctx.fillStyle = '#383a40';
        ctx.beginPath();
        ctx.roundRect(440, 280, maxBarWidth, 65, 30);
        ctx.fill();

        // Ön Doluluk Çubuğu (Turuncu)
        if (barWidth > 0) {
            ctx.fillStyle = '#ff7b00';
            ctx.beginPath();
            ctx.roundRect(440, 280, barWidth, 65, 30);
            ctx.fill();
        }

        // 9. Görseli Gönder
        const buffer = await canvas.encode('png');
        const attachment = new AttachmentBuilder(buffer, { name: 'rank_card.png' });
        message.channel.send({ files: [attachment] });
    }
});

// TOKENİ DISCLOUD ENV ÜZERİNDEN OKUR
client.login(process.env.TOKEN);
      
