# 🧪 VS Code Extension Test Guide

Bu kılavuz, Sentry-AI VS Code Extension'ını test etmen için adım adım talimatlar içerir.

## 📋 Test Adımları

### 1️⃣ Extension'ı Aç

```bash
cd /Users/mikail/Sentry-AI/vscode-extension
code .
```

### 2️⃣ Extension Development Host'u Başlat

VS Code'da:
1. **F5**'e bas (veya Run → Start Debugging)
2. Yeni bir "Extension Development Host" penceresi açılacak
3. Bu yeni pencerede extension aktif olacak

### 3️⃣ Extension'ı Kontrol Et

Yeni pencerede:

#### A) Sidebar'ı Kontrol Et
- Sol tarafta **robot ikonu (🤖)** göreceksin
- Tıkla ve 3 panel göreceksin:
  - **Status**: Çalışma durumu
  - **Activity Log**: Aktivite geçmişi
  - **Statistics**: İstatistikler

#### B) Status Bar'ı Kontrol Et
- Sağ alt köşede: `$(robot) Sentry-AI: Inactive` göreceksin
- Tıkla → Status paneli açılacak

#### C) Command Palette'i Dene
1. **⌘+Shift+P** (Mac) veya **Ctrl+Shift+P** (Windows/Linux)
2. "Sentry-AI" yaz
3. Şu komutları göreceksin:
   - **Sentry-AI: Start Automation** ← Bunu seç!
   - Sentry-AI: Stop Automation
   - Sentry-AI: Restart
   - Sentry-AI: Show Status
   - Sentry-AI: Show Activity Logs
   - Sentry-AI: Open Settings

### 4️⃣ Sentry-AI'ı Başlat

1. Command Palette aç: **⌘+Shift+P**
2. "Sentry-AI: Start Automation" seç
3. Bildirim göreceksin: "Sentry-AI started successfully"
4. Status bar değişecek: `$(robot) Sentry-AI: Active` (turuncu arka plan)

### 5️⃣ Aktiviteyi İzle

Sentry-AI çalışırken:

1. **Sidebar Activity Log**'a bak
   - Her otomatik aksiyon burada görünecek
   - Uygulama adı, aksiyon, zaman damgası

2. **Statistics**'e bak
   - Actions Today: Bugün yapılan işlem sayısı
   - Status: Running/Stopped
   - Last Activity: Son aktivite

3. **Status Panel**'i aç
   - Command Palette → "Sentry-AI: Show Status"
   - Detaylı bilgi göreceksin

### 6️⃣ Test Dialog'u Oluştur

Sentry-AI'ın çalıştığını görmek için VS Code'da bir dialog oluştur:

#### Test 1: Dosya Kaydetme
1. Yeni bir dosya aç: **⌘+N**
2. Biraz yazı yaz
3. Kapat: **⌘+W**
4. "Do you want to save?" dialogu açılacak
5. **Sentry-AI otomatik olarak "Don't Save" veya "Save" tıklayacak!**
6. Activity Log'da göreceksin!

