# QR Payment Solution for Starknet Wallets Without Built-in Scanners

**Date:** 2026-02-05
**Author:** OpenClaw Subagent
**Status:** Design Complete

---

## Executive Summary

This document analyzes QR payment solutions for Starknet wallets (Ready, Braavos) that lack built-in QR scanning capabilities. After evaluating three options against security, UX, compatibility, and standards requirements, **Option 2 (Web-based Scanner with Deep Link Fallback)** emerges as the recommended solution, with **Option 1 (Deep Links + External Scanner)** serving as a complementary approach.

---

## 1. Problem Statement

Ready and Braavos wallets on Starknet do not have native QR code scanners. This creates friction for:
- **Point-of-sale payments** at merchants displaying QR codes
- **P2P transfers** where users want to scan each other's payment requests
- **dApp interactions** requiring wallet connections via QR

Users currently must manually copy-paste addresses, increasing error risk and reducing usability.

---

## 2. Starknet URI Scheme Background

The Starknet ecosystem uses the `starknet:` URI scheme (inspired by ERC-681/ERC-831 for Ethereum):

```
starknet:<address>@<chain_id>/<function>?param1=value1&param2=value2
```

**Example transfer URI:**
```
starknet:0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7@0x534e5f474f45524c49/transfer?address=0x123456789abcdef&uint256=2e-2
```

**Key Parameters:**
- `target_address`: Recipient contract address (required)
- `chain_id`: Network identifier (hex encoded)
  - Mainnet: `0x534e5f4d41494e`
  - Goerli: `0x534e5f474f45524c49`
  - Goerli2: `0x534e5f474f45524c4932`
- `function_name`: Action type (transfer, dapp, watchAsset, etc.)
- `parameters`: Additional query params (amount, token address, etc.)

**Library Support:**
- `starknet-url` (npm): Build and parse Starknet URIs
- `starknet-deeplink` (npm): Generate payment deep links
- `get-starknet`: Wallet-dApp bridge with multi-wallet support

---

## 3. Solution Analysis

### Option 1: Deep Links + External Scanner

**Mechanism:**
1. Merchant/Payee displays QR containing `starknet:<addr>?amount=...`
2. User scans QR using phone's native camera app
3. Camera app detects deep link and opens user's wallet
4. Wallet pre-fills payment details for confirmation

**Technical Flow:**
```
QR Code → Phone Camera → Deep Link Detection → Wallet App → Pre-filled Transfer
```

#### Pros:
- ✅ **Universal compatibility** - All modern phones can scan QR codes
- ✅ **Native UX** - No additional app installation required
- ✅ **Security** - No intermediary; direct wallet communication
- ✅ **Works offline** - QR can be scanned without internet
- ✅ **Simple implementation** - Leverages existing phone capabilities
- ✅ **Standards-compliant** - Uses established `starknet:` URI scheme

#### Cons:
- ⚠️ **Camera app dependency** - Behavior varies by phone/OS
- ⚠️ **No wallet selector** - Opens default wallet; can't choose alternative
- ⚠️ **Trust verification** - Users can't verify recipient before scanning
- ⚠️ **QR tampering risk** - Physical QR codes can be overlaid/masked
- ⚠️ **Desktop limitation** - Doesn't work on computers without cameras

#### Implementation Requirements:
```javascript
// Generate QR with starknet URI
import { transfer } from 'starknet-url'

const qrContent = transfer(recipientAddress, {
  token: { token_address: ETH_ADDRESS, chainId: StarknetChainId.MAINNET },
  amount: 0.01
})

// QR Code generation (using qrcode library)
const qrCode = await QRCode.toDataURL(qrContent)
```

---

### Option 2: Web-based Scanner (RECOMMENDED)

**Mechanism:**
1. Mini-Pay hosts a web scanner page (e.g., `minipay.io/scan`)
2. User visits URL in wallet's in-app browser or external browser
3. Grants camera permissions for web-based scanner
4. Scans QR code on screen
5. Click "Open in Wallet" button to trigger deep link

