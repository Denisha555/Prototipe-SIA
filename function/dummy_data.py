import sqlite3
import datetime

DB = "data_keuangan.db"

def make_id(prefix, date_obj, index=1):
    return f"{prefix}{date_obj.strftime('%Y%m%d')}{str(index).zfill(3)}"

def run():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # ---------- (Opsional) Hapus data lama pada tabel transaksi/jurnal (jangan hapus akun) ----------
    tables_to_clear = [
        "transaksi_penjualan",
        "detail_transaksi_penjualan",
        "transaksi_kas_keluar",
        "jurnal_umum_detail",
        "transaksi_penyesuaian",
        "rekap_modal"
    ]
    for t in tables_to_clear:
        c.execute(f"DELETE FROM {t}")
    conn.commit()

    # ---------- AGUSTUS (bulan awal) ----------
    # Tgl format: YYYY-MM-DD (use date objects for clarity)
    agustus_modal_tgl = datetime.date(2025, 8, 1)

    # 1) Penyetoran modal awal: Kas (111) debit, Modal Pemilik (311) kredit
    ref_modal = make_id("MOD", agustus_modal_tgl, 1)
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_modal, agustus_modal_tgl.isoformat(), "111", "Penyetoran Modal Awal", 50000000, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_modal, agustus_modal_tgl.isoformat(), "311", "Penyetoran Modal Awal", 0, 50000000, "UMUM"))

    # 2) Pembelian perlengkapan (aset) Agustus: Perlengkapan (113) debit, Kas (111) kredit
    tgl_beli_perlengkapan = datetime.date(2025, 8, 5)
    ref_beli_perl = make_id("PB", tgl_beli_perlengkapan, 1)
    jumlah_perlengkapan_agus = 1500000
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_beli_perl, tgl_beli_perlengkapan.isoformat(), "113", "Beli Perlengkapan", jumlah_perlengkapan_agus, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_beli_perl, tgl_beli_perlengkapan.isoformat(), "111", "Beli Perlengkapan (kas)", 0, jumlah_perlengkapan_agus, "UMUM"))

    # 3) Pendapatan Agustus (satu transaksi contoh)
    tgl_pend_agus = datetime.date(2025, 8, 10)
    ref_pj_agus = make_id("PJ", tgl_pend_agus, 1)
    total_pend_agus = 6000000
    c.execute("""
        INSERT INTO transaksi_penjualan (transaksi_penjualan_id, tanggal, total, kategori, keterangan)
        VALUES (?, ?, ?, ?, ?)
    """, (ref_pj_agus, tgl_pend_agus.isoformat(), total_pend_agus, "Pendapatan Jasa", "Pendapatan Agustus"))
    # Jurnal: Kas (111) debit, Pendapatan Jasa (401) kredit
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_pj_agus, tgl_pend_agus.isoformat(), "111", "Kas dari penjualan", total_pend_agus, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_pj_agus, tgl_pend_agus.isoformat(), "401", "Pendapatan jasa", 0, total_pend_agus, "UMUM"))

    # 4) Beban gaji Agustus (kas keluar BEBAN)
    tgl_gaji_agus = datetime.date(2025, 8, 25)
    ref_gaji_agus = make_id("BG", tgl_gaji_agus, 1)
    jumlah_gaji_agus = 2000000
    c.execute("""
        INSERT INTO transaksi_kas_keluar (transaksi_kas_keluar_id, tanggal, kategori, nominal, keterangan)
        VALUES (?, ?, ?, ?, ?)
    """, (ref_gaji_agus, tgl_gaji_agus.isoformat(), "Beban Gaji", jumlah_gaji_agus, "Pembayaran gaji Agustus"))
    # Jurnal: Beban Gaji (511) debit, Kas (111) kredit
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_gaji_agus, tgl_gaji_agus.isoformat(), "511", "Beban Gaji Agustus", jumlah_gaji_agus, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_gaji_agus, tgl_gaji_agus.isoformat(), "111", "Kas keluar gaji Agustus", 0, jumlah_gaji_agus, "UMUM"))

    # 5) PENYESUAIAN akhir Agustus: Perlengkapan terpakai 1.000.000
    tgl_adj_agus = datetime.date(2025, 8, 31)
    # Simpan ke transaksi_penyesuaian (ID auto increment -> do not specify id)
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_agus.isoformat(), "513", "Beban perlengkapan Agustus", 1000000, 0))
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_agus.isoformat(), "113", "Pengurangan perlengkapan Agustus", 0, 1000000))
    # Juga catat ke jurnal_umum_detail dengan jenis PENYESUAIAN
    ref_adj1 = make_id("ADJ", tgl_adj_agus, 1)
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj1, tgl_adj_agus.isoformat(), "513", "Beban perlengkapan Agustus (penyesuaian)", 1000000, 0, "PENYESUAIAN"))
    c.execute("""
        INSERT INTO jurnal_umum_detail
            (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj1, tgl_adj_agus.isoformat(), "113", "Perlengkapan berkurang Agustus (penyesuaian)", 0, 1000000, "PENYESUAIAN"))

    # ---------- SEPTEMBER ----------
    # 1) Pembelian peralatan (aset) September
    tgl_beli_peralatan = datetime.date(2025, 9, 3)
    ref_beli_peral = make_id("PB", tgl_beli_peralatan, 1)
    jumlah_peralatan = 10000000
    # Peralatan = akun 121, Kas 111
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_beli_peral, tgl_beli_peralatan.isoformat(), "121", "Beli Peralatan", jumlah_peralatan, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_beli_peral, tgl_beli_peralatan.isoformat(), "111", "Kas keluar beli peralatan", 0, jumlah_peralatan, "UMUM"))

    # 2) Pendapatan September
    tgl_pend_sep = datetime.date(2025, 9, 12)
    ref_pj_sep = make_id("PJ", tgl_pend_sep, 1)
    total_pend_sep = 8000000
    c.execute("""
        INSERT INTO transaksi_penjualan (transaksi_penjualan_id, tanggal, total, kategori, keterangan)
        VALUES (?, ?, ?, ?, ?)
    """, (ref_pj_sep, tgl_pend_sep.isoformat(), total_pend_sep, "Pendapatan Jasa", "Pendapatan September"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_pj_sep, tgl_pend_sep.isoformat(), "111", "Kas dari penjualan", total_pend_sep, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_pj_sep, tgl_pend_sep.isoformat(), "401", "Pendapatan jasa", 0, total_pend_sep, "UMUM"))

    # 3) Beban gaji September
    tgl_gaji_sep = datetime.date(2025, 9, 25)
    ref_gaji_sep = make_id("BG", tgl_gaji_sep, 1)
    jumlah_gaji_sep = 2500000
    c.execute("""
        INSERT INTO transaksi_kas_keluar (transaksi_kas_keluar_id, tanggal, kategori, nominal, keterangan)
        VALUES (?, ?, ?, ?, ?)
    """, (ref_gaji_sep, tgl_gaji_sep.isoformat(), "Beban Gaji", jumlah_gaji_sep, "Pembayaran gaji September"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_gaji_sep, tgl_gaji_sep.isoformat(), "511", "Beban Gaji September", jumlah_gaji_sep, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_gaji_sep, tgl_gaji_sep.isoformat(), "111", "Kas keluar gaji September", 0, jumlah_gaji_sep, "UMUM"))

    # 4) Penyesuaian akhir September: Penyusutan peralatan 1.000.000
    tgl_adj_sep = datetime.date(2025, 9, 30)
    # simpan di transaksi_penyesuaian (autoinc id)
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_sep.isoformat(), "514", "Beban penyusutan peralatan September", 1000000, 0))
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_sep.isoformat(), "122", "Akumulasi penyusutan peralatan September", 0, 1000000))
    # juga catat di jurnal_umum_detail (jenis PENYESUAIAN)
    ref_adj_sep = make_id("ADJ", tgl_adj_sep, 1)
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj_sep, tgl_adj_sep.isoformat(), "514", "Beban penyusutan peralatan (penyesuaian)", 1000000, 0, "PENYESUAIAN"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj_sep, tgl_adj_sep.isoformat(), "122", "Akumulasi penyusutan peralatan (penyesuaian)", 0, 1000000, "PENYESUAIAN"))

    # ---------- OKTOBER ----------
    # 1) Pembelian perlengkapan tambahan Oktober
    tgl_beli_perl_okt = datetime.date(2025, 10, 4)
    ref_beli_perl_okt = make_id("PB", tgl_beli_perl_okt, 1)
    jumlah_perl_okt = 500000
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_beli_perl_okt, tgl_beli_perl_okt.isoformat(), "113", "Beli perlengkapan tambahan", jumlah_perl_okt, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_beli_perl_okt, tgl_beli_perl_okt.isoformat(), "111", "Kas keluar beli perlengkapan", 0, jumlah_perl_okt, "UMUM"))

    # 2) Pendapatan Oktober
    tgl_pend_okt = datetime.date(2025, 10, 15)
    ref_pj_okt = make_id("PJ", tgl_pend_okt, 1)
    total_pend_okt = 10000000
    c.execute("""
        INSERT INTO transaksi_penjualan (transaksi_penjualan_id, tanggal, total, kategori, keterangan)
        VALUES (?, ?, ?, ?, ?)
    """, (ref_pj_okt, tgl_pend_okt.isoformat(), total_pend_okt, "Pendapatan Jasa", "Pendapatan Oktober"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_pj_okt, tgl_pend_okt.isoformat(), "111", "Kas dari penjualan", total_pend_okt, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_pj_okt, tgl_pend_okt.isoformat(), "401", "Pendapatan jasa", 0, total_pend_okt, "UMUM"))

    # 3) Beban gaji Oktober
    tgl_gaji_okt = datetime.date(2025, 10, 25)
    ref_gaji_okt = make_id("BG", tgl_gaji_okt, 1)
    jumlah_gaji_okt = 3000000
    c.execute("""
        INSERT INTO transaksi_kas_keluar (transaksi_kas_keluar_id, tanggal, kategori, nominal, keterangan)
        VALUES (?, ?, ?, ?, ?)
    """, (ref_gaji_okt, tgl_gaji_okt.isoformat(), "Beban Gaji", jumlah_gaji_okt, "Pembayaran gaji Oktober"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_gaji_okt, tgl_gaji_okt.isoformat(), "511", "Beban Gaji Oktober", jumlah_gaji_okt, 0, "UMUM"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_gaji_okt, tgl_gaji_okt.isoformat(), "111", "Kas keluar gaji Oktober", 0, jumlah_gaji_okt, "UMUM"))

    # 4) Penyesuaian akhir Oktober:
    tgl_adj_okt = datetime.date(2025, 10, 31)
    # Penyesuaian perlengkapan (beban) 300.000
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_okt.isoformat(), "513", "Beban perlengkapan Oktober", 300000, 0))
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_okt.isoformat(), "113", "Pengurangan perlengkapan Oktober", 0, 300000))
    # Jurnal penyesuaian ke jurnal_umum_detail
    ref_adj_okt = make_id("ADJ", tgl_adj_okt, 1)
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj_okt, tgl_adj_okt.isoformat(), "513", "Beban perlengkapan Oktober (penyesuaian)", 300000, 0, "PENYESUAIAN"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj_okt, tgl_adj_okt.isoformat(), "113", "Perlengkapan berkurang Oktober (penyesuaian)", 0, 300000, "PENYESUAIAN"))

    # Penyesuaian penyusutan peralatan Oktober 1.000.000
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_okt.isoformat(), "514", "Beban penyusutan peralatan Oktober", 1000000, 0))
    c.execute("""
        INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tgl_adj_okt.isoformat(), "122", "Akumulasi penyusutan peralatan Oktober", 0, 1000000))
    # jurnal penyesuaian
    ref_adj_okt2 = make_id("ADJ", tgl_adj_okt, 2)
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj_okt2, tgl_adj_okt.isoformat(), "514", "Beban penyusutan peralatan (penyesuaian)", 1000000, 0, "PENYESUAIAN"))
    c.execute("""
        INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ref_adj_okt2, tgl_adj_okt.isoformat(), "122", "Akumulasi penyusutan peralatan (penyesuaian)", 0, 1000000, "PENYESUAIAN"))

    # ---------- Commit & close ----------
    conn.commit()
    conn.close()
    print("✅ Dummy data (logis & konsisten) telah dimasukkan ke database.")

if __name__ == "__main__":
    run()
