"""Tạo sơ đồ PNG và SVG chỉnh sửa được cho tài liệu đọc mã nguồn."""
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / 'so_do'
OUT.mkdir(parents=True, exist_ok=True)
FONT = ImageFont.truetype('C:/Windows/Fonts/times.ttf', 40)
SMALL = ImageFont.truetype('C:/Windows/Fonts/times.ttf', 32)
BOLD = ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf', 43)
W = 1700


class Canvas:
    def __init__(self, height):
        self.image = Image.new('RGB', (W, height), 'white')
        self.draw = ImageDraw.Draw(self.image)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}"><rect width="100%" height="100%" fill="white"/>']

    def text(self, x, y, label, small=False, bold=False):
        font = BOLD if bold else (SMALL if small else FONT)
        lines = label.split('\n')
        step = 50 if not small else 40
        for i, line in enumerate(lines):
            self.draw.text((x, y + i*step), line, font=font, fill='#152b3c', anchor='mm')
            self.svg.append(f'<text x="{x}" y="{y+i*step+12}" text-anchor="middle" font-family="Times New Roman" font-size="{font.size}" fill="#152b3c">{escape(line)}</text>')

    def box(self, x, y, w, h, label, kind='normal'):
        fill = '#edf4f8' if kind == 'normal' else '#fff4de'
        self.draw.rounded_rectangle((x,y,x+w,y+h), radius=16, fill=fill, outline='#30546b', width=3)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="#30546b" stroke-width="3"/>')
        count = len(label.split('\n'))
        self.text(x+w/2, y+h/2-(count-1)*25, label)

    def arrow(self, start, end, label='', dashed=False):
        x1,y1 = start
        x2,y2 = end
        self.draw.line((x1,y1,x2,y2), fill='#30546b', width=4)
        angle = math.atan2(y2-y1,x2-x1)
        points = [(x2,y2), (x2-20*math.cos(angle-.4),y2-20*math.sin(angle-.4)), (x2-20*math.cos(angle+.4),y2-20*math.sin(angle+.4))]
        self.draw.polygon(points, fill='#30546b')
        dash = ' stroke-dasharray="10 8"' if dashed else ''
        self.svg.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#30546b" stroke-width="4"{dash}/><polygon points="'+ ' '.join(f'{x},{y}' for x,y in points) +'" fill="#30546b"/>')
        if label:
            font = SMALL
            tw = self.draw.textlength(label, font=font)
            cx, cy = (x1+x2)/2+90, (y1+y2)/2
            self.draw.rectangle((cx-tw/2-8,cy-20,cx+tw/2+8,cy+20),fill='white')
            self.svg.append(f'<rect x="{cx-tw/2-8}" y="{cy-20}" width="{tw+16}" height="40" fill="white"/>')
            self.text(cx,cy,label,small=True)

    def save(self, name):
        self.image.save(OUT/(name+'.png'))
        (OUT/(name+'.svg')).write_text('\n'.join(self.svg+['</svg>']),encoding='utf-8')


def flow(name, title, steps, note='', error=None):
    height = 140 + len(steps)*190 + (130 if note else 0)
    c = Canvas(height)
    c.text(W/2,55,title,bold=True)
    x,w = (90,1050) if error else (150,1400)
    for i, step in enumerate(steps):
        y = 115+i*190
        c.box(x,y,w,145,step)
        if i:
            c.arrow((x+w/2,y-45),(x+w/2,y))
    if error:
        index,label = error
        y = 115+index*190
        c.box(1220,y,400,210,label,kind='error')
        c.arrow((x+w,y+72),(1220,y+72))
    if note:
        c.text(W/2,height-65,note,small=True)
    c.save(name)