**Technical Flow:**
```
Web Scanner → Camera Permission → QR Detection → Deep Link → Wallet App
```

#### Pros:
- ✅ **Full UX control** - Custom UI with recipient verification
- ✅ **Chain verification** - Can warn if wrong network
- ✅ **Amount preview** - Show transfer details before opening wallet
- ✅ **Multi-wallet selector** - Choose which wallet to open
- ✅ **Accessibility** - Works with screen readers, zoom, etc.
- ✅ **Progressive enhancement** - Works without camera via manual URI entry
- ✅ **Analytics** - Track usage patterns (opt-in, privacy-respecting)

#### Cons:
- ⚠️ **Requires internet** - Must load web page first
- ⚠️ **Camera permission** - Browser permissions can be confusing
- ⚠️ **Trust dependency** - Users must trust the scanning domain
- ⚠️ **Added friction** - Extra step vs. native camera scan

#### Implementation Requirements:
```javascript
// Web Scanner using html5-qrcode library
import { Html5QrcodeScanner } from "html5-qrcode"

const scanner = new Html5QrcodeScanner(
  "reader",
  { fps: 10, qrbox: { width: 250, height: 250 } },
  /* verbose= */ false
)

scanner.render(onScanSuccess, onScanFailure)

function onScanSuccess(decodedText) {
  // Verify starknet: URI format
  if (decodedText.startsWith('starknet:')) {
    showConfirmationUI(decodedText)
  }
}

function openInWallet(uri) {
  window.location.href = uri  // Triggers deep link
}
```

**Web Scanner UI Design:**
```
┌─────────────────────────────────┐
│  Starknet QR Scanner            │
├─────────────────────────────────┤
│  ┌───────────────────────────┐  │
│  │     [ Camera View ]      │  │
│  │        ▢▢▢▢▢             │  │
│  │        ▢▢▢▢▢             │  │
│  │        ▢▢▢▢▢             │  │
│  └───────────────────────────┘  │
│                                 │
│  Point camera at QR code        │
├─────────────────────────────────┤
│  [ Cancel ]                     │
└─────────────────────────────────┘
```

After successful scan:
```
┌─────────────────────────────────┐
│  Payment Request Detected       │
├─────────────────────────────────┐
│  To: 0x049d...4dc7              │
│  Amount: 0.01 ETH               │
│  Network: Starknet Mainnet      │
├─────────────────────────────────┤
│  [ ⚠️ Verify recipient before ] │
│  [      sending funds           ]│
├─────────────────────────────────┤
│  [ Open in Braavos ]            │
│  [ Open in Argent X ]           │
│  [ Open in Ready ]              │
│  [ Copy Address ]               │
└─────────────────────────────────┘
```

---

### Option 3: Camera Intent (Android)

**Mechanism:**
1. QR contains `intent://` URL with Starknet deep link
2. Android system opens camera to scan
3. After scan, system routes to appropriate wallet app
4. Payment pre-filled in wallet

**URI Format:**
```
intent://scan#Intent;scheme=starknet;package=com.braavos.app;end
```

#### Pros:
- ✅ **Native Android integration** - System-level support
- ✅ **App picker** - User can select wallet from installed options
- ✅ **Offline scanning** - Android intent works without internet
- ✅ **Fallback handling** - Can specify fallback URL

#### Cons:
- ⚠️ **Android-only** - No iOS equivalent
- ⚠️ **Fragmented behavior** - Different Android versions behave differently
- ⚠️ **Complexity** - Requires Android intent handling expertise
- ⚠️ **Limited to Android users** - Excludes iOS/browser extension users

---

## 4. Comparative Analysis

| Criteria | Option 1 (Deep Links) | Option 2 (Web Scanner) | Option 3 (Android Intent) |
|----------|---------------------|------------------------|--------------------------|
| **Security** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **User Experience** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Compatibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Standards Compliance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Implementation Effort** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Offline Capability** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| **Cost** | Free | Medium | Low |

---

## 5. Recommended Solution: Hybrid Approach

**Primary:** Web-based Scanner (Option 2)
**Fallback:** Deep Links + External Scanner (Option 1)

