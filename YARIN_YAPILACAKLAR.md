# 📋 Yarın Yapılacaklar - v1.2.0 Finalization

**Tarih**: 2025-11-03 (Yarın)
**Hedef**: Extension test + Marketplace yayını
**Tahmini Süre**: 2-3 saat

---

## 🎯 Ana Hedef

**Extension'ı tam çalışır hale getirip VS Code Marketplace'e yüklemek**

---

## ✅ Test Checklist (Öncelik Sırasına Göre)

### 1️⃣ Extension Test (30 dk)

- [ ] Extension Development Host'ta F5 bas
- [ ] "Start" butonuna tıkla
- [ ] Status "Active" oluyor mu?
- [ ] Claude Code'a soru sor: "Create a Python hello world"
- [ ] Dialog otomatik kapanıyor mu?
- [ ] Activity Log doldu mu?
- [ ] Statistics güncellendi mi?

**Beklenen Sonuç**:
```
✅ Dialog açılır
✅ 2 saniye içinde ENTER basılır (keyboard approach)
✅ Dialog kapanır
✅ Activity Log: "Code: Yes button"
✅ Statistics: "Actions Today: 1"
```

**Eğer Çalışmazsa**:
- Debug Console'a bak
- Log dosyasını kontrol et: `tail -f sentry_ai.log`
- `parseLogOutput()` fonksiyonunu düzelt

### 2️⃣ Activity Log Fix (30 dk)

**Problem**: Activity Log paneli boş kalıyor

**Çözüm**: `extension.ts` dosyasında `parseLogOutput()` fonksiyonunu düzelt

```typescript
function parseLogOutput(output: string) {
    const config = vscode.workspace.getConfiguration('sentry-ai');
    const showNotifications = config.get<boolean>('showNotifications');

    // Pattern 1: Keyboard actions
    if (output.includes('Pressed') && output.includes('key')) {
        const match = output.match(/Pressed (\w+) key/);
        if (match) {
            actionsToday++;
            lastActivity = `Keyboard: ${match[1]}`;
            activityTreeProvider.addActivity({
                app: 'Code',
                action: `Pressed ${match[1]}`,
                time: new Date().toLocaleTimeString()
            });
        }
    }

    // Pattern 2: Vision AI detection
    if (output.includes('Vision AI detected dialog')) {
        const match = output.match(/Vision AI detected dialog in (.+)/);
        if (match) {
            activityTreeProvider.addActivity({
                app: match[1],
                action: 'Vision AI detected',
                time: new Date().toLocaleTimeString()
            });
        }
    }

    // Pattern 3: Successfully automated
    if (output.includes('Successfully automated')) {
        const match = output.match(/Successfully automated (.+?) dialog/);
        if (match) {
            actionsToday++;
            lastActivity = `${match[1]}: Automated`;
            statsTreeProvider.updateStats(actionsToday);
            updateStatusBar();

            if (showNotifications) {
                vscode.window.showInformationMessage(
                    `Sentry-AI automated dialog in ${match[1]}`
                );
            }
        }
    }
}
```

**Test**:
- Extension restart
- Dialog oluştur
- Activity Log'da görünüyor mu?

### 3️⃣ End-to-End Test (30 dk)

**Senaryo 1: Basit Test**
1. Extension'dan "Start"
2. Yeni dosya aç (⌘+N)
3. Bir şey yaz
4. Kapat (⌘+W)
5. "Save?" dialog → Otomatik kapanmalı

**Senaryo 2: Claude Code Test**
1. Extension active
2. Claude Code'a sor: "List all Python files"
3. Bash command approval → Otomatik "Yes"
4. Activity Log'da görünmeli

**Senaryo 3: Multiple Dialogs**
1. Extension active
2. 3-4 farklı dialog oluştur
3. Hepsi otomatik kapanmalı
4. Activity Log'da hepsi görünmeli
5. Statistics: "Actions Today: 4"

---

## 🎨 Marketplace Hazırlığı (45 dk)

### 1. Logo Oluştur (15 dk)

**Gereksinim**: 128x128 PNG logo

**Seçenekler**:
- Online tool: https://www.canva.com/
- AI generator: DALL-E, Midjourney
- Basit: Sentry-AI yazısı + robot emoji

**Kaydet**:
```bash
# Logo'yu kopyala
cp ~/Downloads/logo.png vscode-extension/icon.png
```

### 2. README.md İyileştir (15 dk)

Screenshots ekle:
```bash
# Screenshots al:
# 1. Status panel
# 2. Activity log
# 3. Settings
# 4. Dialog automation (GIF)

mkdir -p vscode-extension/images
# Screenshot'ları images/ klasörüne koy
```

`README.md` güncelle:
```markdown
## Screenshots

### Status Panel
![Status](images/status.png)

### Activity Log
![Activity](images/activity.png)

### Demo
![Demo](images/demo.gif)
```

### 3. CHANGELOG.md Oluştur (5 dk)

```bash
cd vscode-extension
cat > CHANGELOG.md << 'EOF'
# Change Log

## [1.2.0] - 2025-11-03

### Added
- Initial release
- Vision AI dialog detection with Claude Opus 4
- Automatic keyboard automation (ENTER/ESCAPE)
- Activity log tracking in sidebar
- Statistics panel
- Status bar live indicator
- Command palette integration
- Webview status panel

### Features
- 🖥️ Computer Use with vision AI
- 🎹 Keyboard-first automation
- 📊 Real-time activity tracking
- ⚙️ Full VS Code integration

### Known Issues
- Activity log parsing needs testing
- Coordinate-based clicking disabled (using keyboard)

## Future Plans
- Multi-app support
- Custom automation rules
- Advanced statistics
EOF
```

