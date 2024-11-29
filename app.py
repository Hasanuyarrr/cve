from flask import Flask, jsonify, render_template
from datetime import datetime, timedelta
import vulners
import threading
import time

# Flask uygulaması oluştur
app = Flask(__name__)

# Vulners API anahtarı
API_KEY = "N8B8IXAXWYWBRUFB3JOVT566HNSJBRQZKCYPCD4GYLQTWL1APQ748FNK8LJTL4KT"
vulners_api = vulners.Vulners(api_key=API_KEY)

# CVE verilerini depolamak için bir değişken
cve_data = []

# CVE'leri Vulners API'den al ve cve_data'ya kaydet
def fetch_cve_data():
    global cve_data
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    query = f"published:[{yesterday} TO {today}] AND type:cve"
    try:
        search_result = vulners_api.search(query)
        cve_data = []  # Eski verileri temizle

        if search_result:
            for cve in search_result:
                cve_data.append({
                    "id": cve.get("id", "CVE ID yok"),
                    "title": cve.get("title", "Başlık yok"),
                    "description": cve.get("description", "Açıklama yok"),
                    "published_date": cve.get("published", "Tarih yok"),
                    "vhref_link": cve.get("vhref", "vhref bağlantısı yok"),
                })
        else:
            cve_data = []
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

# CVE verilerini düzenli olarak güncellemek için bir zamanlayıcı
def update_cve_data_periodically():
    while True:
        fetch_cve_data()
        print("CVE verileri güncellendi.")
        time.sleep(9 * 60 * 60)  # 9 saat bekle

# Flask endpoint: CVE verilerini görüntüle
@app.route('/vuln')
def vuln():
    return render_template('vuln.html', cves=cve_data)

# Web sunucusunu başlatmadan önce CVE verilerini güncellemeye başla
if __name__ == '__main__':
    # Arka planda veri güncelleme thread'i başlat
    threading.Thread(target=update_cve_data_periodically, daemon=True).start()
    # Flask sunucusunu başlat
    app.run(debug=True)
