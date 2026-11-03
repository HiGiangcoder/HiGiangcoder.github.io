---
title: Kỹ thuật viết blog và văn xuôi tiếng Việt
date: 2026-10-23 09:00:00 +0700
topic: khac
description: "Tập trung vào cơ chế tạo lập văn bản: bố cục, trình tự thông tin, dẫn dắt, ngôi kể, điểm nhìn, cảnh, chuyển cảnh, đoạn văn và nhịp câu. Không đi sâu vào chính tả, lỗi thường gặp hay bài tập luyện viết."
tags:
  - "#kithuat"
---

# 1. Mô hình thiết kế văn bản

Có thể xem một văn bản là sự phối hợp của bốn lớp:

\[ `\text{Văn bản}`{=tex} = `\text{Mục đích}`{=tex} +
`\text{Cấu trúc}`{=tex} + `\text{Trình tự thông tin}`{=tex} +
`\text{Giọng kể}`{=tex} \]

  Lớp        Câu hỏi thiết kế
  ---------- ------------------------------------------------
  Mục đích   Muốn người đọc biết, tin, cảm nhận hay làm gì?
  Cấu trúc   Nội dung được chia thành những phần nào?
  Trình tự   Ý nào xuất hiện trước, ý nào được trì hoãn?
  Giọng kể   Ai đang nói, nói với ai, từ vị trí nào?

Ba loại chuyển động thường gặp:

-   **Logic:** vấn đề → giải thích → bằng chứng → kết luận.
-   **Thời gian:** quá khứ → hiện tại → tương lai; hoặc hồi tưởng, dự
    báo.
-   **Nhận thức:** điều người đọc đã biết → thông tin mới → nhận thức
    được điều chỉnh.

Mẫu thiết kế trước khi viết:

``` text
Chủ đề:
Độc giả:
Mục đích:
Câu hỏi trung tâm:
Luận đề / thông điệp:
Cấu trúc dự kiến:
Giọng văn:
```

Ví dụ:

``` text
Chủ đề: Đọc paper Computer Vision
Độc giả: Sinh viên mới làm nghiên cứu
Mục đích: Hướng dẫn quy trình đọc có hệ thống
Câu hỏi: Nên đọc paper theo thứ tự nào?
Luận đề: Không nhất thiết đọc tuần tự từ đầu đến cuối
Cấu trúc: Vấn đề → quy trình → ví dụ → giới hạn
Giọng văn: Trực tiếp, kỹ thuật
```

------------------------------------------------------------------------

# 2. Các bố cục blog thường gặp

## 2.1. Problem -- Solution

**Công thức:** Vấn đề → nguyên nhân → giải pháp → cách áp dụng.

Dùng cho bài hướng dẫn, bài tư vấn và bài giải quyết vấn đề.

``` text
# Cách [giải quyết vấn đề]

1. Vấn đề
   - Biểu hiện
   - Vì sao đáng quan tâm?

2. Nguyên nhân
   - Nguyên nhân A
   - Nguyên nhân B

3. Giải pháp
   - Giải pháp A
   - Giải pháp B

4. Triển khai
   - Bước 1
   - Bước 2
   - Bước 3

5. Giới hạn / ngoại lệ
6. Kết luận
```

Ví dụ: bài "Cách tổ chức ghi chú khi đọc paper" mở đầu bằng tình trạng
ghi chú rời rạc, phân tích nguyên nhân, trình bày cấu trúc ghi chú, minh
họa bằng một paper và nêu giới hạn của phương pháp.

## 2.2. Inverted Pyramid --- Kim tự tháp ngược

**Công thức:** Thông tin quan trọng nhất → chi tiết hỗ trợ → bối cảnh.

Phù hợp với tin tức, thông báo, bài cập nhật và bài tổng hợp nhanh.

``` text
Đoạn 1: Kết quả / thông tin quan trọng nhất
Đoạn 2: Chi tiết quyết định
Đoạn 3: Bối cảnh
Đoạn 4: Lịch sử và thông tin bổ sung
```

Người đọc có thể dừng sớm mà vẫn nắm được nội dung cốt lõi.

## 2.3. Chronological --- Theo thời gian

**Công thức:** Trạng thái ban đầu → biến cố → diễn biến → kết quả.

Dùng cho nhật ký, hồi ký, tường thuật và hành trình dự án.

``` text
1. Trạng thái ban đầu
2. Sự kiện khởi phát
3. Các bước diễn biến
4. Bước ngoặt
5. Kết quả
6. Nhận thức sau sự kiện
```

Không bắt buộc kể đúng thứ tự xảy ra. Có thể mở bằng kết quả rồi quay
lại nguyên nhân.

## 2.4. Compare -- Contrast --- So sánh và đối chiếu

Có hai cách tổ chức:

**Theo đối tượng:**

``` text
1. Tiêu chí so sánh
2. Đối tượng A
3. Đối tượng B
4. So sánh tổng hợp
5. Kết luận
```

**Theo tiêu chí:**

``` text
1. Tiêu chí 1: A so với B
2. Tiêu chí 2: A so với B
3. Tiêu chí 3: A so với B
4. Tổng hợp và lựa chọn
```

