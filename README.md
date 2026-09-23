# LAN Device Monitor

A small, local-first Python utility that inventories devices already visible in your operating system's ARP/neighbor table and detects changes between snapshots. It is designed for home labs, development networks, troubleshooting, and lightweight inventory checks without active port scanning.

## Why it exists
Operating systems already maintain a neighbor cache for devices they have recently communicated with. This project turns that cache into a portable CLI/API with normalized output, snapshot persistence, CIDR filtering, and deterministic change detection.

## Features
- Windows (`arp -a`), Linux (`ip neigh show`), and macOS (`arp -an`) support.
- Normalized IPv4/MAC/state inventory.
- Save and reload JSON snapshots.
- Detect newly seen devices, disappeared devices, and IP changes by MAC address.
- Optional CIDR filtering such as `192.168.1.0/24`.
- Human-readable and JSON CLI output.
- `--fail-on-change` for scripts/CI (`0` no failure, `1` change detected, `2` operational/input error).
- Python API with no runtime third-party dependencies.
- No packet capture, port scanning, telemetry, cloud service, or credentials.

## Preview
```text
IP               MAC                STATE
192.168.1.1      aa:bb:cc:dd:ee:01 reachable
192.168.1.20     aa:bb:cc:dd:ee:20 stale
```
Output depends entirely on the current OS neighbor cache; the tool never invents devices.

## Requirements
- Python 3.10+
- Windows, Linux, or macOS
- On Linux, the `ip` command (normally supplied by iproute2)

## Installation
```bash
git clone https://github.com/rad03i2/lan-device-monitor.git
cd lan-device-monitor
python -m pip install -e .
```

## Usage
Capture the current cache:
```bash
lan-monitor scan
```

Filter to one subnet and save a baseline:
```bash
lan-monitor scan --network 192.168.1.0/24 --save baseline.json
```

Machine-readable output:
```bash
lan-monitor scan --json
```

Compare a baseline with the current cache:
```bash
lan-monitor diff baseline.json
```

Fail a script when membership/IP changes are detected:
```bash
lan-monitor diff baseline.json --fail-on-change
```

Module invocation is also supported:
```bash
python -m lan_device_monitor scan
```

### Python API
```python
from lan_device_monitor import scan, compare, Snapshot

current = scan()
current.save("baseline.json")
previous = Snapshot.load("baseline.json")
changes = compare(previous, current)
```

## Configuration
There is intentionally no config file or `.env`: the application needs no secrets. Configure each run with CLI options. `--timeout` controls the OS command timeout and `--network` restricts displayed devices to a CIDR.

## Project structure
```text
src/lan_device_monitor/
  core.py        discovery, parsing, snapshots, comparison
  cli.py         command-line interface
  __main__.py    python -m entry point
tests/            deterministic parser/persistence/comparison tests
.github/workflows/ci.yml
pyproject.toml
```

## Testing
```bash
python -m pip install -e . pytest
python -m compileall -q src
python -m pytest -q
lan-monitor --version
```
CI runs these checks on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

## Security & privacy
The tool only reads the local machine's existing neighbor table. It performs no active network sweep, packet capture, exploitation, DNS enrichment, cloud upload, or telemetry. Snapshot JSON contains local IP and MAC addresses and should therefore be treated as potentially sensitive inventory data. Use the tool only on systems/networks you are authorized to inspect. See [SECURITY.md](SECURITY.md).

## Limitations
- A neighbor/ARP cache is **not** a complete list of every device on a network. Devices appear only when the OS has learned about them.
- This release parses IPv4 entries; IPv6 neighbor inventory is not yet normalized.
- Device names, vendors, operating systems, and open ports are intentionally not inferred.
- A device that ages out of the cache can appear "removed" even if it is still online.
- Snapshot comparison identifies a device by MAC address; MAC randomization can therefore look like a new device.

## Optional roadmap
Potential future work includes IPv6 normalization and an opt-in passive history store. Active scanning is intentionally outside the current scope.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes focused, tested, local-first, and non-invasive.

## License
MIT — see [LICENSE](LICENSE).

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية — مراقب أجهزة الشبكة المحلية

أداة Python صغيرة ومحلية أولًا تعرض الأجهزة الموجودة بالفعل في جدول ARP/الجيران الخاص بنظام التشغيل، وتحفظ لقطات قابلة للمقارنة لاكتشاف التغييرات. تناسب الشبكات المنزلية ومختبرات التطوير واستكشاف المشاكل والجرد الخفيف، من دون تنفيذ مسح نشط للمنافذ.