### 4. package.json Final Check (10 dk)

```json
{
  "name": "sentry-ai",
  "displayName": "Sentry-AI",
  "description": "AI-powered automation assistant with vision AI - Never click dialogs again",
  "version": "1.2.0",
  "publisher": "TBD", // ← Azure DevOps'tan alınacak
  "icon": "icon.png",
  "repository": {
    "type": "git",
    "url": "https://github.com/lekesiz/Sentry-AI.git"
  },
  "bugs": {
    "url": "https://github.com/lekesiz/Sentry-AI/issues"
  },
  "license": "MIT"
}
```

---

## 📦 Paketleme ve Yayın (30 dk)

### 1. vsce Kur

```bash
npm install -g @vscode/vsce
```

### 2. Package Oluştur

```bash
cd vscode-extension
npm install
npm run compile
vsce package
```

**Kontrol**: `sentry-ai-1.2.0.vsix` dosyası oluştu mu?

### 3. Local Test

```bash
# VSIX'i yükle
code --install-extension sentry-ai-1.2.0.vsix

# Test et
code .
```

### 4. Azure DevOps Setup

**SADECE EĞER MARKETPLACE'E YÜKLEYECEKSEN**:

1. https://dev.azure.com/ → Hesap oluştur
2. Personal Access Token oluştur
3. Publisher oluştur: https://marketplace.visualstudio.com/manage
4. Token ile publish:

```bash
vsce publish -p <YOUR-PAT-TOKEN>
```

**Veya manuel**: VSIX'i web'den yükle

---

## 🎯 Başarı Kriterleri

Extension başarılı sayılır eğer:

- ✅ Extension başlatılıyor
- ✅ Sentry-AI process başlıyor
- ✅ Status "Active" oluyor
- ✅ Dialog otomatik kapanıyor (keyboard ile)
- ✅ Activity Log doluyorsa
- ✅ Statistics güncelleniyorsa
- ✅ Notification gösteriyorsa (opsiyonel)
- ✅ VSIX package oluşuyorsa
- ✅ Local install çalışıyorsa

---

## 📊 Timeline

| Zaman | Görev | Durum |
|-------|-------|-------|
| 09:00 - 09:30 | Extension test | ⏳ |
| 09:30 - 10:00 | Activity Log fix | ⏳ |
| 10:00 - 10:30 | End-to-end test | ⏳ |
| 10:30 - 11:15 | Marketplace hazırlık | ⏳ |
| 11:15 - 11:45 | Package + local test | ⏳ |
| 11:45 - 12:00 | Git commit + push | ⏳ |

**Toplam**: ~3 saat

---

## 💡 Önemli Notlar

### Extension Test İçin

1. **Her değişiklikten sonra**:
   - Extension'ı reload et (⌘+Shift+F5)
   - Veya: Stop → F5

2. **Debug Console**:
   - View → Debug Console
   - Extension log'larını göster

3. **Log Monitoring**:
```bash
tail -f sentry_ai.log | grep -E "keyboard|Successfully|Vision"
```

### Marketplace Yayını İçin

1. **İlk yayın**: Manuel approval gerekebilir (~1-2 saat)
2. **Güncellemeler**: Otomatik (~5-10 dakika)
3. **Private yayın**: VSIX dosyasını paylaş (marketplace'e gerek yok)

---

## 🔮 Opsiyonel (Zamanın Varsa)

### Icon İyileştirmeleri

Activity Log için custom icon'lar:
```typescript
// extension.ts
new vscode.ThemeIcon('check-all')    // Success
new vscode.ThemeIcon('keyboard')     // Keyboard action
new vscode.ThemeIcon('eye')          // Vision AI
```

### Settings Validation

```typescript
// Extension başlarken settings kontrol et
const sentryPath = config.get<string>('sentryPath');
if (!sentryPath || !fs.existsSync(sentryPath)) {
    vscode.window.showErrorMessage(
        'Please set Sentry-AI path in settings'
    );
}
```

### Error Handling

```typescript
// Sentry-AI crash olursa
sentryProcess.on('error', (error) => {
    logger.error(`Process error: ${error}`);
    vscode.window.showErrorMessage(
        `Sentry-AI failed: ${error.message}. Check logs.`
    );
});
```

---

## 📝 Final Checklist

Test öncesi:
- [ ] Tüm process'ler temizlendi
- [ ] Git commit'leri push edildi
- [ ] Extension compile edildi
- [ ] Dependencies yüklü

Test sırasında:
- [ ] Extension başlatıldı
- [ ] Dialog testi yapıldı
- [ ] Activity Log çalıştı
- [ ] Screenshot'lar alındı

Yayın öncesi:
- [ ] Logo eklendi
- [ ] README güncel
- [ ] CHANGELOG oluşturuldu
- [ ] VSIX test edildi
- [ ] Azure DevOps hazır (marketplace için)

Yayın sonrası:
- [ ] Git tag: `git tag v1.2.0 && git push --tags`
- [ ] GitHub release oluştur
- [ ] README'de marketplace badge ekle

---

**Başarılar! Yarın final stretch! 🚀**

**Next Session Başlangıç Komutu**:
```bash
cd /Users/mikail/Sentry-AI/vscode-extension
code .
# F5 bas → Test başlasın!
```