Cách theo tiêu chí thường phù hợp khi người đọc cần đối chiếu trực tiếp
nhiều thuộc tính.

## 2.5. Concept -- Mechanism -- Application

**Công thức:** Khái niệm → cơ chế → ứng dụng.

Phù hợp với blog kỹ thuật, khoa học và giáo dục.

``` text
1. Khái niệm là gì?
2. Vì sao cần khái niệm này?
3. Nó hoạt động như thế nào?
4. Ví dụ tối thiểu
5. Ứng dụng
6. Giới hạn và giả định
```

Ví dụ bài Attention: định nghĩa Query/Key/Value → nêu vấn đề truy xuất
thông tin theo ngữ cảnh → trình bày công thức → đi qua ví dụ → liên hệ
Transformer → nêu giới hạn.

## 2.6. Thesis -- Argument -- Evidence

**Công thức:** Luận đề → luận điểm → bằng chứng → phân tích → phản biện.

Dùng cho bài quan điểm, tiểu luận và bài phân tích.

``` text
1. Đặt vấn đề
2. Nêu luận đề
3. Luận điểm 1 + bằng chứng + phân tích
4. Luận điểm 2 + bằng chứng + phân tích
5. Quan điểm đối lập
6. Phản hồi / điều chỉnh luận đề
7. Kết luận
```

## 2.7. Listicle --- Bài dạng danh sách

``` text
1. Mở đầu: tiêu chí lựa chọn
2. Mục 1: tên + mô tả + lý do
3. Mục 2: tên + mô tả + lý do
...
4. Tổng kết / khuyến nghị lựa chọn
```

Mỗi mục nên dùng cùng một mẫu trình bày để người đọc dễ so sánh.

## 2.8. Case Study --- Phân tích trường hợp

``` text
1. Bối cảnh
2. Mục tiêu
3. Ràng buộc
4. Quyết định
5. Quá trình thực hiện
6. Kết quả
7. Phân tích nguyên nhân
8. Bài học có thể khái quát
9. Điều không thể khái quát
```

Một trường hợp đơn lẻ không tự động chứng minh một quy luật chung; cần
phân biệt quan sát cụ thể và kết luận tổng quát.

## 2.9. Personal Essay --- Tiểu luận cá nhân

**Công thức:** Trải nghiệm cụ thể → suy nghĩ → mở rộng → quay lại trải
nghiệm.

``` text
1. Một khoảnh khắc hoặc ký ức
2. Câu hỏi nảy sinh từ trải nghiệm
3. Liên tưởng / phân tích / đối chiếu
4. Nhận thức thay đổi
5. Trở lại hình ảnh ban đầu với ý nghĩa mới
```

Phù hợp với blog cá nhân, tản văn và tiểu luận suy tưởng.

## 2.10. FAQ --- Hỏi đáp

``` text
1. Nêu phạm vi
2. Câu hỏi 1 → trả lời trực tiếp
3. Câu hỏi 2 → trả lời trực tiếp
4. Câu hỏi 3 → trả lời trực tiếp
5. Trường hợp ngoại lệ
```

Mỗi câu trả lời nên tương đối độc lập, tránh bắt người đọc phải đọc toàn
bài mới hiểu.

------------------------------------------------------------------------

# 3. Kỹ thuật mở bài và dẫn dắt

Mở bài có hai nhiệm vụ: tạo lý do để tiếp tục đọc và định hướng nội dung
sắp tới.

## 3.1. Mở bằng vấn đề

\[ `\text{Hiện tượng}`{=tex} `\rightarrow `{=tex}`\text{Khó khăn}`{=tex}
`\rightarrow `{=tex}`\text{Câu hỏi}`{=tex} \]

Ví dụ:

"Đọc một paper thường không khó ở việc hiểu từng câu, mà ở việc xác định
tác giả đang giải quyết vấn đề nào và đóng góp thực sự nằm ở đâu. Vậy
nên đọc paper theo trình tự nào?"

## 3.2. Mở bằng tình huống

\[ `\text{Bối cảnh cụ thể}`{=tex}
`\rightarrow `{=tex}`\text{Hành động}`{=tex}
`\rightarrow `{=tex}`\text{Trở ngại}`{=tex} \]

Ví dụ:

"Bạn mở một paper dài ba mươi trang, đọc từ Abstract đến Method, rồi
nhận ra mình chưa hiểu bài báo muốn chứng minh điều gì. Vấn đề có thể
không nằm ở tốc độ đọc, mà ở thứ tự tiếp cận."

## 3.3. Mở bằng kết luận

\[ `\text{Luận điểm}`{=tex} `\rightarrow `{=tex}`\text{Phạm vi}`{=tex}
`\rightarrow `{=tex}`\text{Lý do}`{=tex} \]

Ví dụ:

"Không nên đọc mọi paper theo thứ tự từ trang đầu đến trang cuối. Với
mục tiêu khảo sát nhanh, đọc theo câu hỏi nghiên cứu và cấu trúc lập
luận thường hữu ích hơn."

## 3.4. Mở bằng tương phản

\[ `\text{Kỳ vọng}`{=tex} `\leftrightarrow `{=tex}`\text{Thực tế}`{=tex}
`\rightarrow `{=tex}`\text{Vấn đề}`{=tex} \]