### Why This Hybrid?

1. **Web Scanner handles complex cases:**
   - Merchant environments with displays
   - Screenshots/images of QR codes
   - Multi-wallet selection
   - Recipient verification UI

2. **Deep Links handle edge cases:**
   - Offline scenarios
   - Users without web access
   - Native camera convenience
   - dApp connections

### Implementation Roadmap

```
Phase 1: Core Infrastructure
├── starknet-url library integration
├── QR code generator utilities
└── Deep link handler registration

Phase 2: Web Scanner
├── Host scanner page (minipay.io/scan)
├── Implement camera access (html5-qrcode)
├── Build confirmation UI
└── Add multi-wallet selection

Phase 3: Progressive Enhancement
├── Manual URI input fallback
├── QR image upload support
└── Address book integration

Phase 4: Security Hardening
├── Tampering detection
├── Phishing warnings
├── Transaction simulation
└── Audit logging
```

---

## 6. Technical Implementation

### QR Code Generation (Merchant Side)

```javascript
const starknet = require('starknet-url')
const QRCode = require('qrcode')

async function generatePaymentQR(recipient, amount, token = 'ETH') {
  const tokenAddresses = {
    ETH: '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7',
    STRK: '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4297c7d2',
    USDC: '0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ec1fdada'
  }

  const uri = starknet.transfer(recipient, {
    token: {
      token_address: tokenAddresses[token],
      chainId: '0x534e5f4d41494e'  // Mainnet
    },
    amount: amount.toString()
  })

  return QRCode.toDataURL(uri, {
    errorCorrectionLevel: 'M',
    margin: 2,
    width: 300,
    color: {
      dark: '#000000',
      light: '#ffffff'
    }
  })
}
```

### Web Scanner Implementation

```javascript
// scanner.html
<!DOCTYPE html>
<html>
<head>
  <title>Starknet QR Scanner</title>
  <script src="https://unpkg.com/html5-qrcode"></script>
  <style>
    #reader { width: 100%; max-width: 400px; margin: 0 auto; }
    .confirmation { padding: 20px; text-align: center; }
    .wallet-btn { display: block; width: 100%; padding: 12px; margin: 8px 0; }
  </style>
</head>
<body>
  <div id="reader"></div>
  <div id="confirmation" style="display:none;" class="confirmation">
    <h3>Payment Request</h3>
    <p id="recipient"></p>
    <p id="amount"></p>
    <div id="wallet-buttons"></div>
  </div>

  <script>
    function onScanSuccess(decodedText) {
      if (!decodedText.startsWith('starknet:')) {
        alert('Invalid Starknet QR code')
        return
      }

      const params = new URLSearchParams(decodedText.split('?')[1])
      document.getElementById('recipient').textContent =
        `To: ${decodedText.match(/starknet:([^\/@]+)/)?.[1]}`
      document.getElementById('amount').textContent =
        `Amount: ${params.get('uint256') || 'Not specified'}`

      showWalletOptions(decodedText)
    }

    function showWalletOptions(uri) {
      const wallets = [
        { name: 'Braavos', scheme: 'braavos', url: 'braavos://' },
        { name: 'Argent X', scheme: 'argentx', url: 'argentx://' },
        { name: 'Ready', scheme: 'ready', url: 'starknet-ready://' }
      ]

      const container = document.getElementById('wallet-buttons')
      container.innerHTML = wallets.map(w =>
        `<button class="wallet-btn" onclick="openWallet('${uri}', '${w.scheme}')">
          Open in ${w.name}
        </button>`
      ).join('')
    }

    function openWallet(uri, wallet) {
      // Transform URI for specific wallet if needed
      window.location.href = uri
    }
  </script>
</body>
</html>
```

### Wallet Deep Link Handler

**Android (AndroidManifest.xml):**
```xml
<activity android:name=".MainActivity">
  <intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="starknet" />
  </intent-filter>
</activity>
```

**iOS (Info.plist):**
```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>starknet</string>
    </array>
  </dict>
</array>
```

