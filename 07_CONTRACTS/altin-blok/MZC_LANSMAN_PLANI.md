# MZC COİN — 14 GÜNLÜK LANSMAN PLANI

## ◆ MİMAR KALKAN DAMGASI ◆
**Mimar:** Yonus KALKAN
**Proje:** mucizeWORK Ekosistemi — MZC Token
**Tarih:** 2026-04-29
**Hedef Lansman:** 2026-05-13

---

## 1. TOKEN ÖZETİ

| Özellik | Değer |
|---|---|
| **Token Adı** | MucizeCoin |
| **Sembol** | MZC |
| **Standart** | ERC-20 (tüm zincirler) |
| **Toplam Arz** | 1,000,000,000 MZC (1 Milyar) |
| **Başlangıç Fiyatı** | $0.01 |
| **Başlangıç Piyasa Değeri** | $10,000,000 (tam seyreltilmiş) |
| **Zincirler** | Ethereum, BNB Chain, HyperEVM, Base |

---

## 2. TOKENOMİCS — DAĞILIM

| Dilim | Oran | Miktar | Kilit Süresi |
|---|---|---|---|
| **Ekosistem & Topluluk** | 30% | 300,000,000 MZC | 12 ay vesting (aylık %8.33) |
| **Takım & Kurucu** | 20% | 200,000,000 MZC | 6 ay cliff + 18 ay vesting |
| **Likidite Havuzu (LP)** | 15% | 150,000,000 MZC | Kilitli (LP tokenlar yakılır) |
| **Yatırımcı / Presale** | 15% | 150,000,000 MZC | 3 ay cliff + 12 ay vesting |
| **Hazine (Treasury)** | 10% | 100,000,000 MZC | Multi-sig, DAO onaylı |
| **Pazarlama & Airdrop** | 5% | 50,000,000 MZC | İlk 6 ayda dağıtılır |
| **Danışmanlar** | 3% | 30,000,000 MZC | 6 ay cliff + 12 ay vesting |
| **Reserve** | 2% | 20,000,000 MZC | Acil durum fonu |

---

## 3. ZİNCİR STRATEJİSİ (Multi-Chain)

### Ana Zincir: Ethereum (ERC-20)
- Prestij ve güvenilirlik
- Uniswap V3 listing
- Kurumsal yatırımcılar için tercih

### İkincil Zincirler:
| Zincir | DEX | Neden |
|---|---|---|
| **BNB Chain** | PancakeSwap | Düşük fee, geniş kullanıcı tabanı |
| **HyperEVM** | HyperSwap | Kasa ekosistemi ile uyum |
| **Base** | Aerodrome | Coinbase ekosistemi, düşük fee |

### Köprüleme:
- **LayerZero OFT** veya **Wormhole** ile cross-chain token standardı
- Tek kontrat, tüm zincirlerde aynı token
- Alternatif: Her zincirde bağımsız deploy + resmi köprü

---

## 4. 14 GÜNLÜK TAKVİM

### ═══ GÜN 1 (29 Nisan) — Tokenomics Finalize ═══
- [ ] Tokenomics onayı (Mimar Kalkan)
- [ ] Toplam arz, dağılım, vesting kararları kesinleştir
- [ ] Hangi zincirde önce deploy edileceğine karar ver

### ═══ GÜN 2 (30 Nisan) — Smart Contract Geliştirme ═══
- [ ] ERC-20 kontratı yazılması (Solidity)
  - OpenZeppelin ERC-20 base
  - Mint/Burn yetkileri
  - Vesting kontratı (takım + yatırımcı kilitlileri)
  - Multi-sig owner (Gnosis Safe)
- [ ] Birim testleri (Hardhat/Foundry)

### ═══ GÜN 3 (1 Mayıs) — Testnet Deploy ═══
- [ ] Sepolia (Ethereum testnet) deploy
- [ ] BSC Testnet deploy
- [ ] Temel fonksiyon testleri (transfer, approve, mint)
- [ ] Vesting kontratı testi

### ═══ GÜN 4 (2 Mayıs) — Güvenlik Kontrolü ═══
- [ ] Slither (otomatik audit aracı) taraması
- [ ] Manuel kod incelemesi
- [ ] Reentrancy, overflow, access control kontrolleri
- [ ] (Opsiyonel) CertiK veya Hacken rapid audit başvurusu

### ═══ GÜN 5 (3 Mayıs) — Mainnet Deploy ═══
- [ ] Ethereum Mainnet deploy
- [ ] BNB Chain Mainnet deploy
- [ ] Base Mainnet deploy
- [ ] HyperEVM Mainnet deploy
- [ ] Kontrat verify (Etherscan, BscScan, Basescan)
- [ ] Multi-sig ownership transfer (Gnosis Safe)

### ═══ GÜN 6 (4 Mayıs) — Likidite & DEX Listing ═══
- [ ] Uniswap V3 LP oluştur (ETH/MZC)
  - Başlangıç likiditesi: $___K (Mimar Kalkan belirleyecek)
  - LP token yakma (kalıcı likidite)
- [ ] PancakeSwap LP (BNB/MZC)
- [ ] Aerodrome LP (Base)
- [ ] HyperSwap LP (HyperEVM)
- [ ] İlk fiyat: $0.01/MZC