Ví dụ:

"Ta thường nghĩ viết tốt là tìm được những câu văn đẹp. Nhưng trong
nhiều trường hợp, vấn đề quan trọng hơn là sắp xếp ý sao cho người đọc
hiểu đúng."

## 3.5. Mở bằng câu hỏi

Câu hỏi nên xác định đúng vấn đề, không chỉ tạo cảm giác bí ẩn.

Ví dụ: "Điều gì khiến một đoạn văn có thể chuyển từ một ý sang ý khác mà
không tạo cảm giác đứt gãy?"

## 3.6. Mở bằng cảnh hoặc hình ảnh

Phù hợp với truyện, tản văn, hồi ký và tiểu luận cá nhân.

Ví dụ: "Chiếc đồng hồ trên tường vẫn chạy, dù căn phòng đã tắt hết đèn."

Từ hình ảnh này, người viết có thể đưa vào nhân vật, thời gian, ký ức
hoặc vấn đề suy tưởng.

## 3.7. Mở bài ba bước

``` text
Đoạn 1 — Hook:
Tình huống, câu hỏi, vấn đề hoặc luận điểm.

Đoạn 2 — Context:
Bối cảnh và lý do vấn đề đáng quan tâm.

Đoạn 3 — Scope:
Bài viết sẽ giải quyết điều gì và không giải quyết điều gì.
```

Không cần kéo dài phần dẫn nhập. Khi chủ đề đã rõ, chuyển sang nội dung
chính.

------------------------------------------------------------------------

# 4. Dẫn dắt giữa các ý và các phần

## 4.1. Chuyển ý bằng quan hệ logic

  Quan hệ         Tín hiệu ngôn ngữ
  --------------- ------------------------------------------
  Bổ sung         Ngoài ra... / Một khía cạnh khác...
  Tương phản      Tuy nhiên... / Ngược lại...
  Nguyên nhân     Bởi vì... / Nguyên nhân nằm ở...
  Kết quả         Vì vậy... / Hệ quả là...
  Cụ thể hóa      Chẳng hạn... / Xét trường hợp...
  Khái quát hóa   Từ đó có thể thấy...
  Giới hạn        Điều này chỉ đúng khi...
  Chuyển cấp độ   Ở cấp độ triển khai... / Xét rộng hơn...

Từ nối chỉ là tín hiệu; quan hệ logic phải thực sự tồn tại giữa hai
phần.

## 4.2. Câu cầu nối

\[ `\text{Kết luận đoạn trước}`{=tex} +
`\text{Câu hỏi mở ra đoạn sau}`{=tex} \]

Ví dụ:

"Như vậy, việc đọc Abstract và Introduction giúp xác định mục tiêu
nghiên cứu. Nhưng để đánh giá cách tác giả giải quyết mục tiêu ấy, cần
chuyển sang Method."

## 4.3. Từ khái quát sang cụ thể

``` text
Nhận định chung
    ↓
Phân loại
    ↓
Trường hợp cụ thể
    ↓
Ví dụ
    ↓
Phân tích ví dụ
```

Ví dụ:

"Có nhiều cách tổ chức một bài blog. Trong đó, Problem--Solution phù hợp
với bài hướng dẫn. Chẳng hạn, bài viết về quản lý ghi chú có thể bắt đầu
bằng vấn đề ghi chú phân tán, sau đó trình bày một hệ thống tổ chức cụ
thể."

## 4.4. Từ cụ thể sang khái quát

``` text
Sự kiện / ví dụ
    ↓
Quan sát
    ↓
Mẫu hình
    ↓
Nhận định tổng quát
```

Ví dụ:

"Một người có thể đọc nhiều tài liệu nhưng vẫn không giải thích được
khái niệm bằng lời của mình. Điều này cho thấy tiếp nhận thông tin và
khả năng tái cấu trúc thông tin là hai năng lực khác nhau."

## 4.5. Chuyển góc nhìn

Các trục chuyển thường gặp:

-   Cá nhân → cộng đồng.
-   Người quan sát → nhân vật.
-   Hiện tượng → nguyên nhân.
-   Hiện tại → quá khứ.
-   Lý thuyết → thực hành.
-   Ưu điểm → giới hạn.

Khi đổi góc nhìn, cần báo hiệu đủ rõ để người đọc nhận ra đối tượng hoặc
cấp độ phân tích đã thay đổi.

------------------------------------------------------------------------

# 5. Ngôi kể và điểm nhìn

Cần phân biệt:

-   **Ngôi kể:** hình thức người kể tự xưng hoặc gọi nhân vật.
-   **Điểm nhìn:** vị trí nhận thức mà từ đó câu chuyện được quan sát và
    thuật lại.
-   **Giọng kể:** thái độ và sắc thái của lời kể.

Ba yếu tố liên quan nhưng không đồng nhất.

## 5.1. Ngôi thứ nhất --- "tôi"

Người kể xuất hiện như người tham gia hoặc chứng kiến.

**Mẫu:**

``` text
Tôi quan sát / trải nghiệm
    ↓
Tôi phản ứng
    ↓
Tôi suy nghĩ
    ↓
Tôi nhận thức
```

