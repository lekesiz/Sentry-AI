# 🚀 VS Code Extension Yayınlama Kılavuzu

Bu kılavuz Sentry-AI extension'ını VS Code Marketplace'e yayınlamak için adım adım talimatları içerir.

---

## 📋 Ön Hazırlık

### 1. Microsoft Azure DevOps Hesabı

VS Code Marketplace, Azure DevOps üzerinden yönetiliyor.

1. **Azure DevOps'a git**: https://dev.azure.com/
2. **Microsoft hesabınla giriş yap** (ücretsiz)
3. **Organizasyon oluştur** (örn: "sentry-ai-publisher")

### 2. Personal Access Token (PAT) Oluştur

1. Azure DevOps'ta: **User Settings** → **Personal Access Tokens**
2. **New Token** butonuna tıkla
3. Ayarlar:
   - **Name**: `vscode-marketplace-publisher`
   - **Organization**: `All accessible organizations`
   - **Expiration**: 90 days (veya Custom)
   - **Scopes**:
     - ✅ **Marketplace** → **Manage** (önemli!)
4. **Create** butonuna bas
5. ⚠️ **Token'ı kaydet!** (bir daha göremezsin)

Örnek token:
```
abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqr
```

### 3. Publisher Hesabı Oluştur

1. **Visual Studio Marketplace'e git**: https://marketplace.visualstudio.com/manage
2. **Microsoft hesabınla giriş yap**
3. **Create publisher** butonuna tıkla
4. Bilgileri doldur:
   - **Name**: `sentry-ai` (benzersiz olmalı)
   - **ID**: `sentry-ai` (küçük harf, tire allowed)
   - **Display Name**: `Sentry-AI`
   - **Description**: `AI-powered automation for VS Code`
   - **Website**: `https://github.com/lekesiz/Sentry-AI`
   - **Email**: `your-email@example.com`

---

## 🔧 Extension Hazırlama

### 1. package.json Güncelle

```bash
cd /Users/mikail/Sentry-AI/vscode-extension
```

`package.json` dosyasını düzenle:

```json
{
  "name": "sentry-ai",
  "displayName": "Sentry-AI",
  "description": "AI-powered automation assistant for VS Code with vision AI",
  "version": "1.2.0",
  "publisher": "sentry-ai",  // ← Publisher ID'nizi buraya
  "icon": "icon.png",        // ← Logo ekle (128x128 PNG)
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": [
    "Other",
    "Machine Learning",
    "Productivity"
  ],
  "keywords": [
    "ai",
    "automation",
    "assistant",
    "claude",
    "vision",
    "productivity",
    "dialog automation"
  ],
  "repository": {
    "type": "git",
    "url": "https://github.com/lekesiz/Sentry-AI.git"
  },
  "bugs": {
    "url": "https://github.com/lekesiz/Sentry-AI/issues"
  },
  "homepage": "https://github.com/lekesiz/Sentry-AI#readme",
  "license": "MIT"
}
```

### 2. Logo Ekle

Extension için 128x128 PNG logo gerekli:

```bash
# Logo'yu buraya kopyala:
cp /path/to/logo.png vscode-extension/icon.png
```

**Logo Gereksinimleri**:
- Format: PNG
- Boyut: 128x128 pixels
- Şeffaf arka plan (önerilen)

### 3. README.md İyileştir

Extension'ın marketplace sayfasında görünecek:

```markdown
# Sentry-AI

AI-powered automation assistant for VS Code. Automatically handles dialogs with vision AI.

## Features

- 🖥️ **Vision AI**: Claude Opus 4 sees your screen
- 🤖 **Auto Dialog Handling**: Never click "Yes" again
- 📊 **Activity Tracking**: See all automated actions
- ⚙️ **Full Control**: Start, stop, configure from VS Code

## Installation

1. Install the extension
2. Configure Sentry-AI path in settings
3. Start automation from Command Palette

## Quick Start

⌘+Shift+P → "Sentry-AI: Start Automation"

## Requirements

- Python 3.9+
- Sentry-AI installed

For more information, visit: https://github.com/lekesiz/Sentry-AI
```

### 4. CHANGELOG.md Oluştur

