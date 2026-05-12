---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
license: Complete terms in LICENSE.txt
---

# Skill Creator

Skill này cung cấp hướng dẫn để tạo các skill hiệu quả.

## Về Skill

Skill là các gói modular, tự chứa giúp mở rộng khả năng của Claude bằng cách cung cấp
kiến thức chuyên sâu, workflow và tool. Hãy nghĩ về chúng như "hướng dẫn onboarding" cho các
domain hoặc tác vụ cụ thể — chúng biến Claude từ một agent đa năng thành một agent chuyên biệt
được trang bị kiến thức thủ tục mà không một model nào có thể nắm giữ đầy đủ.

### Skill Cung Cấp Gì

1. Workflow chuyên biệt — Quy trình nhiều bước cho các domain cụ thể
2. Tích hợp tool — Hướng dẫn làm việc với định dạng file hoặc API cụ thể
3. Domain expertise — Kiến thức đặc thù công ty, schema, logic nghiệp vụ
4. Tài nguyên đóng gói — Script, tài liệu tham chiếu và asset cho tác vụ phức tạp và lặp đi lặp lại

### Cấu Trúc Của Một Skill

Mỗi skill bao gồm một file SKILL.md bắt buộc và các tài nguyên đóng gói tùy chọn:

```
skill-name/
├── SKILL.md (bắt buộc)
│   ├── Metadata YAML frontmatter (bắt buộc)
│   │   ├── name: (bắt buộc)
│   │   └── description: (bắt buộc)
│   └── Hướng dẫn Markdown (bắt buộc)
└── Bundled Resources (tùy chọn)
    ├── scripts/          - Code có thể thực thi (Python/Bash/v.v.)
    ├── references/       - Tài liệu được thiết kế để tải vào context khi cần
    └── assets/           - File dùng trong output (template, icon, font, v.v.)
```

#### SKILL.md (bắt buộc)

**Chất lượng Metadata:** `name` và `description` trong YAML frontmatter quyết định khi nào Claude sẽ sử dụng skill. Hãy cụ thể về skill làm gì và khi nào dùng nó. Dùng ngôi thứ ba (ví dụ: "This skill should be used when..." thay vì "Use this skill when...").

#### Bundled Resources (tùy chọn)

##### Scripts (`scripts/`)

Code có thể thực thi (Python/Bash/v.v.) cho các tác vụ đòi hỏi độ tin cậy xác định hoặc được viết đi viết lại nhiều lần.

- **Khi nào nên có**: Khi cùng một đoạn code được viết lại nhiều lần hoặc cần độ tin cậy xác định
- **Ví dụ**: `scripts/rotate_pdf.py` cho tác vụ xoay PDF
- **Lợi ích**: Tiết kiệm token, xác định, có thể thực thi mà không cần tải vào context
- **Lưu ý**: Script vẫn có thể cần được Claude đọc để vá lỗi hoặc điều chỉnh theo môi trường cụ thể

##### References (`references/`)

Tài liệu và tài liệu tham chiếu được thiết kế để tải vào context khi cần, giúp thông tin và tư duy của Claude.

- **Khi nào nên có**: Cho tài liệu mà Claude nên tham chiếu trong khi làm việc
- **Ví dụ**: `references/finance.md` cho schema tài chính, `references/mnda.md` cho template NDA của công ty, `references/policies.md` cho chính sách công ty, `references/api_docs.md` cho đặc tả API
- **Trường hợp dùng**: Schema database, tài liệu API, kiến thức domain, chính sách công ty, hướng dẫn workflow chi tiết
- **Lợi ích**: Giữ SKILL.md gọn nhẹ, chỉ tải khi Claude xác định cần thiết
- **Nguyên tắc tốt nhất**: Nếu file lớn (>10k từ), hãy đưa vào SKILL.md các pattern grep để tìm kiếm
- **Tránh trùng lặp**: Thông tin chỉ nên tồn tại ở SKILL.md hoặc file references, không cả hai. Ưu tiên file references cho thông tin chi tiết trừ khi nó thực sự là cốt lõi của skill — điều này giữ SKILL.md gọn nhẹ trong khi vẫn có thể khám phá thông tin mà không chiếm dụng context window. Chỉ giữ trong SKILL.md các hướng dẫn thủ tục thiết yếu và guidance workflow; chuyển tài liệu tham chiếu chi tiết, schema và ví dụ sang file references.

##### Assets (`assets/`)

File không được thiết kế để tải vào context, mà được dùng trong output Claude tạo ra.

