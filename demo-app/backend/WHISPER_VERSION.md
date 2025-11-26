# Whisper-based Stream Processor Alternative

Đây là phiên bản thay thế sử dụng **Whisper STT** từ audio thay vì Gemini Vision.

## Ưu điểm Whisper:
- Trích xuất chính xác từ **audio** (không phụ thuộc OCR)
- Có timestamp chính xác cho từng đoạn
- Whisper model có thể chạy local

## Nhược điểm:
- Nặng hơn (base model ~1GB RAM, medium ~5GB)
- Chậm hơn khi không có GPU
- Không phân tích được hình ảnh (chỉ audio)

## Cài đặt:

```bash
# Backend requirements (thêm vào requirements.txt)
openai-whisper
ffmpeg-python
```

## Code:

Xem file `backend/whisper_processor.py` (đã tạo sẵn trong repo)

## Khi nào dùng Whisper vs Gemini:

| Tiêu chí | Whisper | Gemini Vision |
|----------|---------|---------------|
| Nguồn dữ liệu | Audio only | Video frames (hình ảnh) |
| Độ chính xác STT | Cao | Trung bình (OCR) |
| Tốc độ | Chậm (local) | Nhanh (API) |
| Chi phí | Free (local) | Tính theo token |
| Yêu cầu phần cứng | GPU tốt | Không |

**Khuyến nghị hiện tại**: Tiếp tục dùng **Gemini** cho demo vì:
- Không cần GPU
- Phân tích cả hình ảnh (headlines, ticker)
- Nhanh hơn
- Dễ scale