```bash
cat > CHANGELOG.md << 'EOF'
# Change Log

## [1.2.0] - 2025-11-02

### Added
- Initial release
- Vision AI dialog detection
- Automatic keyboard automation
- Activity log tracking
- Statistics panel
- Status bar indicator

### Fixed
- venv Python path detection

### Known Issues
- Activity log parsing needs improvement
EOF
```

### 5. LICENSE Ekle

```bash
# MIT License ekle (eğer yoksa)
cp ../LICENSE LICENSE 2>/dev/null || cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Sentry-AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

---

## 📦 Extension Paketleme

### 1. vsce Yükle

```bash
npm install -g @vscode/vsce
```

### 2. Dependencies Kontrol

```bash
cd vscode-extension
npm install
npm run compile
```

### 3. .vscodeignore Düzenle

Gereksiz dosyaları exclude et:

```
.vscode/**
.vscode-test/**
src/**
.gitignore
.yarnrc
vsc-extension-quickstart.md
**/tsconfig.json
**/.eslintrc.json
**/*.map
**/*.ts
node_modules/**
.DS_Store
```

### 4. Package Oluştur

```bash
vsce package
```

Bu komut `sentry-ai-1.2.0.vsix` dosyası oluşturur.

**Kontrol Adımları**:
1. ✅ VSIX dosyası oluştu mu?
2. ✅ Boyut makul mü? (~500KB - 2MB arası)
3. ✅ Hata mesajı yok mu?

---

## 🌐 Marketplace'e Yayınlama

### Yöntem 1: Web UI (Kolay)

1. **Marketplace yönetim sayfasına git**: https://marketplace.visualstudio.com/manage
2. **Publisher'ı seç**: `sentry-ai`
3. **New extension** butonuna tıkla
4. **Upload** ile `sentry-ai-1.2.0.vsix` yükle
5. Bilgileri kontrol et
6. **Publish** butonuna bas

### Yöntem 2: CLI (Hızlı)

```bash
# Token ile login
vsce login sentry-ai

# Token'ı yapıştır (Azure DevOps PAT)
# Paste token: abcdefghijklmnopqrstuvwxyz1234567890...

# Yayınla
vsce publish
```

**Alternatif**: Direkt publish (login + publish):

```bash
vsce publish -p <your-PAT-token>
```

---

## ✅ Yayın Sonrası

### 1. Extension Sayfası

Extension yayınlandıktan sonra:
- **URL**: `https://marketplace.visualstudio.com/items?itemName=sentry-ai.sentry-ai`
- **Görünür olması**: ~5-10 dakika
- **Arama sonuçları**: ~1 saat

### 2. VS Code'dan Kurulum

Kullanıcılar şu şekilde kurabilir:

```
VS Code → Extensions (⌘+Shift+X)
→ "Sentry-AI" ara
→ Install butonuna tıkla
```

Veya:

```bash
code --install-extension sentry-ai.sentry-ai
```

### 3. Güncelleme Yayınlama

Yeni versiyon için:

```bash
# Version'ı güncelle
npm version patch  # 1.2.0 → 1.2.1
# veya
npm version minor  # 1.2.0 → 1.3.0

# Tekrar yayınla
vsce publish
```

---

## 🎨 Marketplace Sayfası Optimize Etme

### README.md İçin İpuçları

1. **Screenshots Ekle**:
```markdown
## Screenshots

![Status Panel](images/status-panel.png)
![Activity Log](images/activity-log.png)
![Settings](images/settings.png)
```

2. **GIF Demo**:
```markdown
## Demo

![Sentry-AI in action](images/demo.gif)
```

3. **Badges Ekle**:
```markdown
[![Version](https://img.shields.io/visual-studio-marketplace/v/sentry-ai.sentry-ai)](https://marketplace.visualstudio.com/items?itemName=sentry-ai.sentry-ai)
[![Installs](https://img.shields.io/visual-studio-marketplace/i/sentry-ai.sentry-ai)](https://marketplace.visualstudio.com/items?itemName=sentry-ai.sentry-ai)
[![Rating](https://img.shields.io/visual-studio-marketplace/r/sentry-ai.sentry-ai)](https://marketplace.visualstudio.com/items?itemName=sentry-ai.sentry-ai)
```

### Gallery Banner (Opsiyonel)

`package.json`'a ekle:

```json
{
  "galleryBanner": {
    "color": "#1e1e1e",
    "theme": "dark"
  }
}
```

---

## 🐛 Sorun Giderme

### Hata: "Publisher not found"

```bash
# Publisher oluştur:
vsce create-publisher sentry-ai
```

### Hata: "ENOENT: icon.png not found"

```bash
# package.json'dan icon satırını kaldır veya logo ekle
# "icon": "icon.png",  ← Bu satırı sil
```

### Hata: "Invalid version"

```bash
# package.json'da version formatı doğru olmalı
"version": "1.2.0"  // ✅ Doğru
"version": "v1.2.0" // ❌ Yanlış
```

### Hata: "Personal access token is invalid"

1. Token'ın expire olmadığından emin ol
2. Scope'ların doğru olduğundan emin ol (Marketplace → Manage)
3. Yeni token oluştur

---

## 📊 İstatistikler Takibi

### Marketplace İstatistikleri

https://marketplace.visualstudio.com/manage adresinden:
- **Installs**: Kaç kez kuruldu
- **Downloads**: Kaç kez indirildi
- **Rating**: Kullanıcı puanı
- **Reviews**: Yorumlar

### Analytics (Opsiyonel)

Google Analytics ekleyebilirsin:

`package.json`'a:
```json
{
  "bugs": {
    "url": "https://github.com/lekesiz/Sentry-AI/issues?utm_source=vscode&utm_medium=extension"
  }
}
```

---

## 🎯 Best Practices

### 1. Versiyonlama (Semantic Versioning)

- `1.0.0` → İlk release
- `1.0.1` → Bug fix
- `1.1.0` → Yeni özellik (backward compatible)
- `2.0.0` → Breaking change

### 2. Release Notes

Her release için CHANGELOG.md güncelle:

```markdown
## [1.2.1] - 2025-11-03

### Fixed
- Activity log parsing improved
- Dialog detection accuracy

### Changed
- Keyboard shortcuts now default
```

### 3. Testing

Yayınlamadan önce:

```bash
# Local test
code --extensionDevelopmentPath=/Users/mikail/Sentry-AI/vscode-extension

# VSIX test
code --install-extension sentry-ai-1.2.0.vsix
```

### 4. User Feedback

- GitHub Issues'i aktif tut
- Marketplace reviews'ları yanıtla
- Community feedback'i dinle

---

## 🚀 Hızlı Başlangıç Komutları

```bash
# 1. Hazırlık
cd vscode-extension
npm install
npm run compile

# 2. vsce kur
npm install -g @vscode/vsce

# 3. Package oluştur
vsce package

# 4. Test et
code --install-extension sentry-ai-1.2.0.vsix

# 5. Yayınla
vsce publish -p <YOUR-PAT-TOKEN>

# Veya interaktif
vsce login sentry-ai
vsce publish
```

---

## 📚 Kaynaklar

- **VS Code Extension Docs**: https://code.visualstudio.com/api
- **Publishing Guide**: https://code.visualstudio.com/api/working-with-extensions/publishing-extension
- **Marketplace**: https://marketplace.visualstudio.com/
- **vsce CLI**: https://github.com/microsoft/vsce

---

## ✅ Checklist

Yayınlamadan önce:

- [ ] `package.json` güncel (publisher, version, repository)
- [ ] `README.md` detaylı ve screenshots var
- [ ] `CHANGELOG.md` oluşturuldu
- [ ] `LICENSE` dosyası var
- [ ] `icon.png` eklendi (128x128)
- [ ] `.vscodeignore` düzenlendi
- [ ] `npm run compile` başarılı
- [ ] `vsce package` çalışıyor
- [ ] VSIX local test edildi
- [ ] Azure DevOps PAT oluşturuldu
- [ ] Publisher hesabı hazır
- [ ] `vsce publish` başarılı

---

**Başarılar! 🎉**

Extension'ınız yayınlandıktan sonra:
`https://marketplace.visualstudio.com/items?itemName=sentry-ai.sentry-ai`