#### Test 2: Terminal Komutu
1. Terminal aç: **Ctrl+`**
2. Bir Python script çalıştır
3. Claude Code bir soru sorarsa, Sentry-AI otomatik yanıt verecek!

### 7️⃣ Log Dosyasını Kontrol Et

1. Command Palette aç: **⌘+Shift+P**
2. "Sentry-AI: Show Activity Logs" seç
3. `sentry_ai.log` dosyası açılacak
4. Tüm aktiviteleri detaylı göreceksin

### 8️⃣ Sentry-AI'ı Durdur

1. Command Palette: **⌘+Shift+P**
2. "Sentry-AI: Stop Automation"
3. Status bar değişecek: `$(robot) Sentry-AI: Inactive`

---

## 🐛 Sorun Giderme

### Extension Yüklenmiyorsa

1. **F5**'e tekrar bas
2. Veya: Run → Restart Debugging
3. Output panelini kontrol et (View → Output → Extension Host)

### Sentry-AI Başlamıyorsa

1. **Settings'i kontrol et**:
   ```bash
   cat /Users/mikail/Sentry-AI/vscode-extension/.vscode/settings.json
   ```

2. **Python path'i kontrol et**:
   ```bash
   ls /Users/mikail/Sentry-AI/venv/bin/python
   ```

3. **Manuel olarak test et**:
   ```bash
   cd /Users/mikail/Sentry-AI
   source venv/bin/activate
   python -m sentry_ai.main
   ```

### Activity Log Boşsa

1. Bir dialog oluştur (yukarıdaki testleri dene)
2. Log dosyasını kontrol et (Show Activity Logs)
3. Terminal'de Sentry-AI output'unu kontrol et

---

## ✅ Başarı Kriterleri

Extension başarıyla çalışıyorsa:

- ✅ Robot ikonu sidebar'da görünüyor
- ✅ Status bar göstergesi aktif
- ✅ Start komutu Sentry-AI'ı başlatıyor
- ✅ Activity Log dolmaya başlıyor
- ✅ Statistics güncellenıyor
- ✅ Notifications gösteriliyor (ayarlarda açıksa)
- ✅ Stop komutu Sentry-AI'ı durduruyor

---

## 📹 Ekran Görüntüleri

Test sırasında şu görünümleri göreceksin:

### Sidebar View
```
🤖 SENTRY-AI
  └─ Status
       ├─ ✅ Running
       ├─ Actions Today: 5
       └─ Last: VS Code: Yes
  └─ Activity Log
       ├─ ✓ VS Code: clicked 'Yes' (14:32:15)
       ├─ ✓ Terminal: allowed command (14:31:02)
       └─ ✓ Claude Code: approved (14:28:45)
  └─ Statistics
       ├─ 📊 Actions Today: 5
       ├─ ✅ Status: Running
       └─ 🕐 Last: VS Code: Yes
```

### Status Bar
```
Bottom right: [$(robot) Sentry-AI: Active]
              (orange background)
```

### Status Panel (Webview)
```
🤖 Sentry-AI Status

✅ Running
├─ Status: Active
├─ Actions Today: 5
├─ Last Activity: VS Code: Yes
├─ Auto Start: Disabled
└─ Observer Interval: 2.0s

📋 Features
✅ Vision AI with Claude Opus 4
✅ Automatic dialog detection
✅ Mouse & keyboard automation
✅ Real-time activity logging
✅ VS Code integration
```

---

## 🎯 İleri Seviye Testler

### Test 1: Vision AI Test
```bash
# Terminal'de
cd /Users/mikail/Sentry-AI
python test_computer_use.py
```

### Test 2: Multiple Dialogs
1. Birden fazla dosya aç
2. Hepsini değişiklik yap
3. "Close All" yap
4. Sentry-AI hepsini otomatik işleyecek!

### Test 3: Settings Değiştirme
1. VS Code Settings aç: **⌘+,**
2. "Sentry-AI" ara
3. Ayarları değiştir:
   - Auto Start: true
   - Show Notifications: false
   - Observer Interval: 5.0
4. Extension'ı restart et

---

## 🚀 Production Kullanımı

Test başarılıysa, production için:

### Option 1: VSIX Oluştur
```bash
cd /Users/mikail/Sentry-AI/vscode-extension
npm install -g vsce
vsce package
# sentry-ai-1.2.0.vsix oluşacak
```

### Option 2: Extensions'a Yükle
1. VS Code aç
2. Extensions (⌘+Shift+X)
3. ... (üç nokta) → "Install from VSIX"
4. `sentry-ai-1.2.0.vsix` seç
5. Reload VS Code

### Option 3: Daemon Kullan
```bash
# Background'da sürekli çalıştır
make daemon-install
make daemon-status
```

---

## 📞 Yardım

Sorun yaşarsan:
1. Developer Tools aç: Help → Toggle Developer Tools
2. Console tab'ına bak
3. Hataları buradan görebilirsin

**Happy Testing! 🎉**
