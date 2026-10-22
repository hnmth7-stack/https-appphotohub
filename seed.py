import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash as gph
from core import q, x, init

def seed():
    init()
    if q("select 1 from users", one=True):
        return
    R = random.Random(7)
    T = date.today()
    d = lambda n: (T - timedelta(days=n)).isoformat()

    def user(email, name, role, pw):
        return x("insert into users(email,name,pw,role,created) values(?,?,?,?,?)", (email, name, gph(pw), role, d(200)))

    user("admin@photohub.vn", "Quản trị PhotoHub", "admin", "admin123")
    me = user("user@photohub.vn", "Lan Anh", "customer", "user123")
    names = ["Minh Khoa", "Thu Hà", "Quang Huy", "Bảo Ngọc", "Đức Anh", "Mai Linh", "Tuấn Kiệt", "Phương Vy", "Hải Đăng", "Ngọc Diệp"]
    custs = [me] + [user(f"kh{i}@mail.vn", n, "customer", "user123") for i, n in enumerate(names)]

    P = [("partner@photohub.vn", "Lumen Studio", "studio", "TP.HCM", "Studio ánh sáng tự nhiên, concept vintage và portrait."),
         ("hanoi@photohub.vn", "Mộc Film", "photographer", "Hà Nội", "Chụp film couple và graduation ngoài trời."),
         ("makeup@photohub.vn", "Mi Beauty", "makeup", "TP.HCM", "Trang điểm phong cách Hàn Quốc cho buổi chụp."),
         ("rent@photohub.vn", "CamRent Saigon", "equipment", "TP.HCM", "Cho thuê máy ảnh, lens và đèn.")]
    pid = []
    for e, n, k, c, b in P:
        u = user(e, n, "partner", "partner123")
        pid.append(x("insert into partners(user_id,name,kind,city,bio) values(?,?,?,?,?)", (u, n, k, c, b)))

    SERV = [(0, "Gói Portrait 60 phút", "Portrait", 1200000, "Chụp chân dung trong studio, 20 ảnh chỉnh màu."),
            (0, "Sinh nhật Vintage", "Vintage", 1800000, "Concept sinh nhật vintage, kèm phụ kiện và phông nền."),
            (1, "Couple kiểu Hàn", "Couple", 2500000, "Chụp cặp đôi tông sáng, phong cách Hàn Quốc."),
            (1, "Graduation ngoài trời", "Graduation", 1500000, "Kỷ yếu, tốt nghiệp ngoài trời, 90 phút."),
            (2, "Makeup chụp ảnh", "Makeup", 600000, "Trang điểm và làm tóc cho buổi chụp.")]
    svc = []
    for pi, t, st, pr, ds in SERV:
        sid = x("insert into services(partner_id,title,style,price,descr) values(?,?,?,?,?)", (pid[pi], t, st, pr, ds))
        svc.append((sid, pid[pi], pr))

    def book(u, si, off, status):
        s = svc[si]
        bid = x("insert into bookings(user_id,service_id,partner_id,day,status,total,deposit_paid,created) values(?,?,?,?,?,?,?,?)",
                (u, s[0], s[1], d(off), status, s[2], 0 if status == "pending" else 1, d(max(off + 5, 0))))
        if status == "completed" and R.random() < 0.45:
            x("insert into reviews(booking_id,partner_id,rating,comment) values(?,?,?,?)", (bid, s[1], R.choice([4, 5, 5, 5, 3]), "Buổi chụp rất ổn."))

    for _ in range(120):
        book(R.choice(custs[:8]), R.randrange(5), int(R.triangular(3, 180, 3)), "completed")
    for u in custs[8:]:
        for _ in range(R.randint(1, 2)):
            book(u, R.randrange(5), R.randint(75, 150), "completed")
    book(me, 0, -6, "confirmed")
    book(custs[1], 2, -3, "pending")

    ITEMS = [(0, "Phông nền giấy trắng", "backdrop", 3, 4, 5, 3, 150000), (0, "Giấy in Polaroid", "print", 25, 60, 30, 4, 12000),
             (0, "Đèn Godox 200W", "light", 4, 12, 3, 2, 200000), (3, "Sony A7 III", "camera", 6, 10, 3, 1, 500000),
             (3, "Lens 50mm f/1.8", "lens", 8, 7, 4, 1, 150000), (3, "Chân máy Tripod", "tripod", 5, 14, 4, 1, 80000)]
    for pi, name, cat, base, final, ro, lead, price in ITEMS:
        iid = x("insert into items(partner_id,name,cat,stock,reorder,lead,price) values(?,?,?,?,?,?,?)", (pid[pi], name, cat, final, ro, lead, price))
        tot = 0
        for w in range(26):
            dem = max(0, round(base * (1 + 0.03 * w) + R.gauss(0, base * 0.2) + (base * 0.5 if w % 4 == 3 else 0)))
            if dem:
                x("insert into moves(item_id,kind,qty,day,note) values(?,?,?,?,?)", (iid, "out", dem, d((25 - w) * 7 + R.randint(0, 5)), "Theo đơn đặt"))
            tot += dem
        x("insert into moves(item_id,kind,qty,day,note) values(?,?,?,?,?)", (iid, "in", tot + final, d(190), "Nhập kho ban đầu"))

    for pi, cap, st, c1, c2 in [(0, "Sinh nhật vintage trong ánh sáng tự nhiên", "Vintage", "#C9A66B", "#5B3A29"),
                                 (1, "Couple tông kem, phong cách Hàn", "Couple", "#E8D5C4", "#8C6A5D"),
                                 (1, "Graduation lúc hoàng hôn", "Graduation", "#F2A65A", "#264653"),
                                 (0, "Portrait đen trắng, một nguồn sáng", "Portrait", "#D9D9D9", "#222222"),
                                 (1, "Film 35mm ở Đà Lạt", "Film", "#9BB7A0", "#2F4538"),
                                 (0, "Hậu trường: dựng ánh sáng studio", "Studio", "#AEC3D8", "#1D3557")]:
        x("insert into posts(partner_id,caption,style,c1,c2,likes) values(?,?,?,?,?,?)", (pid[pi], cap, st, c1, c2, R.randint(20, 300)))

    for n, c, s, st, v in [("Công ty ABC", "abc@mail.vn", "Facebook", 0, 8000000), ("Trường THPT Lê Quý Đôn", "ql@school.vn", "Giới thiệu", 2, 15000000), ("Hoàng Nam", "0901234567", "TikTok", 1, 2500000)]:
        x("insert into leads(name,contact,source,stage,value) values(?,?,?,?,?)", (n, c, s, st, v))

    for n, t, p, a in [("Cảnh báo sắp hết hàng theo dự báo", "low_stock", 0, "Tạo việc nhập hàng và báo đối tác"),
                       ("Đơn mới: thông báo đối tác", "booking_created", 0, "Gửi thông báo cho đối tác"),
                       ("Hoàn thành: cộng PhotoPoint", "booking_completed", 0, "Cộng 1 điểm cho mỗi 10.000đ"),
                       ("Khách im lặng quá 60 ngày", "inactive", 60, "Gắn thẻ at_risk và gửi ưu đãi"),
                       ("Nhắc cọc sau 1 ngày", "deposit", 1, "Nhắc khách thanh toán cọc")]:
        x("insert into rules(name,trigger,param,action) values(?,?,?,?)", (n, t, p, a))
