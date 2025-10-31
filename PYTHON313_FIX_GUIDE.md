# 🐍 Python 3.13 Kurulum Sorunu Çözüldü!

## ✅ Ne Yapıldı?

Projeniz **Python 3.13.7** için tamamen optimize edildi ve kurulum sorunları giderildi.

---

## 🚀 Hızlı Test

Mac'inizde şu adımları izleyin:

### 1. Projeyi Güncelleyin

```bash
cd ~/Sentry-AI
git pull
```

### 2. Kurulumu Başlatın

```bash
./setup.sh
```

### 3. İki Seçenek Sunulacak

#### Seçenek A: Xcode Kurulumu (Tam Özellikler)

Eğer Xcode kurulu DEĞİLse, script size soracak:

```
⚠️  PyObjC installation failed
Would you like to continue with Browser API only? (y/n):
```

**"n" yazın** ve Xcode'u kurun:

1. **App Store'u açın**
2. **"Xcode" arayın**
3. **"İndir" butonuna tıklayın** (~8-12 GB, 30-60 dakika)
4. **İndirme tamamlandığında Xcode'u bir kez açın**
5. **"Install additional components" diyaloğunda "Install" tıklayın**
6. **Xcode'u kapatın**
7. **Terminal'de tekrar `./setup.sh` çalıştırın**

#### Seçenek B: Browser API Only (Xcode Gerekmez)

Eğer Xcode kurmak istemiyorsanız:

```
Would you like to continue with Browser API only? (y/n): y
```

**"y" yazın** ve kurulum devam edecek.

**Avantajlar:**
- ✅ Hızlı kurulum (5-10 dakika)
- ✅ VS Code web ile çalışır (vscode.dev, github.dev)

**Dezavantajlar:**
- ❌ Native macOS uygulamaları ile çalışmaz

---

## 📋 Kurulum Tamamlandıktan Sonra

### 1. Ollama'yı Başlatın

```bash
ollama serve
```

Yeni bir terminal açın:

```bash
ollama pull phi3:mini
```

### 2. .env Dosyasını Yapılandırın

```bash
cd ~/Sentry-AI
nano .env
```

LLM provider seçin (Gemini öneriyorum):

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

### 3. Sentry-AI'yı Çalıştırın

```bash
make run
```

---

## 🎯 Test Senaryosu

### VS Code Web ile Test (Xcode Gerekmez)

1. **vscode.dev'i açın**
2. **GitHub'dan bir proje açın**
3. **Claude Code eklentisini kullanın**
4. **Sentry-AI otomatik olarak dialogları yönetecek**

### Native macOS ile Test (Xcode Gerekli)

1. **TextEdit'i açın**
2. **Bir şeyler yazın**
3. **Cmd+W ile kapatmaya çalışın**
4. **Sentry-AI "Save" dialogunu otomatik yönetecek**

---

## 🔧 Sorun Giderme

### Hata: "xcode-select: error: tool 'xcodebuild' requires Xcode"

**Çözüm:** [XCODE_SETUP.md](XCODE_SETUP.md) dosyasına bakın.

### Hata: "Module 'pyobjc' not found"

**Çözüm 1:** Xcode'u kurun ve `./setup.sh` tekrar çalıştırın.

**Çözüm 2:** Browser API only mode kullanın:

```bash
# .env dosyasında
USE_ACCESSIBILITY_API=False
USE_BROWSER_API=True
```

### Hata: "Permission denied: ./setup.sh"

**Çözüm:**

```bash
chmod +x setup.sh
./setup.sh
```

---

## 📊 Değişiklikler

| Dosya | Değişiklik |
|-------|------------|
| `requirements.txt` | Tüm paketler Python 3.13 için güncellendi |
| `setup.sh` | Geliştirilmiş hata yönetimi eklendi |
| `XCODE_SETUP.md` | Yeni: Detaylı Xcode kurulum rehberi |

---

## 💡 Öneriler

### Tam Özellikler İstiyorsanız

1. **Xcode'u kurun** (App Store'dan, ücretsiz)
2. **`./setup.sh` çalıştırın**
3. **Accessibility izinlerini verin**
4. **Hem native hem web uygulamaları ile çalışın**

### Hızlı Başlangıç İstiyorsanız

1. **`./setup.sh` çalıştırın**
2. **"y" seçin** (Browser API only)
3. **VS Code web ile test edin**
4. **İsterseniz sonra Xcode kurabilirsiniz**

---

## 📞 Yardım

Hala sorun mu yaşıyorsunuz?

1. **Hata mesajını kopyalayın**
2. **Sistem bilgilerinizi toplayın:**
   ```bash
   sw_vers
   python3 --version
   xcode-select -p
   ```
3. **GitHub Issues'da paylaşın:** [github.com/lekesiz/Sentry-AI/issues](https://github.com/lekesiz/Sentry-AI/issues)

---

**Güncelleme:** 31 Ekim 2025  
**Python:** 3.13.7 ✅  
**macOS:** 12.0+ ✅  
**Xcode:** Opsiyonel (Browser API için gerekmez) ✅
