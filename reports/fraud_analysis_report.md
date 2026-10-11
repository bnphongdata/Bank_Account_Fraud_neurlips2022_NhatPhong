# Báo Cáo Phân Tích Dữ Liệu Gian Lận Mở Tài Khoản Ngân Hàng
Bộ dữ liệu: Bank Account Fraud (NeurIPS 2022) | 1,000,000 hồ sơ đăng ký  
Người thực hiện: Bùi Nhất Phong 

---

## 1. Bài toán thực tế: Cái khó của việc tìm gian lận mở tài khoản

Mở tài khoản trực tuyến (eKYC) giúp ngân hàng tiếp cận lượng lớn khách hàng mới trong thời gian ngắn. Tuy nhiên, việc không gặp mặt trực tiếp cũng kéo theo bài toán nhức nhối: gian lận mở tài khoản (application fraud) và danh tính giả mạo (synthetic identity).

Khi nhìn vào con số thực tế từ 1 triệu hồ sơ nộp về trong 8 tháng (từ tháng 0 đến tháng 7):
- Toàn bộ tập dữ liệu chỉ có 11,029 hồ sơ gian lận, chiếm khoảng 1.10%.
- Cứ khoảng 90 người nộp hồ sơ thì chỉ có 1 kẻ lừa đảo, còn 89 người còn lại là khách hàng chân chính.

Cái khó lớn nhất trong bài toán này không nằm ở công nghệ, mà nằm ở sự cân bằng giữa trải nghiệm người dùng và quản trị rủi ro:
- Nếu đặt ra quá nhiều câu hỏi, bắt xác minh phức tạp để chặn sạch gian lận, 89 khách hàng tốt sẽ thấy phiền toái và bỏ sang ngân hàng khác.
- Ngược lại, nếu thả lỏng để duyệt nhanh cho khách hàng, chỉ cần lọt lưới 1% kẻ xấu cũng đủ gây thất thoát hàng chục tỷ đồng nợ xấu khi chúng chiếm đoạt hạn mức thẻ tín dụng rồi bốc hơi.

---

## 2. Dữ liệu thực tế cho chúng ta thấy những gì?

Sau khi làm sạch 1 triệu dòng dữ liệu và bóc tách các đặc trưng, có 3 điểm đáng chú ý nhất về hành vi của kẻ gian:

### Gian lận có xu hướng leo thang qua các tháng
Tỷ lệ gian lận không đứng yên mà tăng đều theo thời gian:
- Tháng 2 có tỷ lệ gian lận thấp nhất, chỉ 0.88%.
- Nhưng đến tháng 6 và tháng 7, con số này nhảy lên 1.34% và 1.48% (tăng gần 70% so với tháng 2).

Điều này phản ánh một thực tế quen thuộc trong ngành: những tháng đầu ra mắt sản phẩm hoặc luồng mở tài khoản mới, kẻ gian thường nộp thăm dò. Khi phát hiện ra các quy tắc kiểm duyệt tự động còn lỏng lẻo ở khâu nào, chúng sẽ tổ chức nộp ồ ạt ở các tháng sau.

### Kẻ gian thường dùng máy tính hơn là điện thoại
Hệ điều hành thiết bị là yếu tố phân hóa rủi ro rất rõ:
- Hồ sơ nộp từ máy tính Windows có tỷ lệ gian lận lên tới 2.47%, cao gấp gần 5 lần so với Linux (0.51%) và gần gấp đôi MacOS (1.40%).
- Lý do thực tế: Các đối tượng gian lận chuyên nghiệp hiếm khi ngồi thao tác bằng tay trên từng chiếc điện thoại. Chúng thường ngồi máy tính chạy các tool giả lập, dùng bot điền form tự động hàng loạt hoặc dùng máy ảo để thay đổi thông số mạng.

### Dấu hiệu của những danh tính chắp vá
Khi đối soát thông tin cá nhân và nơi ở của người nộp đơn:
- Nhóm hồ sơ khai báo tình trạng nhà ở mã BA có tỷ lệ gian lận 3.75%, cao gấp hơn 3 lần mức bình thường.
- Đáng ngờ hơn, nếu hồ sơ vừa thuộc nhóm BA vừa hoàn toàn không có lịch sử địa chỉ cũ, tỷ lệ gian lận vọt lên tới 7.29% (gấp hơn 6.6 lần tỷ lệ thông thường).
- Những hồ sơ này thường đi kèm với tên email không mấy liên quan đến họ tên, dùng nhà cung cấp email miễn phí và có địa chỉ IP từ nước ngoài.

Đây là chân dung kinh điển của dạng danh tính chắp vá: kẻ gian lấy tên của một người, ghép với số điện thoại rác và địa chỉ mới đăng ký để qua mặt bước tra cứu tín dụng ban đầu, sau đó chiếm đoạt hạn mức rồi bỏ mặc tài khoản.

---

## 3. Từ những quy tắc thủ công đến mô hình máy học

### Giới hạn của việc bắt gian lận bằng quy tắc cứng (Rules)
Ban đầu, đội vận hành có thể nghĩ đến việc viết vài câu lệnh điều kiện đơn giản:
- Quy tắc 1: Nếu dùng Windows, nhà ở nhóm BA và không có địa chỉ cũ thì đánh dấu nghi vấn. Quy tắc này bắt được 3,170 vụ gian lận, độ chính xác đạt 7.29%.
- Quy tắc 2: Tên email lệch họ tên, dùng email miễn phí và truy cập từ IP nước ngoài thì đánh dấu nghi vấn. Quy tắc này bắt được 152 vụ, độ chính xác 3.69%.