- **Khi nào nên có**: Khi skill cần file sẽ được dùng trong output cuối cùng
- **Ví dụ**: `assets/logo.png` cho brand asset, `assets/slides.pptx` cho template PowerPoint, `assets/frontend-template/` cho boilerplate HTML/React, `assets/font.ttf` cho typography
- **Trường hợp dùng**: Template, hình ảnh, icon, boilerplate code, font, tài liệu mẫu được sao chép hoặc chỉnh sửa
- **Lợi ích**: Tách biệt tài nguyên output khỏi tài liệu, cho phép Claude dùng file mà không tải vào context

### Nguyên Tắc Thiết Kế Progressive Disclosure

Skill dùng hệ thống tải ba cấp để quản lý context hiệu quả:

1. **Metadata (name + description)** — Luôn trong context (~100 từ)
2. **Body SKILL.md** — Khi skill kích hoạt (<5k từ)
3. **Bundled resources** — Khi Claude cần (Không giới hạn*)

*Không giới hạn vì script có thể thực thi mà không cần đọc vào context window.

## Quy Trình Tạo Skill

Để tạo một skill, hãy thực hiện theo "Quy Trình Tạo Skill" theo thứ tự, bỏ qua bước chỉ khi có lý do rõ ràng chúng không áp dụng được.

### Bước 1: Hiểu Skill Qua Ví Dụ Cụ Thể

Bỏ qua bước này chỉ khi các pattern sử dụng của skill đã được hiểu rõ. Bước này vẫn có giá trị ngay cả khi làm việc với skill đã tồn tại.

Để tạo một skill hiệu quả, hãy hiểu rõ các ví dụ cụ thể về cách skill sẽ được sử dụng. Sự hiểu biết này có thể đến từ ví dụ trực tiếp của người dùng hoặc ví dụ được tạo ra và được validate bởi phản hồi của người dùng.

Ví dụ, khi xây dựng skill image-editor, các câu hỏi liên quan bao gồm:

- "Skill image-editor nên hỗ trợ chức năng gì? Chỉnh sửa, xoay, hay gì khác không?"
- "Bạn có thể cho vài ví dụ về cách skill này sẽ được sử dụng không?"
- "Tôi có thể hình dung người dùng sẽ yêu cầu như 'Xóa mắt đỏ trong ảnh này' hay 'Xoay ảnh này'. Bạn có nghĩ đến cách dùng nào khác không?"
- "Người dùng sẽ nói gì để kích hoạt skill này?"

Để tránh làm người dùng choáng ngợp, không hỏi quá nhiều câu hỏi trong một tin nhắn. Bắt đầu với câu hỏi quan trọng nhất và hỏi thêm khi cần để hiệu quả hơn.

Kết thúc bước này khi đã có cảm nhận rõ ràng về chức năng mà skill cần hỗ trợ.

### Bước 2: Lên Kế Hoạch Nội Dung Skill Có Thể Tái Sử Dụng

Để biến ví dụ cụ thể thành một skill hiệu quả, hãy phân tích từng ví dụ bằng cách:

1. Cân nhắc cách thực hiện ví dụ từ đầu
2. Xác định script, references và asset nào sẽ hữu ích khi thực hiện các workflow này lặp đi lặp lại

Ví dụ: Khi xây dựng skill `pdf-editor` để xử lý query như "Giúp tôi xoay PDF này," việc phân tích cho thấy:

1. Xoay PDF yêu cầu viết lại cùng đoạn code mỗi lần
2. Script `scripts/rotate_pdf.py` sẽ hữu ích để lưu trong skill

Ví dụ: Khi thiết kế skill `frontend-webapp-builder` cho query như "Xây cho tôi một todo app" hoặc "Xây cho tôi một dashboard theo dõi bước chân," việc phân tích cho thấy:

1. Viết frontend webapp yêu cầu cùng boilerplate HTML/React mỗi lần
2. Template `assets/hello-world/` chứa boilerplate HTML/React sẽ hữu ích để lưu trong skill

Ví dụ: Khi xây dựng skill `big-query` để xử lý query như "Hôm nay có bao nhiêu user đã đăng nhập?" việc phân tích cho thấy:

1. Truy vấn BigQuery yêu cầu khám phá lại schema và mối quan hệ bảng mỗi lần
2. File `references/schema.md` ghi lại schema bảng sẽ hữu ích để lưu trong skill

Để xây dựng nội dung skill, hãy phân tích từng ví dụ cụ thể để tạo danh sách tài nguyên tái sử dụng cần có: script, references và assets.

### Bước 3: Khởi Tạo Skill

Đến bước này, đã đến lúc thực sự tạo skill.

Bỏ qua bước này chỉ khi skill đang được phát triển đã tồn tại và cần lặp lại hoặc đóng gói. Trong trường hợp đó, hãy chuyển sang bước tiếp theo.

