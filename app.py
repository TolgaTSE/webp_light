import streamlit as st
from PIL import Image, ImageCms
import io

st.title("ICC Profil Dönüşümü ile Işık Koşulları Simülasyonu")

# Kullanıcıdan dosyaları yükletiyoruz:
uploaded_image = st.file_uploader("Görüntü Dosyasını Yükleyin (TIFF veya WebP)", type=["tif", "tiff", "webp"])
uploaded_dst_icc = st.file_uploader("Hedef ICC Profil Dosyasını Yükleyin", type=["icc"])
uploaded_src_icc = st.file_uploader("Kaynak ICC Profil Dosyasını Yükleyin (Opsiyonel)", type=["icc"])

if uploaded_image is not None and uploaded_dst_icc is not None:
    try:
        # Görüntüyü aç ve gerekli mod dönüşümünü yap (RGB gereklidir)
        img = Image.open(uploaded_image)
        if img.mode != "RGB":
            st.write(f"Görüntü mevcut mod: {img.mode}. RGB moduna dönüştürülüyor.")
            img = img.convert("RGB")
        
        # Hedef ICC profilini yükle
        try:
            dst_profile = ImageCms.ImageCmsProfile(io.BytesIO(uploaded_dst_icc.read()))
        except Exception as e:
            st.error("Hedef ICC profil yüklenirken hata: " + str(e))
            st.stop()
        
        # Kaynak ICC profili: İlk olarak gömülü profil denenir. Eğer yoksa, kullanıcı tarafından opsiyonel olarak sağlanan profil kullanılır.
        icc_embedded = img.info.get("icc_profile")
        if icc_embedded:
            try:
                src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_embedded))
            except Exception as e:
                st.error("Gömülü ICC profil yüklenirken hata: " + str(e))
                st.stop()
        elif uploaded_src_icc is not None:
            try:
                src_profile = ImageCms.ImageCmsProfile(io.BytesIO(uploaded_src_icc.read()))
            except Exception as e:
                st.error("Kaynak ICC profil yüklenirken hata: " + str(e))
                st.stop()
        else:
            st.error("Kaynak ICC profili bulunamadı. Lütfen kaynak ICC profil dosyasını ekleyin.")
            st.stop()
        
        # ICC dönüşümünü oluştur
        try:
            transform = ImageCms.buildTransformFromOpenProfiles(src_profile, dst_profile, img.mode, img.mode)
        except Exception as e:
            st.error("Dönüşüm oluşturulurken hata: " + str(e))
            st.stop()
        
        # Dönüşümü uygulayarak simülasyonu gerçekleştir
        img_transformed = ImageCms.applyTransform(img, transform)
        
        # Dönüştürülmüş görüntüyü göster
        st.image(img_transformed, caption="Dönüştürülmüş Görüntü", use_column_width=True)
        
        # Kullanıcının görüntüyü indirebilmesi için BytesIO nesnesine kaydetme
        buf = io.BytesIO()
        img_transformed.save(buf, format="TIFF")
        st.download_button("Dönüştürülmüş Görüntüyü İndir", buf.getvalue(), file_name="output.tif", mime="image/tiff")
    
    except Exception as e:
        st.error("Bir hata oluştu: " + str(e))