Vấn đề là các quy tắc cứng này chỉ bắt được những trường hợp quá lộ liễu. Kẻ gian chỉ cần đổi loại thiết bị hoặc mượn một địa chỉ khác là lọt lưới ngay. Chúng ta không thể ngồi viết hàng trăm quy tắc thủ công để bao quát hết 44 thuộc tính của một hồ sơ.

### Hiệu quả thực tế của mô hình LightGBM
Thay vì dùng quy tắc tĩnh, chúng tôi xây dựng mô hình phân lớp LightGBM trên 44 biến đặc trưng. Mô hình được huấn luyện trên dữ liệu 6 tháng đầu (tháng 0 đến 5) và đem kiểm tra độc lập trên 96,843 hồ sơ của tháng 7 (tập kiểm thử ngoài thời gian):

- Chỉ số ROC-AUC đạt 0.8933, cho thấy mô hình phân tách hồ sơ tốt và xấu rất sắc bén.
- Chỉ số Recall tại ngưỡng FPR 5% đạt 55.32%: chỉ cần đội ngũ thẩm định kiểm tra kỹ 5% số hồ sơ bị mô hình chấm điểm rủi ro cao nhất, chúng ta đã chặn đứng được hơn một nửa (790 trong tổng số 1,428 vụ gian lận của tháng 7).
- Độ chính xác (Precision) đạt 14.22%: trong top 5% hồ sơ bị cảnh báo, cứ khoảng 7 hồ sơ sẽ tóm trúng 1 hồ sơ gian lận (cao gấp 10 lần so với việc kiểm tra ngẫu nhiên).
- Quan trọng nhất là 95% khách hàng bình thường còn lại hoàn toàn không bị làm phiền, được duyệt nhanh chóng mà không gặp trở ngại nào.

---

## 4. Đề xuất quy trình xử lý thực tế cho ngân hàng (3 Luồng phê duyệt)

Trên môi trường thực tế, không nên dùng một ngưỡng cắt cứng (như xác suất trên 0.5 là từ chối). Thay vào đó, chúng tôi đề xuất phân thành 3 luồng dựa trên điểm xác suất rủi ro P do mô hình trả về:

```text
               [Hồ sơ đăng ký mở tài khoản]
                             │
                  [Mô hình chấm điểm P]
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
   P < 0.15           0.15 <= P < 0.65          P >= 0.65
   Luồng Xanh            Luồng Vàng             Luồng Đỏ
 (Chiếm ~92% đơn)      (Chiếm ~6% đơn)       (Chiếm ~2% đơn)
       │                     │                     │
 Duyệt tự động         Xác thực thêm         Từ chối thẳng
  (Dưới 2 phút)     (Video call, chip CCCD)   (Vào danh sách đen)
```

1. Luồng Xanh (Rủi ro rất thấp - chiếm khoảng 92% hồ sơ): Khách hàng có thông tin nhất quán, thiết bị tin cậy. Phê duyệt tự động và cấp tài khoản ngay trong vòng 2 phút.
2. Luồng Vàng (Cần kiểm tra thêm - chiếm khoảng 6% hồ sơ): Hồ sơ có một số điểm bất thường nhưng chưa đủ căn cứ để kết luận lừa đảo. Hệ thống kích hoạt bước xác thực bổ sung: yêu cầu quay video nhận diện khuôn mặt trực tiếp (liveness detection), quét NFC căn cước công dân gắn chip hoặc yêu cầu cung cấp hóa đơn sinh hoạt.
3. Luồng Đỏ (Rủi ro rất cao - chiếm khoảng 2% hồ sơ): Các trường hợp điểm rủi ro vượt ngưỡng an toàn. Từ chối ngay lập tức, chặn thiết bị và lưu vào danh sách đen để phòng ngừa các đợt tấn công tiếp theo.

---

## 5. Kết luận

Bằng cách chuyển từ các quy tắc thủ công sang mô hình học máy phân tầng, ngân hàng giải quyết được hai mục tiêu tưởng chừng đối nghịch:
1. Bảo vệ dòng vốn: Chặn trước hơn một nửa số vụ gian lận mở thẻ hoặc vay thấu chi ngay từ vòng đăng ký ban đầu.
2. Giữ chân khách hàng: Đảm bảo hơn 90% khách hàng lương thiện được trải nghiệm dịch vụ mở tài khoản trực tuyến mượt mà, nhanh gọn.

---

## 6. Các tài nguyên sẵn có trong dự án

- Dữ liệu sạch đã qua tiền xử lý: data/processed/clean_base.csv
- Mã nguồn huấn luyện: src/models/train_model.py và src/models/evaluate.py
- File mô hình đã huấn luyện: models/lgbm_fraud_model.joblib
- Biểu đồ trực quan: Nằm trong thư mục reports/figures/ (bao gồm biểu đồ xu hướng theo tháng, phân bố thiết bị, ma trận tương quan, biểu đồ đặc trưng quan trọng và đường cong ROC/PR)
- Notebooks chạy thử: notebooks/01_eda_and_cleaning.ipynb, notebooks/02_fraud_deep_dive.ipynb, notebooks/03_model_training_and_evaluation.ipynb