Ví dụ:

"Tôi từng nghĩ rằng đọc nhanh đồng nghĩa với đọc hiệu quả. Sau vài lần
đọc lại cùng một đoạn mà vẫn không thể giải thích nội dung, tôi bắt đầu
chú ý nhiều hơn đến cách mình ghi chú."

Hiệu ứng thường gặp:

-   Tạo cảm giác trực tiếp và cá nhân.
-   Phù hợp với hồi ức, trải nghiệm và suy tưởng.
-   Thông tin bị giới hạn bởi điều người kể biết hoặc nhớ.

"Tôi" trong văn bản hư cấu là người kể chuyện, không nhất thiết là tác
giả ngoài đời.

## 5.2. Ngôi thứ ba giới hạn

Người kể gọi nhân vật bằng tên hoặc đại từ, nhưng thông tin chủ yếu đi
theo nhận thức của một nhân vật.

Ví dụ:

"Minh đứng trước cửa phòng. Cậu không biết bên trong có ai, nhưng vẫn
nghe thấy tiếng ghế dịch chuyển."

Người đọc chủ yếu biết điều Minh biết hoặc có thể quan sát, trừ khi văn
bản báo hiệu sự thay đổi điểm nhìn.

``` text
Nhân vật A quan sát
    ↓
Nhân vật A diễn giải
    ↓
Người đọc nhận thông tin qua A
```

Dùng khi muốn giữ bí mật, tạo đồng cảm hoặc kiểm soát lượng thông tin.

## 5.3. Ngôi thứ ba toàn tri

Người kể có thể cung cấp thông tin vượt khỏi hiểu biết của một nhân vật,
bao gồm suy nghĩ của nhiều nhân vật hoặc sự kiện ở nơi khác.

Ví dụ:

"Minh nghĩ rằng Lan đã quên cuộc hẹn. Nhưng ở phía bên kia thành phố,
Lan vẫn đang tìm cách đến đúng giờ."

Dùng khi câu chuyện cần phạm vi quan sát rộng. Cần kiểm soát việc chuyển
giữa nội tâm các nhân vật.

## 5.4. Ngôi thứ hai --- "bạn"

Người viết hướng lời kể trực tiếp đến người đọc hoặc một nhân vật được
gọi là "bạn".

Ví dụ:

"Bạn mở cánh cửa và nhận ra căn phòng không giống như lần cuối mình nhìn
thấy."

Phù hợp với hướng dẫn, nội dung tương tác, bài viết trực tiếp với độc
giả và một số thử nghiệm văn chương.

## 5.5. Kết hợp ngôi kể trong blog

Một bài blog cá nhân có thể kết hợp:

``` text
Tôi — trải nghiệm cá nhân
    ↓
Bạn — liên hệ với người đọc
    ↓
Chúng ta — khái quát vấn đề chung
```

Ví dụ:

"Tôi từng ghi chú mỗi paper theo một cách khác nhau. Có lẽ bạn cũng từng
gặp tình trạng này: thông tin nằm rải rác ở nhiều nơi, nhưng rất khó tìm
lại. Vấn đề ở đây không chỉ là công cụ ghi chú, mà còn là cấu trúc lưu
trữ."

Đây là thủ pháp tu từ, không phải yêu cầu bắt buộc.

## 5.6. Kiểm soát điểm nhìn

Khi viết một cảnh, xác định:

1.  Ai đang quan sát?
2.  Người đó biết những gì?
3.  Người đó không thể biết những gì?
4.  Thông tin được mô tả qua giác quan hay suy nghĩ nào?
5.  Khi nào và bằng cách nào điểm nhìn thay đổi?

------------------------------------------------------------------------

# 6. Tổ chức cảnh, thời gian và bối cảnh

## 6.1. Cảnh và tóm lược

**Cảnh (scene):** tái hiện sự kiện đang diễn ra, thường có hành động,
đối thoại, không gian và phản ứng.

**Tóm lược (summary):** nén một khoảng thời gian hoặc nhiều sự kiện vào
lượng văn bản ngắn.

Ví dụ cảnh:

"Lan đặt chiếc cốc xuống bàn.

'Cậu đã đọc nó chưa?'

Minh không trả lời ngay. Cậu nhìn phong bì nằm giữa hai người."

Ví dụ tóm lược:

"Trong suốt tuần đó, Minh nhiều lần định mở phong bì nhưng đều dừng
lại."

Cách lựa chọn:

-   Sự kiện quan trọng, có xung đột → viết thành cảnh.
-   Khoảng thời gian dài, ít biến chuyển → tóm lược.
-   Thông tin nền → thuyết minh ngắn.
-   Cảm xúc cần dư âm → thể hiện qua hành động hoặc chi tiết.

## 6.2. Thiết lập bối cảnh

Một cảnh có thể được thiết lập bằng bốn thành phần:

\[ `\text{Bối cảnh}`{=tex} = `\text{Thời gian}`{=tex} +
`\text{Không gian}`{=tex} + `\text{Nhân vật}`{=tex} +
`\text{Trạng thái}`{=tex} \]

Ví dụ:

"Gần nửa đêm, trong căn phòng chỉ còn ánh sáng từ màn hình máy tính,
Minh vẫn ngồi trước bản thảo chưa hoàn thành."

