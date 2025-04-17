import streamlit as st
from pydub import AudioSegment
import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import os
import uuid

# Folder simpan
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_audio(uploaded_file):
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp3")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def apply_fade(audio_path, fade_in_ms=2000, fade_out_ms=2000):
    audio = AudioSegment.from_file(audio_path)
    faded = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)
    output_path = audio_path.replace(".mp3", "_fade.mp3")
    faded.export(output_path, format="mp3")
    return output_path

def change_tempo(audio_path, rate):
    y, sr = librosa.load(audio_path)
    y_stretched = librosa.effects.time_stretch(y, rate=rate)
    output_path = audio_path.replace(".mp3", f"_{str(rate).replace('.', '')}x.wav")
    sf.write(output_path, y_stretched, sr)
    return output_path

def simulate_podcast_intro_outro(audio_paths):
    intro_audio = AudioSegment.from_file(audio_paths[0])[:10000]
    outro_audio = AudioSegment.from_file(audio_paths[1])[-10000:]
    intro_fade = intro_audio.fade_in(3000)
    outro_fade = outro_audio.fade_out(3000)

    intro_path = os.path.join(UPLOAD_DIR, "podcast_intro_fade.mp3")
    outro_path = os.path.join(UPLOAD_DIR, "podcast_outro_fade.mp3")
    intro_fade.export(intro_path, format="mp3")
    outro_fade.export(outro_path, format="mp3")

    return intro_path, outro_path

def plot_waveform(audio_file, title):
    y, sr = librosa.load(audio_file)
    plt.figure(figsize=(10, 2))
    plt.title(title)
    plt.plot(y, color='skyblue')
    plt.xlabel("Waktu")
    plt.ylabel("Amplitudo")
    plt.tight_layout()
    st.pyplot(plt)

def analyze_audio_characteristics(audio_path):
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)
    rms = np.sqrt(np.mean(y**2))
    peak_amplitude = np.max(np.abs(y))
    return duration, rms, peak_amplitude

def generate_narrative(audio_paths, fade_paths, slow_paths, fast_paths, podcast_paths, combined_paths):
    st.markdown("## 📝 Narasi Eksperimen")

    durations = [analyze_audio_characteristics(p)[0] for p in audio_paths]
    rms_values = [analyze_audio_characteristics(p)[1] for p in audio_paths]
    peaks = [analyze_audio_characteristics(p)[2] for p in audio_paths]

    fade_durations = [analyze_audio_characteristics(p)[0] for p in fade_paths]
    slow_durations = [analyze_audio_characteristics(p)[0] for p in slow_paths]
    fast_durations = [analyze_audio_characteristics(p)[0] for p in fast_paths]
    combined_rms = [analyze_audio_characteristics(p)[1] for p in combined_paths]

    st.markdown(f"""
    Pada eksperimen ini, dua file audio telah diunggah dan diproses secara otomatis.

    **1. Efek Fade In dan Out**:
    - Durasi audio 1 sebelum fade: {durations[0]:.2f} detik → setelah fade: {fade_durations[0]:.2f} detik.
    - Durasi audio 2 sebelum fade: {durations[1]:.2f} detik → setelah fade: {fade_durations[1]:.2f} detik.
    - Rata-rata amplitudo RMS sebelum fade: audio 1 = {rms_values[0]:.4f}, audio 2 = {rms_values[1]:.4f}

    **2. Perubahan Tempo**:
    - Durasi audio 1 saat diperlambat (0.75x): {slow_durations[0]:.2f} detik, saat dipercepat (1.5x): {fast_durations[0]:.2f} detik.
    - Durasi audio 2 saat diperlambat (0.75x): {slow_durations[1]:.2f} detik, saat dipercepat (1.5x): {fast_durations[1]:.2f} detik.

    **3. Simulasi Podcast**:
    - Bagian pembuka menggunakan 10 detik awal dari audio 1 dengan fade in, memberikan nuansa halus saat mulai.
    - Bagian penutup mengambil 10 detik akhir dari audio 2 dan diberi fade out agar transisi keluar terasa natural.

    **4. Kombinasi Fade + Tempo**:
    - Gabungan efek ini menunjukkan perubahan signifikan pada dinamika suara.
    - Rata-rata amplitudo setelah efek kombinasi: audio 1 = {combined_rms[0]:.4f}, audio 2 = {combined_rms[1]:.4f}

    Dari waveform yang divisualisasikan, terlihat jelas bahwa efek fade membuat transisi masuk dan keluar menjadi lebih lembut. Sementara itu, perubahan tempo tidak hanya mempengaruhi durasi, tapi juga pola amplitudo. Kombinasi fade dan tempo memberikan variasi ritmis yang bisa disesuaikan untuk kebutuhan artistik atau komunikasi audio.
    """)