### ═══ GÜN 7 (5 Mayıs) — Dashboard Entegrasyonu ═══
- [ ] wallet_dashboard.py'ye MZC paneli ekle
- [ ] Fiyat feed entegrasyonu (CoinGecko/DEXScreener)
- [ ] Holder sayısı takibi
- [ ] LP değeri gösterimi
- [ ] kasa_komuta_merkezi.py'ye MZC bölümü ekle

### ═══ GÜN 8 (6 Mayıs) — Website ═══
- [ ] Landing page tasarımı (dark theme, Mimar Kalkan damgalı)
  - Hero: Token adı + fiyat + satın alma butonu
  - Tokenomics bölümü (pasta grafik)
  - Yol haritası (roadmap)
  - Takım bölümü
  - Kontrat adresleri (tüm zincirler)
- [ ] Domain: mucizecoin.com veya mzc.network (karar verilecek)
- [ ] Deploy (Vercel/Netlify)

### ═══ GÜN 9 (7 Mayıs) — Whitepaper ═══
- [ ] Whitepaper yazımı (10-15 sayfa)
  - Vizyon & Misyon
  - mucizeWORK ekosistem açıklaması
  - Tokenomics detayları
  - Teknik mimari
  - Yol haritası (6-12-24 ay)
  - Takım
- [ ] PDF tasarımı (Mimar Kalkan damgalı)
- [ ] Website'e yükle

### ═══ GÜN 10 (8 Mayıs) — Sosyal Medya Hazırlık ═══
- [ ] Twitter/X hesabı: @MucizeCoin
- [ ] Telegram grubu oluştur
- [ ] Discord sunucusu (opsiyonel)
- [ ] Logo & marka kiti hazırla
- [ ] Banner'lar (Twitter, Telegram, LinkedIn)

### ═══ GÜN 11 (9 Mayıs) — Topluluk Oluşturma ═══
- [ ] Telegram'da ilk duyuru
- [ ] Twitter'da tease kampanyası başlat
- [ ] Influencer outreach listesi hazırla
- [ ] Airdrop kampanyası planla (galxe.com veya zealy.io)

### ═══ GÜN 12 (10 Mayıs) — Pre-Launch Buzz ═══
- [ ] Binance Square makale yayınla
- [ ] LinkedIn duyuru yazısı
- [ ] Medium/Mirror blog post
- [ ] AMA (Ask Me Anything) duyurusu
- [ ] Countdown başlat

### ═══ GÜN 13 (11 Mayıs) — Son Kontroller ═══
- [ ] Tüm kontratlar verify edildi mi? ✓
- [ ] LP'ler aktif mi? ✓
- [ ] Website çalışıyor mu? ✓
- [ ] Sosyal medya hazır mı? ✓
- [ ] Dashboard MZC paneli çalışıyor mu? ✓
- [ ] Whitepaper yayında mı? ✓
- [ ] Test alımı yap (küçük miktar)

### ═══ GÜN 14 (12 Mayıs) — LANSMAN GÜNÜ ═══
- [ ] Tüm sosyal medyalarda eş zamanlı duyuru
- [ ] DEX'lerde trading açık
- [ ] CoinGecko / CoinMarketCap listing başvurusu
- [ ] DEXScreener'da görünürlük
- [ ] Topluluk AMA gerçekleştir
- [ ] İlk 24 saat hacim ve fiyat takibi

---

## 5. LANSMAN SONRASI (Gün 15+)

| Hafta | Hedef |
|---|---|
| **Hafta 3** | CoinGecko listing onayı, ilk partnership duyuruları |
| **Hafta 4** | CEX (merkezi borsa) başvuruları (MEXC, Gate.io, Bitget) |
| **Ay 2** | Staking mekanizması açılışı |
| **Ay 3** | Governance (yönetişim) özelliği |
| **Ay 6** | Tier-2 borsa listingleri |
| **Yıl 1** | mucizeWORK ekosistem entegrasyonu tamamlanması |

---

## 6. GEREKLİ KAYNAKLAR

| Kaynak | Tahmini Maliyet |
|---|---|
| **Başlangıç Likiditesi** | $50K - $500K (Mimar Kalkan belirleyecek) |
| **Gas Fee (4 zincir deploy)** | ~$200-500 |
| **Domain** | ~$15/yıl |
| **Audit (opsiyonel)** | $2K-15K |
| **Logo/Marka Tasarım** | $0 (kendi yapacağız) |
| **Marketing budget** | Mimar Kalkan belirleyecek |

---

## 7. BEKLEYEN KARARLAR (MİMAR KALKAN ONAYI GEREKLİ)

- [ ] Toplam arz: 1 Milyar MZC doğru mu?
- [ ] Başlangıç fiyatı: $0.01 doğru mu?
- [ ] Başlangıç likiditesi: Ne kadar koyacaksın?
- [ ] Vesting süreleri uygun mu?
- [ ] Hangi zincirde önce başlayalım?
- [ ] Domain tercihi: mucizecoin.com? mzc.network?
- [ ] Cross-chain: LayerZero OFT mi yoksa bağımsız deploy mi?

---

**◆ MİMAR KALKAN DAMGASI ◆**
**Yonus KALKAN — mucizeWORK Ekosistemi**
**Lansman Hedefi: 12-13 Mayıs 2026**