def main():
    c=Canvas(1420)
    c.text(850,55,'Kiến trúc thực tế của Hồ sơ và Hợp đồng',bold=True)
    c.box(150,115,1400,140,'Trình duyệt\nHTML + employees.js')
    c.box(150,320,1400,140,'Django đọc phiên và tài khoản\nCSRF kiểm tra các yêu cầu ghi')
    c.arrow((850,255),(850,320),'GET / POST')
    c.box(150,525,1400,140,'config/urls.py → apps/employees/urls.py\nChọn hàm theo địa chỉ')
    c.arrow((850,460),(850,525))
    c.box(100,750,700,170,'Xem trang\naccess → views → bootstrap')
    c.box(900,750,700,170,'Lưu thông tin\nmutation → API → forms')
    c.arrow((600,665),(450,750),'GET')
    c.arrow((1100,665),(1250,750),'POST')
    c.box(150,1020,1400,170,'models.py + Django\nĐọc bảng / kiểm tra quy tắc / lưu dữ liệu')
    c.arrow((450,920),(500,1020))
    c.arrow((1250,920),(1200,1020))
    c.box(150,1250,1400,110,'SQLite trong db.sqlite3')
    c.arrow((850,1190),(850,1250))
    c.text(850,1390,'Kết quả xem: HTML kèm JSON. Kết quả lưu: JSON; rồi trình duyệt mở lại danh sách.',small=True)
    c.save('01_kien_truc')

    c=Canvas(1200)
    c.text(850,55,'Quan hệ giữa bốn bảng đã triển khai',bold=True)
    c.box(70,140,700,250,'NGUOIDUNG\nid, username, password băm\nrole, is_active')
    c.box(930,140,700,250,'PHONGBAN\nmaphongban, tenphongban\nmota, ngaytao')
    c.box(150,550,1400,220,'NHANVIEN\nmanv, id_taikhoan có thể trống, maphong\nThông tin cá nhân, công việc, ngày/lý do nghỉ')
    c.arrow((420,390),(500,550),'1 tài khoản ↔ 0 hoặc 1 hồ sơ')
    c.arrow((1280,390),(1200,550),'1 phòng ban → nhiều hồ sơ')
    c.box(150,950,1400,190,'HOPDONG\nmahd, manv, loại, ngày, lương, trạng thái')
    c.arrow((850,770),(850,950),'1 nhân viên → nhiều hợp đồng')
    c.save('02_quan_he_du_lieu')

    flow('03_xem_trang','Luồng xem danh sách và chi tiết',[
        'Người dùng mở một địa chỉ GET',
        'Django nhận tài khoản → kiểm tra quyền trang',
        'views chọn trang; chi tiết/sửa kiểm tra mã có tồn tại',
        'bootstrap đọc bảng và giới hạn theo tài khoản',
        'Template gắn data-page, record_id và JSON',
        'employees.js chọn handlers[page] để dựng nội dung',
    ],'Đọc dữ liệu không tạo hay sửa hồ sơ/hợp đồng.',(1,'Chưa đăng nhập: 302\nSai quyền: 403\nKhông có mã: 404'))
    flow('04_luu_ho_so','Luồng tạo hoặc sửa hồ sơ',[
        'Biểu mẫu: người dùng nhập hoặc sửa thông tin',
        'initEmployeeForm kiểm tra nhanh → submit gửi POST',
        'CSRF và mutation kiểm tra tài khoản/định dạng',
        'employee_save chọn hồ sơ → EmployeeForm kiểm tra',
        'Employee.clean → CodedHistoryModel.save → full_clean',
        'Django ghi SQLite trong transaction.atomic',
        'JSON id + thông báo → mở lại danh sách từ database',
    ],'Thêm: cấp mã NV. Sửa: giữ mã; không sửa user hoặc is_active bằng EmployeeForm.',(3,'Sai dữ liệu: 400\nTrùng bảng: 409\nLỗi database: 503'))
    flow('05_vo_hieu_hoa','Luồng vô hiệu hóa hồ sơ',[
        'Chọn Vô hiệu hóa → mở hộp ngày/lý do nghỉ',
        'initDeactivate gửi POST có mã hồ sơ',
        'API kiểm tra quyền, còn hoạt động, không phải chính mình',
        'DeactivateForm kiểm tra ngày và lý do',
        'Lưu Employee: is_active=False, ngày và lý do nghỉ',
        'Nếu có tài khoản: lưu User.is_active=False',
        'Cùng giao dịch thành công → trở lại danh sách',
    ],'Giữ hồ sơ và hợp đồng; không tự đặt hợp đồng thành Chấm dứt.',(2,'Đã nghỉ: 409\nTự khóa: 400\nNgày/lý do sai: 400'))
    flow('06_luu_hop_dong','Luồng tạo và chỉnh sửa hoặc gia hạn hợp đồng',[
        'initContractForm dựng các ô theo chế độ tạo/sửa',
        'Kiểm tra ngày, lương và trùng khoảng ở trình duyệt',
        'submit → CSRF → mutation → contract_save',
        'Mới: ContractForm. Sửa: ContractUpdateForm',
        'Contract.clean kiểm tra nhân viên và khoảng ngày',
        'Contract.save tính trạng thái → cấp/giữ mã → ghi bảng',
        'Trả JSON id → mở lại danh sách hợp đồng',
    ],'Gia hạn sửa chính bản ghi, không tạo bản hợp đồng hay lịch sử phiên bản mới.',(4,'Trùng thời gian: 400\nNhân viên nghỉ: 400\nĐã chấm dứt: 400'))
    flow('07_tim_kiem','Luồng tìm kiếm lọc và phân trang trong danh sách',[
        'Danh sách đã có state.employees hoặc state.contracts',
        'Nhập từ khóa / chọn bộ lọc → về trang 1',
        'normalize bỏ dấu và chuyển chữ thường',
        'filter chọn các bản ghi khớp tất cả điều kiện',
        'slice lấy tối đa 4 dòng của trang đang chọn',
        'Ghi HTML vào bảng → paginate nối nút đổi trang',
    ],'Bộ lọc trên danh sách không gọi API tìm kiếm; tìm kiếm đầu trang có thể mở GET mới.')
    flow('08_ca_nhan','Luồng xem hồ sơ và hợp đồng của bản thân',[
        'Đăng nhập → mở me/ hoặc me/contracts/',
        'my_profile / my_contracts nhận yêu cầu GET',
        'bootstrap lọc Employee.user = request.user',
        'Chỉ chuyển các hợp đồng thuộc hồ sơ được phép',
        'Không có hồ sơ/hợp đồng: hiển thị thông báo trống',
        'Có dữ liệu: renderMyProfile / renderMyContracts',
    ],'Với Nhân viên, dữ liệu người khác không nằm trong JSON của trang.')
    c=Canvas(1180)
    c.text(850,55,'Quyết định trạng thái khi đọc hợp đồng',bold=True)
    conditions=[('status = CHAMDUT?', 'terminated'),('start_date > hôm nay?', 'upcoming'),('end_date < hôm nay?\n(chỉ khi có ngày hết hạn)', 'expired'),('Còn 1–30 ngày đến hết hạn?\n(chỉ khi có ngày hết hạn)', 'expiring')]
    for i,(condition,result) in enumerate(conditions):
        y=140+i*205
        c.box(80,y,1010,145,condition)
        c.box(1240,y,380,145,result,kind='error')
        c.arrow((1090,y+72),(1240,y+72),'Có')
        if i:
            c.arrow((585,y-60),(585,y),'Không')
    c.box(80,975,1010,100,'active: đang hiệu lực')
    c.arrow((585,900),(585,975),'Không')
    c.text(850,1130,'Ngày hết hạn = hôm nay → active. Nhãn expiring chỉ dùng để hiển thị.',small=True)
    c.save('09_tinh_trang_thai')
    flow('10_nap_mau','Luồng nạp dữ liệu mẫu trong môi trường phát triển',[
        'seed_demo_data: kiểm tra DEBUG=True',
        'Đọc hr_demo.json, mở giao dịch chung',
        'Theo email: thêm hồ sơ chưa có, giữ hồ sơ đã có',
        'Theo nhân viên/loại/ngày: thêm hợp đồng chưa có',
        'Chỉ hồ sơ mới: áp dụng nghỉ việc trong bộ mẫu',
        'Liên kết dev_staff nếu chưa có liên kết khác',
        'Hoàn tất cả bộ mẫu; có lỗi thì hoàn tác lần nạp',
    ],'Không ghi đè bản đã sửa; không đồng bộ thay đổi giữa các SQLite của thành viên.')

    c=Canvas(1440)
    c.text(850,55,'Thứ tự gọi khi lưu một biểu mẫu',bold=True)
    xs=[180,510,850,1190,1520]
    names=['Trình duyệt','CSRF / quyền','API / Forms','models.py','SQLite']
    for x,name in zip(xs,names):
        c.box(x-150,125,300,95,name)
        c.draw.line((x,220,x,1360),fill='#bdcbd4',width=3)
        c.svg.append(f'<path d="M{x},220 L{x},1360" stroke="#bdcbd4" stroke-width="3" stroke-dasharray="10 8"/>')
    messages=[(0,1,'POST JSON + mã CSRF'),(1,2,'Yêu cầu đã hợp lệ về quyền'),(2,3,'form.is_valid → model.clean'),(3,4,'Đọc dữ liệu trùng / khoảng ngày'),(4,3,'Kết quả kiểm tra'),(3,2,'Hợp lệ'),(2,3,'form.save → model.save'),(3,4,'Ghi bản ghi trong giao dịch'),(4,3,'Bản ghi đã lưu'),(3,2,'Đối tượng có mã NV / HD'),(2,0,'JSON id (thông báo chờ GET)'),(0,2,'GET danh sách mới qua views')]
    for i,(a,b,label) in enumerate(messages):
        y=295+i*85
        c.arrow((xs[a],y),(xs[b],y))
        c.text((xs[a]+xs[b])/2,y-24,label,small=True)
    c.text(850,1400,'Các trường hợp lỗi trả về sớm; form.save chỉ chạy sau khi kiểm tra hợp lệ.',small=True)
    c.save('11_tuong_tac_luu')
    c=Canvas(1170)
    c.text(850,55,'Các liên kết đã có trong mã nguồn',bold=True)
    c.box(90,150,680,180,'accounts\nTài khoản, vai trò, đăng nhập')
    c.box(930,150,680,180,'config + Django\nPhiên, CSRF, SQLite, thông báo')
    c.box(150,490,1400,180,'employees\nHồ sơ và Hợp đồng')
    c.arrow((430,330),(550,490),'user / role')
    c.arrow((1270,330),(1160,490),'cấu hình / bảo vệ')
    c.box(90,840,680,180,'templates + static\nKhung trang, CSS, biểu tượng')
    c.box(930,840,680,180,'Các module còn lại\nChưa có liên kết dữ liệu nghiệp vụ',kind='error')
    c.arrow((550,670),(430,840),'render / nội dung')
    c.text(850,1100,'Nút Chấm công, Đào tạo, Đánh giá đang bị vô hiệu hóa trong khung trang.',small=True)
    c.save('12_lien_ket_module')
    (OUT/'danh_sach.json').write_text(json.dumps([p.stem for p in sorted(OUT.glob('*.png'))],ensure_ascii=False,indent=2),encoding='utf-8')
    print('Created 12 diagrams in PNG and editable SVG formats.')


if __name__ == '__main__':
    main()
