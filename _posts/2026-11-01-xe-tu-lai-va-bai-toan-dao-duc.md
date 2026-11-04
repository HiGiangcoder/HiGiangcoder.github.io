---
title: "Xe tự lái và bài toán đạo đức"
date: 2026-11-01 09:00:00 +0700
topic: triet-hoc
description: "Khi một chiếc xe tự lái buộc phải chọn giữa hai tai nạn, ai sẽ là người quyết định? Bài toán xe điện không chỉ hỏi về kỹ thuật — nó hỏi về quyền lực và trách nhiệm."
tags: [đạo đức học, xe tự lái, bài toán xe điện]
---

Hãy tưởng tượng một chiếc xe tự lái đang chạy trong đường hầm. Phanh hỏng. Phía trước là năm người đi bộ. Nếu xe chuyển làn, nó sẽ đâm vào một người đang đứng bên lề. Không có lựa chọn nào không gây thương tích.

Con người sẽ làm gì trong tình huống ấy? Và quan trọng hơn: **ai là người lập trình cho chiếc xe quyết định?**

## Bài toán xe điện

Tình huống trên là một biến thể của **bài toán xe điện** (trolley problem), được Philippa Foot đưa ra năm 1967 và Judith Jarvis Thomson phát triển sau đó. Phiên bản gốc: một chiếc xe điện mất phanh đang lao về phía năm người bị trói trên đường ray. Bạn đứng cạnh một cần gạt. Nếu gạt, xe sẽ chuyển sang đường ray khác và giết một người. Bạn có gạt không?

Điều thú vị là hầu hết mọi người nói *có*: giết một người để cứu năm người có vẻ là lựa chọn đúng. Nhưng nếu thay đổi tình huống — thay vì gạt cần, bạn phải đẩy một người to lớn xuống đường ray để chặn xe — phần lớn lại nói *không*. Cùng một kết quả, cùng một số người chết, nhưng trực giác của ta thay đổi.

Các nhà triết học dùng những thí nghiệm tư tưởng này không phải để tìm ra câu trả lời duy nhất, mà để làm lộ ra những nguyên tắc đạo đức ngầm mà ta đang dùng.

## Ba cách nhìn

| Cách tiếp cận | Câu hỏi trung tâm | Trong bài toán xe điện | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| Hệ quả luận | Hành động nào tạo ra nhiều điều tốt nhất? | Gạt cần, cứu năm người | Rõ ràng, có thể tính toán | Có thể biện minh cho việc hy sinh thiểu số |
| Nghĩa vụ luận | Mình có đang làm trái bổn phận hoặc xâm phạm quyền của ai không? | Có thể không gạt, vì không được dùng người như phương tiện | Bảo vệ phẩm giá cá nhân | Có thể dẫn tới kết quả tệ hơn về tổng thể |
| Đức hạnh luận | Một người khôn ngoan và công bằng sẽ làm gì? | Chú ý đến bối cảnh, động cơ và nhân cách | Giữ được sự phức tạp của đời sống | Ít đưa ra chỉ dẫn cụ thể |

Không có cách nào hoàn hảo. Hệ quả luận có thể biến con người thành những con số. Nghĩa vụ luận có thể bám vào nguyên tắc đến mức bỏ qua hậu quả. Đức hạnh luận có thể quá mơ hồ để lập trình.

## Khi thí nghiệm tư tưởng gặp dữ liệu

Năm 2018, nhóm nghiên cứu của Edmond Awad công bố *The Moral Machine experiment* trên tạp chí *Nature*. Họ tạo ra một nền tảng trực tuyến cho phép hàng triệu người trên thế giới quyết định xe tự lái nên làm gì trong các tình huống tai nạn. Kết quả cho thấy con người khá nhất quán ở một số điểm: ưu tiên cứu người hơn động vật, cứu nhiều người hơn ít người, cứu trẻ em hơn người già. Nhưng cũng có những khác biệt đáng kể giữa các nền văn hóa.

Nghiên cứu này không cho ta biết điều gì là đúng. Nó chỉ cho thấy rằng **không có một bảng xếp hạng đạo đức chung cho toàn nhân loại**. Bất kỳ hệ thống nào được triển khai toàn cầu cũng sẽ phải chọn giữa những giá trị đang xung đột với nhau.

## Vấn đề thật sự

Bài toán xe điện thường được kể như một câu đố về lựa chọn giữa hai tai nạn. Nhưng trong đời thực, câu hỏi khó hơn nằm ở những chỗ khác:

- **Xác suất, không phải chắc chắn.** Xe tự lái không biết chắc ai sẽ chết. Nó phải ước lượng rủi ro trong điều kiện thiếu thông tin.
- **Phân phối rủi ro.** Một thuật toán có thể vô tình khiến một nhóm người — người đi bộ, người đi xe máy, người già, người khuyết tật — gánh rủi ro nhiều hơn.
- **Lỗ hổng trách nhiệm.** Khi xe gây tai nạn, ai chịu trách nhiệm: lập trình viên, nhà sản xuất, chủ xe, hay thuật toán? Pháp luật hiện tại thường được thiết kế cho một người lái có thể bị quy trách nhiệm.
- **Ai được quyền quyết định?** Nếu một công ty tư nhân viết ra quy tắc đạo đức cho hàng triệu chiếc xe, thì đó là quyết định chính trị, không chỉ là quyết định kỹ thuật.

Đây là lý do các nhà đạo đức học không chỉ hỏi “xe nên chọn ai?” mà còn hỏi “ai được ngồi vào bàn thiết kế?”, “người bị ảnh hưởng có tiếng nói không?”, và “làm sao để những quy tắc ấy có thể bị chất vấn?”

## Không có thuật toán nào thay thế được tranh luận

Công nghệ có thể giúp ta mô phỏng hàng triệu kịch bản và đánh giá hậu quả tốt hơn. Nhưng nó không thể tự quyết định điều gì đáng giá hơn điều gì. Đó là câu hỏi đạo đức, và câu hỏi đạo đức cần con người tranh luận với nhau — một cách công khai, có lý lẽ, và có khả năng sửa sai.

Bài toán xe điện không cần một đáp án cuối cùng. Nó cần ta nhận ra rằng mỗi lần chọn một thuật toán, ta đang chọn một hệ giá trị. Và nếu ta không chọn, người khác sẽ chọn hộ.

[^1]: Foot, P. (1967). The problem of abortion and the doctrine of the double effect. *Oxford Review*, 5, 5–15.
[^2]: Thomson, J. J. (1976). Killing, letting die, and the trolley problem. *The Monist*, 59(2), 204–217.
[^3]: Awad, E., Dsouza, S., Kim, R., et al. (2018). The Moral Machine experiment. *Nature*, 563, 59–64.
[^4]: Matthias, A. (2004). The responsibility gap: Ascribing responsibility for the actions of learning automata. *Ethics and Information Technology*, 6(3), 175–183.
