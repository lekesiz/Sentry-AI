# VS Code Simple Mode - Kullanım Kılavuzu

## 📌 Özet

Sentry-AI artık **sadece Visual Studio Code** için optimize edilmiş, basit otomatik onay modunda çalışıyor.

### Ne Yapar?

✅ Claude Code'un sorduğu sorulara otomatik "Evet" der
✅ Claude'un bash komutlarını otomatik onaylar
✅ Claude'un edit isteklerini otomatik kabul eder
✅ Claude'un sorularına basit yanıtlar üretir
❌ Diğer tüm uygulamaları ignore eder (sadece VS Code)

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

Bağımlılıklar yüklü değilse:
```bash
pip install -r requirements.txt
```

### 2. Başlatma

**Terminal ile:**
```bash
make run
```

**Menu Bar UI ile:**
```bash
make menubar
# Sonra menu bar'dan "Start Sentry-AI"
```

### 3. VS Code'da Test Et

1. VS Code'u aç
2. Claude Code extension'ı başlat
3. Claude'a bir görev ver, örneğin:
   ```
   "Create a simple Hello World Python script"
   ```
4. Claude bir dialog gösterdiğinde Sentry-AI otomatik olarak "Yes" tıklayacak
5. İşlem loglarını görmek için:
   ```bash
   tail -f sentry_ai.log
   ```

---

## ⚙️ Konfigürasyon

`.env` dosyasındaki ayarlar:

```bash
# SADECE VS Code otomatize edilir
WHITELIST_APPS=["Visual Studio Code","Code"]

# Diğer tüm uygulamalar engellendi
BLACKLIST_APPS=["Terminal","iTerm","Keychain Access",...tüm liste]

# Basit mod aktif (her zaman evet)
VSCODE_SIMPLE_MODE=True

# Event-driven mode (performans için)
EVENT_DRIVEN_MODE=True
```

---

## 🎯 Davranış Özellikleri

### Otomatik Onaylanan Durumlar

| Dialog Tipi | Sentry-AI Yanıtı | Örnek |
|-------------|------------------|-------|
| Bash komut onayı | "Yes" | "Allow this bash command?" → Yes |
| Edit isteği | "Yes" | "Allow editing this file?" → Yes |
| Soru | Basit yanıt | "What file name?" → "output.txt" |
| Genel dialog | İlk "Yes" seçeneği | Herhangi bir dialog → Yes |

### Güvenlik

- **Güvenlik kontrolü YOK:** `VSCODE_SIMPLE_MODE=True` olduğunda TÜM komutlar otomatik onaylanır
- **Sadece VS Code:** Diğer uygulamalar tamamen ignore edilir
- **Tehlikeli komutlar bile onaylanır:** `rm -rf` bile "Yes" alır (dikkatli ol!)

> ⚠️ **UYARI:** Bu mod sadece güvendiğin projeler ve Claude ile çalışırken kullanılmalı!

---

## 🔧 Gelişmiş Mod (Opsiyonel)

Güvenlik kontrolleri istiyorsan:

```bash
# .env dosyasında
VSCODE_SIMPLE_MODE=False
```

Bu durumda:
- Tehlikeli komutlar (`rm -rf`, `sudo`) otomatik REDDEDILIR
- Güvenli komutlar (`ls`, `cat`) otomatik ONAYLANIR
- Bilinmeyen komutlar kullanıcıya sorar

---

## 📊 Log İzleme

### Terminal'de Canlı Log

```bash
tail -f sentry_ai.log
```

### Önemli Log Mesajları

```
🎯 Using SIMPLE VS Code strategy (auto-approve everything)
✅ Auto-approving with: Yes
🤖 Simple answer: Yes, proceed
```

---

## 🐛 Sorun Giderme

### Sentry-AI Çalışmıyor

1. **Observer çalışıyor mu kontrol et:**
   ```bash
   # Log'da şunu ara:
   grep "Event-Driven Observer" sentry_ai.log
   ```

2. **VS Code tanınıyor mu:**
   ```bash
   # Accessibility permissions verilmiş mi kontrol et
   # System Preferences → Security & Privacy → Accessibility
   ```

3. **Whitelist doğru mu:**
   ```bash
   # .env dosyasında:
   WHITELIST_APPS=["Visual Studio Code","Code"]
   ```

### Dialog Otomatik Onaylanmıyor

1. **Doğru uygulama mı:**
   - Sadece "Visual Studio Code" veya "Code" çalışır
   - Terminal, TextEdit vs. ignore edilir

2. **Simple mode aktif mi:**
   ```bash
   grep "VSCODE_SIMPLE_MODE" .env
   # True olmalı
   ```

3. **Log'lara bak:**
   ```bash
   tail -f sentry_ai.log | grep "Simple"
   ```

### Performans Sorunları

1. **Event-driven mode aktif mi:**
   ```bash
   grep "EVENT_DRIVEN_MODE" .env
   # True olmalı
   ```

2. **CPU kullanımı:**
   ```bash
   # Activity Monitor'de "python" ara
   # %0-1 civarında olmalı (idle)
   ```

---

## 📚 Daha Fazla Bilgi

### Diğer Uygulamalar

Başka uygulamaları da eklemek istersen:

```bash
# .env dosyasında
WHITELIST_APPS=["Visual Studio Code","Code","iTerm"]
```

### Basit Moddan Çıkmak

```bash
# Güvenlik kontrolleri ile çalışmak için:
VSCODE_SIMPLE_MODE=False

# Ya da tüm uygulamaları aktif et:
WHITELIST_APPS=[]  # Boş liste = tüm uygulamalar (blacklist hariç)
```

### Tüm Özellikleri Aktif Et

Tüm iyileştirmeleri kullanmak istersen:

```bash
# .env dosyasında:
WHITELIST_APPS=[]  # Tüm uygulamalar
VSCODE_SIMPLE_MODE=False  # Gelişmiş stratejiler
EVENT_DRIVEN_MODE=True  # Performans
```

Sonra [IMPROVEMENTS_REPORT.md](IMPROVEMENTS_REPORT.md) dosyasına bak.

---

## 💡 İpuçları

1. **İlk test:** VS Code'da basit bir Python script yazdır Claude'a
2. **Log izle:** Başka terminalde `tail -f sentry_ai.log` çalıştır
3. **Menu bar kullan:** `make menubar` ile GUI'den kontrol et
4. **Otomatik başlatma:** Login Items'a ekle (macOS)

---

## ✅ Özet Checklist

Kurulum sonrası kontrol et:

- [ ] `pip install -r requirements.txt` çalıştırıldı
- [ ] `.env` dosyası düzenlendi
- [ ] `WHITELIST_APPS=["Visual Studio Code","Code"]` set edildi
- [ ] `VSCODE_SIMPLE_MODE=True` set edildi
- [ ] `make run` veya `make menubar` ile başlatıldı
- [ ] Accessibility permissions verildi
- [ ] VS Code + Claude Code ile test edildi
- [ ] Log'larda "✅ Auto-approving" görünüyor

---

**Version:** 1.1.0
**Mod:** VS Code Simple (Auto-Approve)
**Performans:** Event-Driven (~0% CPU)
**Güvenlik:** Düşük (tüm komutlar otomatik onay)

**Kullanmaya hazır!** 🚀
