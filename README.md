# Souline
Nama “SOULINE” diambil dari kata “SOUL” yang artinya jiwa, dan “LINE” yang artinya garis. Dua kata ini relevan dengan olahraga Yoga & Pilates yang mementingkan ketenangan jiwa dan keseimbangan. Pengucapan “SOULINE” juga mirip dengan kata ‘SOLAINE” dalam bahasa Prancis yang dapat diartikan sebagai Brightness atau Positivity. Aplikasi ini akan membantu pengguna untuk mencari dan menentukan studio olahraga berdasarkan area yang mereka pilih. Pengguna juga dapat melihat rekomendasi sportswear dan resources dalam mempelajari Yoga & Pilates. Selain itu, pengguna dapat berbagi pengalaman dengan komunitas yang dapat meningkatkan semangat dalam berolahraga Yoga atau Pilates. 

## Nama-nama anggota kelompok
- Adzradevany Aqiila - 2406410121
- Aghnaya Kenarantanov - 2406436410
- Cheryl Raynasya Adenan - 2406437571
- Cristian Dillon Philbert - 2406495956
- Muhammad Faza Al-Banna - 2406496082
- Farrel Rifqi Bagaskoro - 2406406780

## Daftar modul yang akan diimplementasikan
### Studio (Faza)
Modul yang digunakan untuk mencari studio terdekat di lingkup daerah Jabodetabek. Modul ini berisi detail studio yoga dan/atau pilates, termasuk data seperti nama studio, foto-foto di dalam studio, jam buka-tutup, rating dan reviews, serta link ke google maps. Modul ini juga memiliki fitur untuk melakukan booking sesuai dengan ketentuan dari studio masing masing, dapat melalui WhatsApp atau melalui link ke website langsung.
### Sportswear (Cheryl)
Modul yang berguna untuk mencari sportswear yang akan membantu olahraga yoga dan/atau pilates, seperti diantaranya yoga pants, yoga clothes, yoga mat, dan sebagainya. Di modul ini akan ditampilkan brand-brand yang populer. Setiap brand akan memiliki tombol yang akan mengarah langsung ke online shop seperti Tokopedia/Shopee (atau keduanya) yang nantinya akan berguna bagi user agar segera membeli sportswear yang diinginkan.
### Resources (Dillon)
Modul ini akan memberikan panduan untuk memulai olahraga yoga dan/atau pilates. Panduan akan dibagi dari tingkat kesulitannya, dari yang baru mulai melakukan yoga dan/atau pilates hingga yang sudah ahli. Di modul ini akan diberikan sebuah video YouTube (melalui embed) kemudian ada paragraf penjelasan juga bagi yang tidak ingin menonton videonya. Tiap langkah akan dijelaskan secara mendetail agar tidak ada kesalahan dalam melakukan kegiatan olahraga.
### User (profile) (Farrel)
Sebuah modul yang akan menyimpan informasi pengguna saat ini. Modul ini sudah termasuk halaman register, login, dan fitur log out di halaman utama. Semua modul dalam website Souline akan memerlukan login, setiap user diperlukan untuk membuat akun untuk membuka website. Akun dapat dibuat dengan registrasi username dan password, dengan validasi password yang aman menggunakan implementasi dari Django. User juga diminta untuk memasukkan kota tempat tinggal saat ini untuk mempersonalisasikan pengalaman website berdasarkan lokasi (terutama modul studio).
### Timeline (Adzradevany Aqiila)
Modul yang dapat digunakan untuk membangun komunitas olahraga yoga dan pilates sesuai dengan minat dan hobi. Suatu komunitas akan mempunyai nama, deskripsi, dan foto yang merepresentasikan komunitas tersebut. Hubungan dari user ke komunitas adalah many-to-many, artinya satu user bisa mengikuti banyak komunitas dan satu komunitas bisa berisi banyak user. Pembuat dari suatu komunitas adalah owner dari komunitas tersebut, memiliki akses untuk menghapus komunitas secara permanen.

### Events (Aghnaya)
Modul ini berguna untuk menginformasikan acara terkait olahraga yoga dan/atau pilates yang tersedia untuk diikuti. Modul akan menampilkan suatu timeline berisi acara-acara yang akan datang beserta tanggal dan lokasinya. Informasi yang akan ditampilkan untuk setiap acara adalah nama acara, deskripsi singkat, dan poster dari acara tersebut. Setiap event akan mempunyai gambar poster dan mekanisme pendaftarannya masing-masing, misalnya dengan mengisi link Google Forms atau registrasi secara offline. Informasi mengenai acara-acara ini kami dapatkan dari sosial media atau komunitas yang ada.

## Sumber initial dataset kategori utama produk
[Dataset](https://github.com/pbp-kelompok-a3/souline/blob/aa663bd0609cfa5165a43fb26f251ec662d359fc/DataSet%20-%20List%20Pilates%20_%20Yoga%20Studio%20Jabodetabek%20(1).csv)

## Role atau peran pengguna beserta deskripsinya (karena bisa saja lebih dari satu jenis pengguna yang mengakses aplikasi)
- Pengguna Umum : Orang yang ingin mencari studio Yoga atau Pilates, ingin belajar, atau ingin mencari rekomendasi Sportswear.
- Admin : Orang yang mengelola aplikasi.

## Tautan deployment PWS dan link design
- PWS: https://farrel-rifqi-souline-pbp.cs.ui.ac.id/
- Figma: https://www.figma.com/design/ql7AIQTcw69ICUzbf60xvR/souline?node-id=0-1&t=neB69mb4vch7VejF-1