## لماذا المشروع؟
يحتفظ نظام التشغيل أصلًا بمعلومات الأجهزة التي تواصل معها مؤخرًا. يحول هذا المشروع تلك المعلومات إلى CLI وPython API منظّمين، مع توحيد عناوين MAC وحفظ JSON والتصفية حسب الشبكة ومقارنة اللقطات.

## المزايا
- دعم Windows عبر `arp -a` وLinux عبر `ip neigh show` وmacOS عبر `arp -an`.
- عرض IPv4 وMAC والحالة بصورة موحدة.
- حفظ اللقطات واستعادتها بصيغة JSON.
- كشف الأجهزة الجديدة والمختفية وتغير عنوان IP لنفس MAC.
- تصفية اختيارية بصيغة CIDR مثل `192.168.1.0/24`.
- مخرجات نصية أو JSON.
- خيار `--fail-on-change` مناسب للأتمتة: 0 طبيعي، 1 عند وجود تغيير، 2 عند خطأ تشغيل/إدخال.
- لا توجد اعتماديات تشغيل خارجية أو خدمة سحابية أو telemetry.

## معاينة
```text
IP               MAC                STATE
192.168.1.1      aa:bb:cc:dd:ee:01 reachable
```
النتيجة تعتمد على جدول الجيران الحقيقي في جهازك ولا ينشئ البرنامج أجهزة وهمية.

## المتطلبات والتثبيت
Python 3.10 أو أحدث على Windows أو Linux أو macOS. يحتاج Linux إلى أمر `ip`.

```bash
git clone https://github.com/rad03i2/lan-device-monitor.git
cd lan-device-monitor
python -m pip install -e .
```

## الاستخدام
```bash
lan-monitor scan
lan-monitor scan --network 192.168.1.0/24 --save baseline.json
lan-monitor scan --json
lan-monitor diff baseline.json
lan-monitor diff baseline.json --fail-on-change
```

ويمكن تشغيله أيضًا عبر:
```bash
python -m lan_device_monitor scan
```

### Python API
```python
from lan_device_monitor import scan, compare, Snapshot
current = scan()
current.save("baseline.json")
previous = Snapshot.load("baseline.json")
changes = compare(previous, current)
```

## الإعداد
لا يحتاج المشروع إلى `.env` أو أسرار. يتم ضبط المهلة عبر `--timeout` وتحديد الشبكة عبر `--network` عند الحاجة.

## بنية المشروع
المحرك موجود في `src/lan_device_monitor/core.py`، والواجهة الطرفية في `cli.py`، والاختبارات في `tests/`، وCI في `.github/workflows/ci.yml`.

## الاختبارات
```bash
python -m pip install -e . pytest
python -m compileall -q src
python -m pytest -q
lan-monitor --version
```
ويشغّل GitHub Actions الاختبارات على Ubuntu وWindows وmacOS مع Python 3.10 و3.12 و3.13.

## الأمان والخصوصية
الأداة تقرأ جدول الجيران الموجود محليًا فقط؛ لا تنفذ مسح منافذ أو التقاط حزم أو استغلالًا أو رفعًا سحابيًا أو telemetry. تحتوي ملفات اللقطات على IP وMAC محليين، لذلك تعامل معها كبيانات جرد قد تكون حساسة. استخدم الأداة فقط على الأنظمة والشبكات المصرح لك بفحصها. راجع [SECURITY.md](SECURITY.md).

## القيود
جدول ARP/الجيران ليس قائمة كاملة بكل أجهزة الشبكة؛ تظهر الأجهزة التي تعلّمها النظام فقط. الإصدار الحالي يوحد IPv4 فقط، ولا يستنتج أسماء الأجهزة أو الشركات أو أنظمة التشغيل أو المنافذ. وقد يبدو الجهاز مختفيًا إذا انتهى إدخاله من الكاش، كما أن MAC العشوائي قد يظهر كجهاز جديد.

## تطوير اختياري
يمكن مستقبلًا إضافة توحيد IPv6 وسجل تاريخي محلي اختياري. المسح النشط خارج نطاق المشروع الحالي عمدًا.

## المساهمة
راجع [CONTRIBUTING.md](CONTRIBUTING.md). يجب أن تبقى التغييرات مختبرة ومحلية وغير تدخّلية.

## الترخيص
MIT — راجع [LICENSE](LICENSE).

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