def streamlit_ui():
    st.title("🎧 Eksperimen Audio Interaktif")

    st.write("Upload 2 file audio (.mp3) untuk memulai eksperimen.")
    uploaded_files = st.file_uploader("Pilih dua file audio", accept_multiple_files=True, type=["mp3"])

    if uploaded_files and len(uploaded_files) == 2:
        st.success("Berhasil mengunggah 2 file audio!")
        audio_paths = [save_audio(f) for f in uploaded_files]

        # 1. Fade
        st.header("1. Efek Fade In/Out")
        fade_paths = [apply_fade(p) for p in audio_paths]
        for path in fade_paths:
            st.audio(path)
            plot_waveform(path, f"Waveform: {os.path.basename(path)}")

        # 2. Tempo
        st.header("2. Perubahan Tempo (0.75x dan 1.5x)")
        slow_paths = [change_tempo(p, 0.75) for p in audio_paths]
        fast_paths = [change_tempo(p, 1.5) for p in audio_paths]

        st.subheader("📂 Audio Slow (0.75x)")
        for path in slow_paths:
            st.audio(path)
            plot_waveform(path, f"Waveform: {os.path.basename(path)}")

        st.subheader("📂 Audio Fast (1.5x)")
        for path in fast_paths:
            st.audio(path)
            plot_waveform(path, f"Waveform: {os.path.basename(path)}")

        # 3. Podcast Intro/Outro
        st.header("3. Simulasi Podcast (Intro & Outro)")
        podcast_paths = simulate_podcast_intro_outro(audio_paths)
        st.subheader("🎙️ Opening (Fade In dari 10 detik awal audio 1)")
        st.audio(podcast_paths[0])
        plot_waveform(podcast_paths[0], "Podcast Opening")

        st.subheader("🎙️ Closing (Fade Out dari 10 detik akhir audio 2)")
        st.audio(podcast_paths[1])
        plot_waveform(podcast_paths[1], "Podcast Closing")

        # 4. Gabungan Fade + Tempo
        st.header("4. Gabungan Fade + Tempo")
        combined_paths = []
        for path in audio_paths:
            faded = apply_fade(path)
            combined = change_tempo(faded, 1.2)
            combined_paths.append(combined)
            st.audio(combined)
            plot_waveform(combined, f"Gabungan Fade + Tempo ({os.path.basename(combined)})")

        # 5. Narasi otomatis
        generate_narrative(audio_paths, fade_paths, slow_paths, fast_paths, podcast_paths, combined_paths)

                # 6. Diskusi
        st.markdown("## 💬 Diskusi")
        st.markdown("""
### 1. Apa fungsi dari efek fade in dan fade out dalam produksi audio?
Efek *fade in* (perlahan muncul) dan *fade out* (perlahan menghilang) digunakan untuk membuat transisi suara menjadi lebih halus. Fungsinya antara lain:
- Menghindari suara tiba-tiba yang bisa mengganggu pendengar.
- Memberi nuansa emosional atau dramatis.
- Transisi antar track agar terdengar natural.

### 2. Apa dampak dari manipulasi kecepatan terhadap kualitas suara?
Manipulasi kecepatan berdampak pada panjang dan karakter suara:
- Jika diperlambat: suara terdengar lebih berat dan panjang.
- Jika dipercepat: suara terdengar lebih pendek dan tinggi.
Jika pitch dijaga dengan *time-stretch*, kualitas tetap bagus namun bisa timbul artefak digital.

### 3. Kapan sebaiknya menggunakan time-stretch dibanding pitch-shift?
- Gunakan *time-stretch* jika ingin mengubah durasi tanpa mengubah pitch.
- Gunakan *pitch-shift* jika ingin mengubah tinggi nada tanpa mengubah durasi.

Contoh:
- Sinkronisasi ritme → pakai *time-stretch*
- Penyesuaian harmoni → pakai *pitch-shift*

### 4. Apakah hasil audio setelah dipercepat akan berubah durasinya? Jelaskan.
Iya, durasi akan berubah.
- Jika tempo dipercepat (1.5x), durasi lebih pendek.
- Jika diperlambat (0.75x), durasi lebih panjang.

Namun dengan *time-stretch* (tanpa ubah pitch), kita bisa ubah durasi tanpa ubah nada.

### 5. Apa perbedaan hasil efek fade antara format MP3 dan WAV?
Efek fade tetap berlaku di MP3 dan WAV, namun ada perbedaan:
- **MP3**: kompresi *lossy*, efek fade bisa kurang detail karena artefak kompresi.
- **WAV**: kualitas lebih natural, cocok untuk proses editing lanjutan.
        """)


if __name__ == "__main__":
    streamlit_ui()