**Browser Extension (manifest.json):**
```json
{
  "externally_connectable": {
    "matches": ["*://*.starknet/*"]
  }
}
```

---

## 7. Security Considerations

### Threat Model

| Threat | Severity | Mitigation |
|--------|----------|------------|
| **QR Code Tampering** | High | Verify checksum, display full address before confirming |
| **Address Poisoning** | Medium | Show first/last 4 chars, encourage address book |
| **Phishing Sites** | High | Domain verification, HTTPS enforcement |
| **Malicious Deep Links** | Medium | Input validation, sandboxed parsing |
| **Camera Hijacking** | Low | Use HTTPS, request permission explicitly |
| **MITM Attacks** | Medium | Certificate pinning, HSTS |

### Security Best Practices

1. **QR Code Integrity:**
   - Use error correction level M or H
   - Include CRC32 checksum in URI
   - Implement QR authentication for high-value transactions

2. **User Education:**
   ```
   ⚠️ Security Tips:
   • Verify the recipient address matches what you expect
   • Check the network (Mainnet vs Testnet)
   • Start with small amounts when trying new merchants
   • Never share your seed phrase, even if asked "for verification"
   ```

3. **UI Security Indicators:**
   - Green verification badge for verified merchants
   - Red warning for unknown recipients
   - Network indicator clearly visible
   - Amount in user-selected denomination

4. **Transaction Simulation:**
   ```
   Before confirming, show:
   ┌─────────────────────────────────────┐
   │ Transaction Preview                 │
   ├─────────────────────────────────────┤
   │ Send: 0.01 ETH                      │
   │ To: 0x049d...4dc7 (Merchant ABC)    │
   │ Network: Starknet Mainnet           │
   │ Gas: ~0.001 ETH                     │
   │ ───────────────────────────────     │
   │ Total: 0.011 ETH                    │
   └─────────────────────────────────────┘
   ```

5. **Fraud Detection:**
   - Flag unusual amounts
   - Detect repeated small transactions
   - Merchant reputation system (opt-in)
   - Reporting mechanism for fraudulent QRs

---

## 8. Improvement Proposal for Wallet Developers

### Requested Features (Priority Order)

#### High Priority

**1. Native QR Scanner Integration**
```
Issue: Wallets without scanners force users to use external tools
Impact: High friction, security risk from untrusted scanners
Solution: Integrate jsQR or native platform scanner
Timeline: Q2 2026
```

**2. Web Scanner Deep Linking**
```
Issue: Web scanners can't reliably open specific wallet apps
Impact: Users can't choose their preferred wallet
Solution: Support starknet: URI with wallet selection
Timeline: Q1 2026
```

**3. Address Verification UI**
```
Issue: Users can't easily verify QR addresses match intent
Impact: High risk of wrong-address attacks
Solution: Show address hash with visual verification
Timeline: Immediate (UI update)
```

#### Medium Priority

**4. Transaction Preview API**
```
Issue: dApps can't show transaction preview before wallet opens
Impact: Users blind-sign without seeing full details
Solution: Implement Starknet Request API (similar to EIP-1193)
Timeline: Q3 2026
```

**5. Offline QR Generation**
```
Issue: Can't generate payment QR without internet
Impact: Fails in low-connectivity areas
Solution: Cache token metadata, generate QR client-side
Timeline: Q2 2026
```

**6. Multi-Language Address Display**
```
Issue: Addresses hard to verify across languages
Impact: Confusion errors
Solution: Show address in local script where possible
Timeline: Q4 2026
```

#### Nice to Have

**7. Batch Transaction Support**
```
Issue: Can't approve multiple transfers in one QR
Impact: Inefficient for recurring payments
Solution: Support array of transactions in single URI
Timeline: 2027
```

**8. QR Code Animation/Security Pattern**
```
Issue: Static QR codes can be photographed/duplicated
Impact: Physical theft risk
Solution: Time-limited or gesture-confirmed QRs
Timeline: 2027
```

### Implementation Checklist