Câu này cung cấp thời gian, không gian, nhân vật và trạng thái. Không
nhất thiết phải mô tả đủ cả bốn yếu tố ngay câu đầu; có thể phân phối
chúng trong vài câu.

## 6.3. Chuyển bối cảnh bằng mốc thời gian

``` text
Cảnh hiện tại
    ↓
Tín hiệu thời gian
    ↓
Cảnh mới
```

Ví dụ:

"Minh đóng máy tính và bước ra khỏi phòng.

Sáng hôm sau, cậu quay lại với một quyết định khác."

Tín hiệu thường dùng:

-   Thời điểm: sáng hôm sau, ba giờ sau, vào mùa đông năm ấy.
-   Khoảng thời gian: nhiều tháng trôi qua, suốt quãng thời gian đó.
-   Hồi tưởng: ngày trước, cậu vẫn nhớ, vài năm trước.
-   Dự báo: ngày mai, về sau, cậu chưa biết rằng...

## 6.4. Chuyển bối cảnh bằng không gian

``` text
Điểm A
    ↓
Hành động di chuyển / tín hiệu chuyển cảnh
    ↓
Điểm B
    ↓
Chi tiết định vị tại B
```

Ví dụ:

"Cậu rời thư viện khi trời bắt đầu tối.

Ở cuối con phố, quán cà phê vẫn sáng đèn. Tiếng máy pha cà phê vang lên
sau lớp kính."

Nếu địa điểm mới quan trọng với diễn biến, hãy cung cấp dấu hiệu định
vị.

## 6.5. Chuyển cảnh bằng liên tưởng

Một chi tiết ở cảnh A dẫn sang cảnh B.

Ví dụ:

"Tiếng mưa gõ lên mái tôn khiến tôi nhớ đến căn nhà cũ. Ngày ấy, mỗi khi
mưa lớn, bà thường đặt những chiếc chậu dưới chỗ mái dột."

\[ `\text{Chi tiết hiện tại}`{=tex}
`\rightarrow `{=tex}`\text{Liên tưởng}`{=tex}
`\rightarrow `{=tex}`\text{Ký ức}`{=tex} \]

Phù hợp với tản văn, hồi ký và tiểu luận cá nhân.

## 6.6. Chuyển cảnh bằng đối chiếu

Ví dụ:

"Căn phòng ngày trước luôn đầy tiếng nói. Bây giờ, chỉ còn tiếng quạt
quay đều trên trần."

\[ `\text{Không gian / thời điểm A}`{=tex}
`\leftrightarrow `{=tex}`\text{Không gian / thời điểm B}`{=tex} \]

Dùng để làm nổi bật thay đổi về trạng thái, quan hệ hoặc cảm xúc.

## 6.7. Chuyển cảnh bằng vật trung gian

Một vật thể được giữ lại qua hai cảnh, đóng vai trò cầu nối.

Ví dụ:

"Minh đặt tấm ảnh vào ngăn kéo.

Nhiều năm sau, Lan tìm thấy chính tấm ảnh ấy trong căn nhà cũ."

## 6.8. Cắt cảnh và chuyển cảnh mềm

-   **Cắt cảnh:** kết thúc cảnh A, bắt đầu cảnh B ngay, không giải thích
    chuyển tiếp.
-   **Chuyển mềm:** dùng một câu hoặc đoạn trung gian để dẫn từ A sang
    B.

Cắt cảnh tạo nhịp nhanh; chuyển mềm tạo cảm giác liên tục.

## 6.9. Tần suất mô tả bối cảnh

Không cần mô tả lại toàn bộ căn phòng mỗi khi nhân vật quay lại. Chỉ
nhắc chi tiết mới, chi tiết đã thay đổi, chi tiết liên quan đến hành
động hoặc chi tiết mang ý nghĩa biểu tượng.

------------------------------------------------------------------------

# 7. Tổ chức diễn biến: cảnh, phản ứng và nhịp kể

## 7.1. Scene -- Sequel

Một chuỗi tự sự có thể được tổ chức bằng hai khối luân phiên.

**Scene:**

\[ `\text{Mục tiêu}`{=tex} `\rightarrow `{=tex}`\text{Xung đột}`{=tex}
`\rightarrow `{=tex}`\text{Kết quả}`{=tex} \]

**Sequel:**

\[ `\text{Phản ứng}`{=tex} `\rightarrow `{=tex}`\text{Suy xét}`{=tex}
`\rightarrow `{=tex}`\text{Quyết định}`{=tex} \]

Ví dụ:

-   **Scene:** Minh muốn lấy lại cuốn sổ, nhưng người giữ nó từ chối.
    Cuộc đối thoại kết thúc khi người kia rời đi.
-   **Sequel:** Minh tức giận, cân nhắc việc bỏ cuộc, rồi quyết định tìm
    một cách khác.

Scene tạo biến cố; Sequel cho thấy biến cố tác động đến nhân vật như thế
nào.

## 7.2. Xung đột

Xung đột xuất hiện khi mục tiêu gặp trở ngại.

Các dạng thường gặp:

