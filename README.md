# Aplikasi Radar FMCW

Aplikasi GUI radar untuk FMCW. Digunakan untuk keperluan penelitian IS-IoT Telkom University.
Aplikasi ini mengambil nilai _phase_ dan _magnitude_ dari radar FMCW, lalu menyimpa(di ``Document``) dan menampilkan
data tersebut.

## Cara Install

- Pastikan Python versi 3.7 keatas telah terinstall.
- Cek dengan membuka CMD (Command Prompt) dan ketik python, jika muncul tulisan: "Python 3.x.xx ..." (versi python) maka prosess instalasi berhasil.
- Buka lagi CMD (Command Prompt) di folder ini (radar-fmcw) dengan cara: ```ctrl + shift + click``` kanan di dalam folder urad lalu pilih **Command Prompt** atau **Powershell** atau **Terminal**, lalu ketik ```pip install -r requirements.txt```
- Tunggu hingga selesai.
- Setelah prosess installasi library berhasil, double click file: main.py. Jika muncul UI maka prosess installasi berhasil

## Cara Menggunakan Aplikasi

1. Pastikan nomor port radar, telah di konfigurasi secara benar.
    - Buka Setting
      
      ![image](https://github.com/rc-iot-telu/radar-fmcw/assets/60130740/e0c6ea35-6266-47ca-9a0d-44218ad810e7)

    - Klik tombol ```Refresh Daftar Port```, lalu akan muncul nomor port (radar) yang terhubung, masukan nomor
      port tersebut (hanya tulis "COMXX", XX berarti nomor port), lalu klik ```Simpan Setting```
      ![image](https://github.com/rc-iot-telu/radar-fmcw/assets/60130740/70025fe1-cad2-45f0-8fde-9705c59b197d)

    - Jika sudah, klik tombol ```Mulai Scan```, jika grafik terjadi perubahan, berarti Anda telah menyeting aplikasi
      secara benar.
    - Untuk menyimpan data, klik tombol ```Save Data```, maka data akan tersimpan di dalam folder ```Dokuments``` Anda.