```markdown
## Wallet QR Support Checklist

### Required (MVP)
- [ ] Register starknet: URI scheme
- [ ] Parse transfer URIs
- [ ] Display transaction preview
- [ ] Pre-fill transfer form
- [ ] Handle invalid URIs gracefully

### Recommended
- [ ] Native QR scanner
- [ ] Address book integration
- [ ] Transaction history lookup
- [ ] Gas estimation
- [ ] Token icon display

### Enhanced Security
- [ ] Phishing domain detection
- [ ] Address whitelisting
- [ ] Spending limits
- [ ] Multi-factor confirmation
- [ ] Hardware wallet signing
```

---

## 9. Compatibility Matrix

| Wallet | Platform | QR Scanner | Deep Link Support | Status |
|--------|----------|-------------|-------------------|--------|
| Braavos | Mobile | ✅ Built-in | ✅ Full | Compatible |
| Braavos | Extension | ❌ None | ✅ Full | Needs Scanner |
| Argent X | Extension | ❌ None | ✅ Full | Needs Scanner |
| Ready | Mobile | ✅ Built-in | ✅ Full | Compatible |
| Argent | Mobile | ✅ Built-in | ✅ Full | Compatible |
| MetaMask | Extension | ❌ None | ⚠️ Limited | Needs Adapter |

---

## 10. Testing Strategy

### Unit Tests
```javascript
describe('Starknet URI Parser', () => {
  it('parses transfer URIs correctly', () => {
    const uri = 'starknet:0x123...@0x534e5f474f45524c49/transfer?uint256=1e-2'
    const parsed = parse(uri)
    expect(parsed.target_address).to.equal('0x123...')
    expect(parsed.chain_id).to.equal('0x534e5f474f45524c49')
    expect(parsed.function_name).to.equal('transfer')
    expect(parsed.parameters.uint256).to.equal('1e-2')
  })

  it('rejects invalid URIs', () => {
    expect(() => parse('invalid')).to.throw()
    expect(() => parse('https://example.com')).to.throw()
  })
})
```

### Integration Tests
- QR generation with valid starknet URIs
- Deep link opening from various sources
- Transaction pre-fill accuracy
- Wallet selection on multi-wallet devices

### E2E Tests
- Full payment flow from QR scan to confirmation
- Network switching scenarios
- Insufficient balance handling
- Error recovery flows

---

## 11. Cost Analysis

| Component | One-time Cost | Recurring Cost |
|-----------|--------------|----------------|
| Web Scanner Development | $15,000-25,000 | $50-200/month (hosting) |
| QR Code Library Licenses | $0 (MIT) | $0 |
| Security Audit | $10,000-20,000 | N/A |
| UI/UX Design | $5,000-10,000 | N/A |
| Testing | $5,000 | N/A |

**Total Initial Investment:** $35,000-60,000
**Annual Maintenance:** $600-2,400

---

## 12. Conclusion

The **Hybrid Web Scanner + Deep Link** approach provides the best balance of security, UX, and compatibility for Starknet wallets without native QR scanners. This solution:

1. **Prioritizes Security** - No private key exposure, verification UI, phishing protection
2. **Delivers Excellent UX** - Single web interface, wallet selection, transaction preview
3. **Ensures Compatibility** - Works across iOS, Android, browser extensions
4. **Follows Standards** - Leverages established `starknet:` URI scheme

**Immediate Next Steps:**
1. Begin web scanner development (Phase 1)
2. Coordinate with wallet teams for deep link verification
3. Conduct security audit of scanner implementation
4. Pilot with Ready wallet for feedback
5. Roll out to broader user base

---

## References

- Starknet URI Scheme: https://github.com/myBraavos/starknet-url
- Get Starknet (Wallet Bridge): https://github.com/starknet-io/get-starknet
- ERC-681 (Ethereum Payment URIs): https://eips.ethereum.org/EIPS/eip-681
- QR Code Security Best Practices: https://www.infosecurity-magazine.com/
- Android Intent Documentation: https://developer.android.com/guide/topics/manifest/intent-filter-element

---

*Document Version: 1.0*
*Last Updated: 2026-02-05*