-   Nhân vật với nhân vật.
-   Nhân vật với xã hội hoặc môi trường.
-   Nhân vật với hoàn cảnh.
-   Nhân vật với chính mình.
-   Nhân vật với giới hạn tri thức hoặc nhận thức.

Mẫu:

``` text
Nhân vật muốn X
Nhưng Y cản trở
Vì vậy nhân vật phải chọn A hoặc B
Lựa chọn dẫn đến hệ quả Z
```

## 7.3. Điều chỉnh nhịp kể

  Kỹ thuật             Hiệu ứng thường gặp
  -------------------- ------------------------------------------
  Tóm lược thời gian   Tăng tốc
  Đối thoại ngắn       Tăng tốc, tạo đối đầu
  Câu ngắn liên tiếp   Tạo nhịp gấp
  Mô tả chi tiết       Làm chậm
  Độc thoại nội tâm    Kéo dài thời gian suy nghĩ
  Khoảng lặng          Tạo độ trễ và dư âm
  Cắt cảnh             Thay đổi nhanh không gian hoặc thời điểm

Hiệu ứng còn phụ thuộc nội dung và ngữ cảnh, không chỉ độ dài câu.

## 7.4. Trì hoãn thông tin

Người viết có thể kiểm soát thời điểm tiết lộ:

-   **Ẩn thông tin:** người đọc chưa biết một sự thật.
-   **Gợi ý:** cung cấp dấu hiệu nhưng chưa giải thích.
-   **Tiết lộ:** đưa thông tin ra ánh sáng.
-   **Tái diễn giải:** thông tin mới làm thay đổi cách hiểu chi tiết cũ.

Ví dụ:

"Trên bàn có hai chiếc cốc. Minh chỉ sống một mình."

Chi tiết này tạo câu hỏi nhưng chưa xác định nguyên nhân.

------------------------------------------------------------------------

# 8. Công thức tổ chức đoạn văn

## 8.1. Đoạn lập luận

\[ P = C + E + R + T \]

-   (C): Claim --- ý chính.
-   (E): Evidence --- bằng chứng hoặc ví dụ.
-   (R): Reasoning --- phân tích vì sao bằng chứng hỗ trợ ý chính.
-   (T): Transition --- liên kết sang ý tiếp theo, nếu cần.

Ví dụ:

"Đọc paper theo câu hỏi nghiên cứu giúp người đọc xác định trọng tâm sớm
hơn. Chẳng hạn, trước khi đọc chi tiết Method, người đọc có thể xác định
bài báo đang giải quyết hạn chế nào của các phương pháp trước. Khi đã
hiểu vấn đề, các lựa chọn kỹ thuật trong Method sẽ có ngữ cảnh rõ hơn.
Từ đó, việc đọc chuyển từ tiếp nhận thông tin sang đánh giá giải pháp."

## 8.2. Đoạn miêu tả

\[ P = O + D + S + I \]

-   (O): Object --- đối tượng.
-   (D): Detail --- chi tiết cụ thể.
-   (S): Sensory impression --- cảm giác giác quan.
-   (I): Interpretation --- ý nghĩa hoặc cảm nhận, nếu cần.

Ví dụ:

"Chiếc bàn gỗ nằm sát cửa sổ. Mặt bàn có nhiều vết xước nhỏ, còn lớp
véc-ni đã ngả màu ở các cạnh. Ánh sáng buổi chiều rơi nghiêng trên những
trang giấy. Căn phòng mang vẻ cũ kỹ nhưng không lạnh lẽo."

## 8.3. Đoạn tự sự

\[ P = A + R + C \]

-   (A): Action --- hành động.
-   (R): Reaction --- phản ứng.
-   (C): Consequence --- hệ quả.

Ví dụ:

"Lan mở lá thư nhưng không đọc ngay. Cô nhìn tên người gửi rất lâu, rồi
gấp lá thư lại. Từ khoảnh khắc ấy, cuộc trò chuyện giữa hai người không
còn có thể tiếp tục như trước."

## 8.4. Đoạn giải thích

\[ P = D + M + X \]

-   (D): Definition --- định nghĩa.
-   (M): Mechanism --- cơ chế.
-   (X): Example --- ví dụ.

Ví dụ:

"Điểm nhìn là vị trí nhận thức mà từ đó câu chuyện được thuật lại. Nó
quyết định người đọc được tiếp cận thông tin nào và bị giới hạn ở đâu.
Chẳng hạn, với điểm nhìn giới hạn theo Minh, người đọc không thể biết
trực tiếp suy nghĩ của Lan nếu Minh không quan sát hoặc suy đoán được
điều đó."

## 8.5. Đoạn đối chiếu

``` text
Tiêu chí
  ├── Đối tượng A
  ├── Đối tượng B
  └── Nhận xét về khác biệt
```

Ví dụ:

"Cách kể ngôi thứ nhất tạo cảm giác trải nghiệm trực tiếp, nhưng giới
hạn thông tin theo người kể. Ngôi thứ ba toàn tri có thể mở rộng phạm vi
thông tin, song đòi hỏi kiểm soát tốt việc chuyển điểm nhìn."

------------------------------------------------------------------------

# 9. Kỹ thuật câu và nhịp văn

## 9.1. Câu thông tin

