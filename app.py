from playwright.sync_api import sync_playwright
import pandas as pd
import time

def scrape_indonesia_school():
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Ganti True jika tidak ingin menampilkan browser
        page = browser.new_page()
        page.goto("https://www.cambridgeinternational.org/why-choose-us/find-a-cambridge-school/")

        time.sleep(5)  # Tunggu halaman termuat

        # Menunggu dropdown lokasi (Region)
        try:
            page.wait_for_selector("//select[@id='SelectedRegionId']", timeout=60000)  # Tunggu hingga 60 detik
        except TimeoutError:
            print("❌ Gagal memuat dropdown lokasi dalam waktu yang ditentukan.")
            browser.close()
            return

        # Pilih Indonesia di dropdown lokasi
        location_dropdown = page.locator("//select[@id='SelectedRegionId']")
        locations = location_dropdown.locator("option").all()

        for location in locations[1:]:  # Lewati opsi pertama (placeholder)
            location_name = location.inner_text()
            location_value = location.get_attribute("value")

            if location_name == "Asia" or location_name == "Indonesia":  # Pilih Indonesia
                print(f"🔹 Memilih lokasi: {location_name}")
                location_dropdown.select_option(value=location_value)
                time.sleep(3)  # Tunggu daftar kota diperbarui

                # Pilih dropdown kota (City)
                city_dropdown = page.locator("//select[@id='SelectedCity']")
                try:
                    page.wait_for_selector("//select[@id='SelectedCity']", timeout=60000)  # Tunggu hingga 60 detik
                except TimeoutError:
                    print(f"❌ Gagal memuat dropdown kota di {location_name}.")
                    continue  # Lanjutkan ke lokasi berikutnya

                cities = city_dropdown.locator("option").all()

                # Ambil semua kota yang terdaftar
                for city in cities[1:]:  # Lewati opsi pertama (placeholder)
                    city_name = city.inner_text()
                    city_value = city.get_attribute("value")
                    print(f"📍 Memilih kota: {city_name}")
                    city_dropdown.select_option(value=city_value)
                    time.sleep(5)  # Tunggu daftar sekolah dimuat

                    # Klik tombol pencarian (search button)
                    search_button = page.locator("//input[@id='search']")
                    search_button.click()
                    time.sleep(5)  # Tunggu hasil pencarian dimuat

                    # Scrape daftar sekolah, lokasi dan private candidates menggunakan XPath
                    school_rows = page.locator("//*[@id='physicalAndOnlineOnly']/table/tbody/tr").all()

                    for row in school_rows:
                        # Nama sekolah ada pada kolom pertama (td[1]) dan mengandung link
                        try:
                            school_name_locator = row.locator("td:nth-child(1) a")  # Ambil tautan dalam nama sekolah
                            school_name = school_name_locator.inner_text()
                            school_link = school_name_locator.get_attribute("href")  # Ambil URL link
                        except Exception as e:
                            print(f"⚠️ Gagal mengambil nama sekolah atau link: {e}")
                            school_name = "Tidak Tersedia"
                            school_link = "Tidak Tersedia"

                        # Lokasi sekolah ada pada kolom kedua (td[2])
                        try:
                            location_text = row.locator("td:nth-child(2)").inner_text()
                        except Exception as e:
                            location_text = "Tidak Tersedia"
                            print(f"⚠️ Gagal mengambil lokasi sekolah: {e}")

                        # Informasi private candidates ada pada kolom ketiga (td[3])
                        try:
                            private_candidates_text = row.locator("td:nth-child(3)").inner_text()
                        except Exception as e:
                            private_candidates_text = "Tidak Tersedia"
                            print(f"⚠️ Gagal mengambil informasi private candidates: {e}")

                        # Simpan data
                        data.append({
                            "Location": location_name,
                            "City": city_name,
                            "School Name": school_name,
                            "School Link": school_link,  # Menyimpan link sekolah
                            "School Location": location_text,
                            "Private Candidates Accepted": private_candidates_text
                        })

                    print(f"✅ {len(school_rows)} sekolah ditemukan di {city_name}, {location_name}")

        browser.close()

    # Simpan data ke CSV
    if data:
        df = pd.DataFrame(data)
        df.to_csv("cambridge_schools_indonesia.csv", index=False, encoding='utf-8')
        print("✅ Scraping selesai! Data disimpan di cambridge_schools_indonesia.csv")
    else:
        print("⚠️ Tidak ada data yang diambil.")

# Jalankan scraper
scrape_indonesia_school()
