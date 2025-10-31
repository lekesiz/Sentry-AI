# 🛠️ Xcode Kurulum Rehberi - Sentry-AI

Bu rehber, Sentry-AI'nın macOS Accessibility API'sine erişebilmesi için gerekli olan **Xcode** kurulumunu açıklar.

---

## ❓ Neden Xcode Gerekli?

Sentry-AI, macOS'un **Accessibility API**'sini kullanarak:
- Uygulama pencerelerini algılar
- Dialogları okur
- Butonlara tıklar
- Metin girer

Bu API'ye erişmek için **PyObjC** kütüphanesi gereklidir ve PyObjC'nin derlenmesi için **Xcode** gerekir.

---

## 📋 Gereksinimler

| Gereksinim | Durum |
|------------|-------|
| **macOS** | 12.0+ (Monterey veya üstü) |
| **Disk Alanı** | ~15 GB boş alan |
| **İnternet** | Hızlı bağlantı (8+ GB indirme) |
| **Süre** | 30-60 dakika |

---

## 🚀 Kurulum Adımları

### Adım 1: Mevcut Durumu Kontrol Edin

Terminalinizi açın ve şu komutu çalıştırın:

```bash
xcode-select -p
```

**Sonuç 1:** `/Applications/Xcode.app/Contents/Developer`
- ✅ Xcode zaten kurulu! [Adım 4'e](#adım-4-xcode-lisansını-kabul-edin) geçin.

**Sonuç 2:** `/Library/Developer/CommandLineTools`
- ⚠️ Sadece Command Line Tools kurulu. Tam Xcode gerekli.

**Sonuç 3:** `xcode-select: error: unable to get active developer directory`
- ❌ Hiçbir şey kurulu değil.

---

### Adım 2: Xcode'u İndirin ve Kurun

#### Seçenek A: App Store'dan (Önerilen)

1. **App Store'u açın**
   - Dock'taki App Store ikonuna tıklayın
   - Veya Spotlight'ta (Cmd+Space) "App Store" yazın

2. **Xcode'u arayın**
   - Arama çubuğuna "Xcode" yazın
   - İlk sonuç Apple'ın resmi Xcode uygulaması olmalı

3. **İndirin ve kurun**
   - "GET" veya "İndir" butonuna tıklayın
   - Apple ID şifrenizi girin
   - İndirme başlayacak (~8-12 GB)
   - Kurulum otomatik olarak yapılacak

4. **Bekleyin**
   - İndirme süresi: 10-30 dakika (internet hızınıza bağlı)
   - Kurulum süresi: 5-10 dakika

#### Seçenek B: Apple Developer Sitesinden

1. **Apple Developer sayfasına gidin**
   ```
   https://developer.apple.com/download/all/
   ```

2. **Apple ID ile giriş yapın**
   - Ücretsiz bir Apple Developer hesabı yeterli

3. **Xcode'u bulun**
   - "Xcode" araması yapın
   - En son stable versiyonu seçin (örn: Xcode 15.x)

4. **İndirin**
   - `.xip` dosyasını indirin (~8-12 GB)
   - İndirme tamamlandığında dosyaya çift tıklayın
   - Otomatik olarak açılacak ve Applications klasörüne taşınacak

---

### Adım 3: Xcode'u İlk Kez Açın

1. **Xcode'u başlatın**
   ```bash
   open /Applications/Xcode.app
   ```
   
   Veya:
   - Spotlight'ta (Cmd+Space) "Xcode" yazın
   - Applications klasöründen Xcode'u çift tıklayın

2. **İlk açılış**
   - "Install additional required components?" diyalogu çıkacak
   - **"Install"** butonuna tıklayın
   - Şifrenizi girin
   - Ek bileşenler kurulacak (5-10 dakika)

3. **Xcode'u kapatın**
   - Kurulum tamamlandıktan sonra Xcode'u kapatabilirsiniz
   - Sentry-AI için Xcode'u açık tutmanıza gerek yok

---

### Adım 4: Xcode Lisansını Kabul Edin

Terminal'de şu komutu çalıştırın:

```bash
sudo xcodebuild -license accept
```

- Şifrenizi girin
- Lisans kabul edilecek

---

### Adım 5: Command Line Tools'u Yapılandırın

Xcode'un command line tools'larını aktif edin:

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

Doğrulayın:

```bash
xcode-select -p
```

**Beklenen çıktı:**
```
/Applications/Xcode.app/Contents/Developer
```

---

### Adım 6: Kurulumu Test Edin

Xcode'un düzgün çalıştığını test edin:

```bash
xcodebuild -version
```

**Beklenen çıktı:**
```
Xcode 15.4
Build version 15F31d
```

(Versiyon numaraları farklı olabilir)

---

## ✅ Kurulum Tamamlandı!

Artık Sentry-AI'yı kurabilirsiniz:

```bash
cd ~/Sentry-AI
./setup.sh
```

Veya manuel kurulum:

```bash
cd ~/Sentry-AI
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🐛 Sorun Giderme

### Hata: "xcode-select: error: tool 'xcodebuild' requires Xcode"

**Çözüm:**
- Xcode tam olarak kurulmamış olabilir
- [Adım 2](#adım-2-xcodeu-indirin-ve-kurun)'yi tekrar uygulayın
- Xcode'u en az bir kez açtığınızdan emin olun

### Hata: "xcrun: error: invalid active developer path"

**Çözüm:**
```bash
sudo xcode-select --reset
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

### Hata: "You have not agreed to the Xcode license agreements"

**Çözüm:**
```bash
sudo xcodebuild -license accept
```

### Hata: PyObjC hala derlenmiyor

**Çözüm 1: Python versiyonunu kontrol edin**
```bash
python3 --version
```

Python 3.13.7 kullanıyorsanız, requirements.txt'deki PyObjC versiyonu 10.3.1 olmalı.

**Çözüm 2: Homebrew ile yükleyin**
```bash
brew install python@3.12
cd ~/Sentry-AI
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Çözüm 3: PyObjC'yi ayrı yükleyin**
```bash
pip install --upgrade pip setuptools wheel
pip install pyobjc-core==10.3.1
pip install pyobjc-framework-Cocoa==10.3.1
pip install -r requirements.txt
```

---

## 💡 Alternatif: Xcode Olmadan Çalıştırma

Eğer Xcode kurmak istemiyorsanız, Sentry-AI'yı **sadece Browser API** ile kullanabilirsiniz:

### 1. requirements-minimal.txt Oluşturun

```bash
cd ~/Sentry-AI
cat > requirements-minimal.txt << 'EOF'
# Core Dependencies
fastapi==0.115.5
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.6.1

# AI/LLM Integration
ollama==0.4.4
google-genai==1.9.0
openai==1.57.2
anthropic==0.42.0

# Database
sqlalchemy==2.0.36
alembic==1.14.0

# Utilities
python-dotenv==1.0.1
loguru==0.7.2
pillow==11.0.0

# Testing
pytest==8.3.4
pytest-asyncio==0.24.0
EOF
```

### 2. Minimal Kurulum Yapın

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

### 3. Browser API Modunu Aktive Edin

`.env` dosyanızda:

```bash
# Accessibility API'yi devre dışı bırak
USE_ACCESSIBILITY_API=False

# Browser API'yi aktive et
USE_BROWSER_API=True
```

**Avantajlar:**
- ✅ Xcode gerekmez
- ✅ Daha hızlı kurulum
- ✅ VS Code web (vscode.dev, github.dev) ile çalışır

**Dezavantajlar:**
- ❌ Native macOS uygulamaları ile çalışmaz
- ❌ Sadece browser-based VS Code desteklenir

---

## 📞 Yardım

Hala sorun yaşıyorsanız:

1. **GitHub Issues**: [github.com/lekesiz/Sentry-AI/issues](https://github.com/lekesiz/Sentry-AI/issues)
2. **Hata loglarını paylaşın**: Kurulum sırasında aldığınız hata mesajlarını kopyalayın
3. **Sistem bilgilerinizi ekleyin**:
   ```bash
   sw_vers
   python3 --version
   xcode-select -p
   ```

---

## 📚 Ek Kaynaklar

- **Apple Developer Documentation**: [developer.apple.com/xcode](https://developer.apple.com/xcode/)
- **PyObjC Documentation**: [pyobjc.readthedocs.io](https://pyobjc.readthedocs.io/)
- **Sentry-AI Documentation**: [github.com/lekesiz/Sentry-AI/docs](https://github.com/lekesiz/Sentry-AI/tree/main/docs)

---

**Son güncelleme:** 31 Ekim 2025  
**Python desteği:** 3.11, 3.12, 3.13  
**macOS desteği:** 12.0+ (Monterey, Ventura, Sonoma, Sequoia)