\[ `\text{Đối tượng}`{=tex} + `\text{Hành động / trạng thái}`{=tex} +
`\text{Thông tin bổ sung}`{=tex} \]

Ví dụ: "Mô hình sử dụng cơ chế attention để tổng hợp thông tin từ các
token."

Dùng cho blog kỹ thuật, thuyết minh và nội dung cần độ rõ cao.

## 9.2. Câu nhấn mạnh

\[ `\text{Thông tin nền}`{=tex}
`\rightarrow `{=tex}`\text{Ý cần nhấn}`{=tex} \]

Ví dụ: "Điều quan trọng không phải là đọc hết mọi trang, mà là hiểu được
lập luận của tác giả."

## 9.3. Câu tương phản

\[ A, `\text{nhưng }`{=tex} B \]

Ví dụ: "Bản nháp có thể chứa nhiều ý tưởng, nhưng chưa chắc đã có một
cấu trúc rõ ràng."

## 9.4. Câu nhân quả

\[ A `\rightarrow `{=tex}B \]

Ví dụ: "Vì luận điểm chưa được xác định, các đoạn văn chưa có trật tự
triển khai thống nhất."

Cần phân biệt quan hệ nhân quả thực sự với sự trùng hợp hoặc tương quan.

## 9.5. Câu nhượng bộ

\[ `\text{Dù }`{=tex} A, `\text{vẫn }`{=tex} B \]

Ví dụ: "Dù cấu trúc ba phần khá phổ biến, người viết vẫn có thể thay đổi
trình tự nếu mục đích của bài yêu cầu."

## 9.6. Câu điều kiện

\[ `\text{Nếu }`{=tex} A, `\text{thì }`{=tex} B \]

Ví dụ: "Nếu bài viết hướng đến người mới, hãy giải thích thuật ngữ trước
khi sử dụng chúng trong lập luận."

## 9.7. Câu song hành

\[ A + B + C \]

Ví dụ: "Đọc để tiếp nhận, ghi chú để tổ chức, viết để kiểm tra hiểu
biết."

## 9.8. Phối hợp độ dài câu

Mẫu nhịp:

``` text
Câu ngắn: nêu ý chính.
Câu vừa: giải thích.
Câu dài: mở rộng hoặc mô tả quan hệ phức tạp.
Câu ngắn: khóa ý hoặc tạo nhấn.
```

Ví dụ:

"Viết là lựa chọn. Người viết phải quyết định thông tin nào cần xuất
hiện trước, chi tiết nào nên được giữ lại và điều gì có thể lược bỏ để
người đọc theo dõi được mạch nội dung. Không phải mọi thứ đều cần được
kể."

------------------------------------------------------------------------

# 10. Bố cục văn xuôi và tiểu luận cá nhân

## 10.1. Từ trải nghiệm đến suy tưởng

``` text
1. Sự kiện cụ thể
2. Cảm nhận tại thời điểm đó
3. Khoảng cách thời gian / suy ngẫm
4. Liên hệ với vấn đề rộng hơn
5. Trở lại sự kiện ban đầu
```

Khung câu:

``` text
Tôi nhớ một buổi chiều...
Khi ấy, tôi nghĩ rằng...
Nhiều năm sau, tôi hiểu...
Có lẽ trải nghiệm ấy nói lên...
Bây giờ, mỗi khi nhìn thấy..., tôi lại...
```

## 10.2. Bố cục vòng tròn

``` text
Mở: hình ảnh A
Thân: câu chuyện / phân tích / biến chuyển
Kết: quay lại hình ảnh A, nhưng ý nghĩa đã thay đổi
```

Ví dụ: mở bằng một chiếc ghế trống; thân bài kể về người từng ngồi ở đó;
kết bài quay lại chiếc ghế, nhưng người kể đã nhìn sự vắng mặt theo cách
khác.

## 10.3. Bố cục tuyến tính

``` text
Sự kiện 1 → Sự kiện 2 → Sự kiện 3 → Kết quả
```

Dùng khi quan hệ thời gian và nhân quả là trọng tâm.

## 10.4. Bố cục phân mảnh

``` text
Mảnh A: hiện tại
Mảnh B: ký ức
Mảnh C: hình ảnh
Mảnh D: suy tưởng
Mảnh E: quay lại hiện tại
```

Mỗi mảnh cần liên hệ về chủ đề, hình ảnh, cảm xúc hoặc biểu tượng. Nếu
không, sự phân mảnh dễ trở thành rời rạc.

## 10.5. Bố cục luận đề mở rộng

``` text
1. Một nhận định ban đầu
2. Giải thích khái niệm
3. Xét các trường hợp
4. Đưa ra phản ví dụ
5. Điều chỉnh nhận định
6. Kết luận có giới hạn
```

Phù hợp với tiểu luận triết học, văn hóa và các bài suy tưởng.

------------------------------------------------------------------------

