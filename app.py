import streamlit as st
from PIL import Image, ImageCms
import io

st.title("ICC Profil Dönüşümü ile Işık Simülasyonu")

# Kullanıcıdan dosyaları alın
uploaded_image = st.file_uploader("Görüntü Dosyasını Yükleyin (TIFF veya WebP)", type=["tif", "tiff", "webp"])
uploaded_icc = st.file_uploader("Hedef ICC Profil Dosyasını Yükleyin", type=["icc"])

if uploaded_image is not None and uploaded_icc is not None:
    try:
        # Görüntüyü aç
        img = Image.open(uploaded_image)
        # Eğer dosya WebP ise, RGB'ye çevir
        if uploaded_image.name.lower().endswith('.webp'):
            st.write("WebP formatı algılandı; görüntü RGB formatına dönüştürülüyor.")
            img = img.convert("RGB")
        
        # Hedef ICC profilini oku
        icc_profile_data = uploaded_icc.read()
        dst_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_profile_data))
        
        # Kaynak profil: Görüntüde gömülü profil varsa kullan; yoksa sRGB oluştur.
        icc_embedded = img.info.get("icc_profile")
        if icc_embedded:
            src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_embedded))
        else:
            src_profile = ImageCms.createProfile("sRGB")
        
        # ICC dönüşümü oluştur
        transform = ImageCms.buildTransformFromOpenProfiles(src_profile, dst_profile, img.mode, img.mode)
        img_transformed = ImageCms.applyTransform(img, transform)
        
        # Dönüştürülmüş görüntüyü göster
        st.image(img_transformed, caption="Dönüştürülmüş Görüntü", use_column_width=True)
        
        # Kullanıcının görüntüyü indirebilmesi için çıktı oluştur
        buf = io.BytesIO()
        img_transformed.save(buf, format="TIFF")
        byte_im = buf.getvalue()
        st.download_button("Dönüştürülmüş Görüntüyü İndir", byte_im, file_name="output.tif", mime="image/tiff")
    except Exception as e:
        st.error("Bir hata oluştu: " + str(e))