Khi tạo skill mới từ đầu, luôn chạy script `init_skill.py`. Script này tiện lợi tạo ra thư mục template skill mới tự động bao gồm mọi thứ skill cần, giúp quá trình tạo skill hiệu quả và đáng tin cậy hơn nhiều.

Cách dùng:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

Script sẽ:

- Tạo thư mục skill tại đường dẫn được chỉ định
- Tạo template SKILL.md với frontmatter đúng và placeholder TODO
- Tạo thư mục tài nguyên mẫu: `scripts/`, `references/`, và `assets/`
- Thêm file mẫu trong mỗi thư mục có thể tùy chỉnh hoặc xóa

Sau khi khởi tạo, hãy tùy chỉnh hoặc xóa SKILL.md đã tạo và các file mẫu khi cần.

### Bước 4: Chỉnh Sửa Skill

Khi chỉnh sửa skill (mới tạo hoặc đã tồn tại), hãy nhớ rằng skill đang được tạo cho một instance Claude khác sử dụng. Tập trung vào việc đưa vào thông tin sẽ hữu ích và không hiển nhiên với Claude. Hãy cân nhắc kiến thức thủ tục, chi tiết đặc thù domain hoặc asset tái sử dụng nào sẽ giúp instance Claude khác thực thi các tác vụ này hiệu quả hơn.

#### Bắt Đầu với Nội Dung Skill Tái Sử Dụng

Để bắt đầu triển khai, hãy bắt đầu với các tài nguyên tái sử dụng đã xác định ở trên: file `scripts/`, `references/` và `assets/`. Lưu ý bước này có thể cần input từ người dùng. Ví dụ, khi triển khai skill `brand-guidelines`, người dùng có thể cần cung cấp brand asset hoặc template để lưu trong `assets/`, hoặc tài liệu để lưu trong `references/`.

Ngoài ra, hãy xóa các file mẫu và thư mục không cần thiết cho skill. Script khởi tạo tạo file mẫu trong `scripts/`, `references/` và `assets/` để minh họa cấu trúc, nhưng hầu hết skill sẽ không cần tất cả.

#### Cập Nhật SKILL.md

**Phong cách viết:** Viết toàn bộ skill theo **dạng imperative/infinitive (hướng dẫn bắt đầu bằng động từ)**, không dùng ngôi thứ hai. Dùng ngôn ngữ khách quan, mang tính hướng dẫn (ví dụ: "To accomplish X, do Y" thay vì "You should do X" hay "If you need to do X"). Điều này duy trì sự nhất quán và rõ ràng cho AI sử dụng.

Để hoàn thành SKILL.md, hãy trả lời các câu hỏi sau:

1. Mục đích của skill là gì, trong vài câu?
2. Khi nào skill nên được sử dụng?
3. Trên thực tế, Claude nên sử dụng skill như thế nào? Tất cả nội dung skill tái sử dụng đã phát triển ở trên đều phải được tham chiếu để Claude biết cách dùng chúng.

### Bước 5: Đóng Gói Skill

Khi skill đã sẵn sàng, nó nên được đóng gói thành file zip có thể phân phối để chia sẻ với người dùng. Quá trình đóng gói tự động validate skill trước để đảm bảo đáp ứng mọi yêu cầu:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Chỉ định thư mục output tùy chọn:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

Script đóng gói sẽ:

1. **Validate** skill tự động, kiểm tra:
   - Định dạng YAML frontmatter và các trường bắt buộc
   - Quy ước đặt tên skill và cấu trúc thư mục
   - Tính đầy đủ và chất lượng của description
   - Tổ chức file và tham chiếu tài nguyên

2. **Đóng gói** skill nếu validation pass, tạo file zip được đặt tên theo skill (ví dụ: `my-skill.zip`) bao gồm tất cả file và duy trì cấu trúc thư mục đúng để phân phối.

Nếu validation thất bại, script sẽ báo lỗi và thoát mà không tạo gói. Sửa các lỗi validation và chạy lại lệnh đóng gói.

### Bước 6: Lặp Lại

Sau khi kiểm thử skill, người dùng có thể yêu cầu cải thiện. Điều này thường xảy ra ngay sau khi dùng skill, với context còn tươi về cách skill đã hoạt động.

**Workflow lặp lại:**
1. Dùng skill trên tác vụ thực tế
2. Nhận thấy những khó khăn hoặc kém hiệu quả
3. Xác định SKILL.md hoặc bundled resources cần cập nhật như thế nào
4. Triển khai thay đổi và kiểm thử lại