# 11. Chọn cấu trúc theo mục đích

  Mục đích                    Cấu trúc nên cân nhắc
  --------------------------- ---------------------------------------------
  Hướng dẫn thao tác          Problem--Solution / Step-by-step
  Giải thích khái niệm        Concept--Mechanism--Application
  Đưa tin, cập nhật           Inverted Pyramid
  Phân tích quan điểm         Thesis--Argument--Evidence
  So sánh công nghệ           Compare--Contrast
  Kể trải nghiệm              Chronological / Personal Essay
  Phân tích dự án             Case Study
  Giới thiệu nhiều lựa chọn   Listicle
  Viết truyện                 Scene--Sequel / tuyến tính / phi tuyến
  Tản văn                     Hình ảnh--liên tưởng--suy tưởng / vòng tròn
  Tiểu luận cá nhân           Trải nghiệm--phân tích--nhận thức

Quy tắc lựa chọn:

-   Người đọc cần **câu trả lời nhanh** → đưa kết luận lên đầu.
-   Người đọc cần **hiểu cơ chế** → khái niệm → cơ chế → ví dụ.
-   Người đọc cần **thực hiện một việc** → vấn đề → các bước.
-   Người đọc cần **đánh giá nhận định** → luận đề → bằng chứng → phản
    biện.
-   Người đọc cần **trải nghiệm câu chuyện** → kiểm soát điểm nhìn, cảnh
    và thời gian.
-   Bài viết nhằm **gợi suy tưởng** → có thể trì hoãn kết luận và dùng
    hình ảnh làm trục liên kết.

------------------------------------------------------------------------

# 12. Các mẫu khung tái sử dụng

## 12.1. Blog hướng dẫn

``` text
# [Kết quả người đọc muốn đạt được]

[Mở bằng vấn đề hoặc kết quả.]

## 1. Vấn đề
[Hiện trạng và khó khăn.]

## 2. Nguyên tắc
[Giải thích cơ chế hoặc tư duy nền.]

## 3. Quy trình
### Bước 1
[Mục đích → thao tác → kết quả.]

### Bước 2
[Mục đích → thao tác → kết quả.]

## 4. Ví dụ hoàn chỉnh
[Áp dụng quy trình vào một trường hợp.]

## 5. Giới hạn
[Điều kiện, ngoại lệ, đánh đổi.]

## Kết luận
[Tóm tắt và bước tiếp theo.]
```

## 12.2. Blog phân tích

``` text
# [Luận đề hoặc câu hỏi]

[Mở bằng vấn đề và nêu luận đề.]

## 1. Bối cảnh
[Định nghĩa và phạm vi.]

## 2. Luận điểm thứ nhất
[Claim → Evidence → Reasoning.]

## 3. Luận điểm thứ hai
[Claim → Evidence → Reasoning.]

## 4. Phản biện
[Quan điểm đối lập → đánh giá → phản hồi.]

## 5. Tổng hợp
[Trả lời câu hỏi trung tâm.]
```

## 12.3. Bài viết trải nghiệm

``` text
# [Tên gắn với trải nghiệm]

[Mở bằng một cảnh cụ thể.]

## [Diễn biến]
[Hành động và biến cố.]

## [Suy nghĩ]
[Phản ứng và nhận thức tại thời điểm đó.]

## [Mở rộng]
[Liên hệ với một vấn đề lớn hơn.]

## [Quay lại]
[Trở về hình ảnh hoặc sự kiện mở đầu.]
```

## 12.4. Truyện ngắn tối giản

``` text
1. Thiết lập nhân vật và bối cảnh
2. Mục tiêu của nhân vật
3. Trở ngại xuất hiện
4. Nhân vật lựa chọn
5. Hệ quả của lựa chọn
6. Bước ngoặt hoặc nhận thức mới
7. Kết thúc
```

## 12.5. Tiểu luận suy tưởng

``` text
1. Một câu hỏi hoặc nhận định
2. Giải thích vấn đề
3. Phân tích từ góc nhìn thứ nhất
4. Đối chiếu với góc nhìn khác
5. Xem xét giới hạn của nhận định
6. Đưa ra kết luận đã được điều chỉnh
```

------------------------------------------------------------------------

# 13. Nguyên tắc thiết kế văn bản

1.  **Mỗi bài có một trục:** câu hỏi, luận đề, sự kiện hoặc hình ảnh
    trung tâm.
2.  **Mỗi phần có một chức năng:** không tạo tiêu đề chỉ để chia trang.
3.  **Mỗi đoạn có một đơn vị ý nghĩa:** luận điểm, cảnh, bước giải thích
    hoặc hình ảnh.
4.  **Mỗi chuyển đoạn có quan hệ:** logic, thời gian, không gian, liên
    tưởng hoặc đối chiếu.
5.  **Điểm nhìn phải được kiểm soát:** người kể cung cấp thông tin theo
    quy tắc đã chọn.
6.  **Thông tin được phân phối có chủ đích:** biết lúc nào giải thích,
    lúc nào mô tả, lúc nào trì hoãn.
7.  **Nhịp văn là một biến số:** thay đổi độ dài câu, độ dài cảnh và mức
    độ chi tiết theo hiệu ứng mong muốn.
8.  **Cấu trúc phục vụ mục đích:** không có một bố cục duy nhất phù hợp
    với mọi bài viết.

> Công thức là công cụ thiết kế, không phải khuôn bắt buộc. Hãy chọn cấu
> trúc dựa trên trải nghiệm đọc mà văn bản cần tạo ra.