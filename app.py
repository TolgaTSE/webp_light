import streamlit as st
from PIL import Image, ImageCms
import io

st.title("ICC Profil Dönüşümü ile Işık Koşulları Simülasyonu")

# Kullanıcıdan dosya yükleme widget'ları
uploaded_image = st.file_uploader("Görüntü Dosyasını Yükleyin (TIFF veya WebP)", type=["tif", "tiff", "webp"])
uploaded_icc = st.file_uploader("Hedef ICC Profil Dosyasını Yükleyin", type=["icc"])

if uploaded_image is not None and uploaded_icc is not None:
    try:
        # Görüntüyü aç
        img = Image.open(uploaded_image)

        # Görüntünün renk modu RGB değilse, RGB'ye dönüştür
        if img.mode != "RGB":
            st.write(f"Görüntü mevcut mod: {img.mode}. RGB moduna dönüştürülüyor.")
            img = img.convert("RGB")

        # Hedef ICC profilini yükle
        try:
            icc_data = uploaded_icc.read()
            dst_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_data))
        except Exception as e:
            st.error("Hedef ICC profil yüklenirken hata: " + str(e))
            st.stop()

        # Kaynak profil: Görüntünün gömülü ICC profili var mı kontrol et
        icc_embedded = img.info.get("icc_profile")
        if icc_embedded:
            try:
                src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_embedded))
            except Exception as e:
                st.write("Gömülü ICC profil yüklenemedi, varsayılan sRGB profili kullanılıyor. Detay: " + str(e))
                src_profile = ImageCms.createProfile("sRGB")
        else:
            st.write("Gömülü ICC profil bulunamadı. Varsayılan sRGB profili kullanılıyor.")
            src_profile = ImageCms.createProfile("sRGB")

        # ICC dönüşümünü oluştur (kaynak ve hedef profiller arasında)
        try:
            transform = ImageCms.buildTransformFromOpenProfiles(src_profile, dst_profile, img.mode, img.mode)
        except Exception as e:
            st.error("Dönüşüm oluşturulurken hata: " + str(e))
            st.stop()

        # Dönüşümü uygulayarak simülasyonu gerçekleştir
        img_transformed = ImageCms.applyTransform(img, transform)

        # Dönüştürülmüş görüntüyü göster
        st.image(img_transformed, caption="Dönüştürülmüş Görüntü", use_column_width=True)

        # İndirmek için BytesIO nesnesine kaydet
        buf = io.BytesIO()
        img_transformed.save(buf, format="TIFF")
        byte_im = buf.getvalue()
        st.download_button("Dönüştürülmüş Görüntüyü İndir", byte_im, file_name="output.tif", mime="image/tiff")

    except Exception as e:
        st.error("Bir hata oluştu: " + str(e))
