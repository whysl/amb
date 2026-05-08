from app.database import engine, SessionLocal, Base
from app.models.models import Department, User, Subject
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Department).count() > 0:
        db.close()
        return

    company = Department(code="company", name="威高商管公司", level=1, sort_order=1)
    minsuqun = Department(code="minsuqun", name="民俗邨", parent_id=None, level=2, sort_order=2)
    shiguangcheng = Department(code="shiguangcheng", name="时光城", parent_id=None, level=2, sort_order=3)
    whgc = Department(code="whgc", name="威高广场", parent_id=None, level=2, sort_order=4)

    db.add_all([company, minsuqun, shiguangcheng, whgc])
    db.flush()

    minsuqun.parent_id = company.id
    shiguangcheng.parent_id = company.id
    whgc.parent_id = company.id

    depts_l3 = [
        Department(code="zhaoshang", name="招商中心", parent_id=whgc.id, level=3, sort_order=1),
        Department(code="safety", name="安全环境部·安全", parent_id=whgc.id, level=3, sort_order=2),
        Department(code="environment", name="安全环境部·环境", parent_id=whgc.id, level=3, sort_order=3),
        Department(code="catering", name="餐饮部", parent_id=whgc.id, level=3, sort_order=4),
        Department(code="engineering", name="工程服务部", parent_id=whgc.id, level=3, sort_order=5),
        Department(code="marketing", name="营销推广部", parent_id=whgc.id, level=3, sort_order=6),
        Department(code="service", name="顾客服务部", parent_id=whgc.id, level=3, sort_order=7),
        Department(code="cinema", name="开乐影城", parent_id=whgc.id, level=3, sort_order=8),
        Department(code="general", name="综合管理部", parent_id=whgc.id, level=3, sort_order=9),
    ]
    db.add_all(depts_l3)
    db.flush()

    dept_map = {d.code: d.id for d in db.query(Department).all()}

    admin = User(
        username="admin",
        password_hash=pwd_context.hash("1234"),
        real_name="系统管理员",
        role="super_admin",
        department_id=dept_map["company"],
        is_active=True
    )
    db.add(admin)

    all_subjects = []

    def S(code, name, category, formula=None, is_calculated=False, is_required=False, sort_order=0, unit="元"):
        return {"code": code, "name": name, "category": category, "formula": formula,
                "is_calculated": is_calculated, "is_required": is_required, "sort_order": sort_order, "unit": unit}

    subjects_minsuqun = [
        S("A1", "回款", "收入", sort_order=1),
        S("A2", "租金收入", "收入", sort_order=2),
        S("A3", "物业费收入", "收入", sort_order=3),
        S("A4", "兴源收入", "收入", sort_order=4),
        S("A5", "研学团建", "收入", sort_order=5),
        S("A6", "车场收入", "收入", sort_order=6),
        S("A7", "能源收入", "收入", sort_order=7),
        S("A", "总销售额", "收入", formula="A1+A2+A3+A4+A5+A6+A7", is_calculated=True, sort_order=8),
        S("B1", "推广费", "变动费用", sort_order=10),
        S("B2", "其他成本", "变动费用", sort_order=11),
        S("B3", "招待费", "变动费用", sort_order=12),
        S("B4", "差旅费", "变动费用", sort_order=13),
        S("B", "变动费用合计", "变动费用", formula="B1+B2+B3+B4", is_calculated=True, sort_order=14),
        S("C", "边界利益", "边界利益", formula="A-B", is_calculated=True, sort_order=20),
        S("D1", "能源费", "固定费用", sort_order=21),
        S("D2", "外包费", "固定费用", sort_order=22),
        S("D3", "维保费", "固定费用", sort_order=23),
        S("D4", "维修费", "固定费用", sort_order=24),
        S("D5", "办公费", "固定费用", sort_order=25),
        S("D6", "折旧费", "固定费用", sort_order=26),
        S("D7", "其他固定费用", "固定费用", sort_order=27),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3+D4+D5+D6+D7", is_calculated=True, sort_order=28),
        S("E", "附加价值", "附加价值", formula="C-D", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F3", "分摊时间", "时间", unit="小时", sort_order=42),
        S("F", "总时间", "时间", formula="F1+F2+F3", is_calculated=True, unit="小时", sort_order=43),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
        S("K", "应收账款余额", "重要指标", sort_order=51),
        S("L", "人均销售额", "重要指标", formula="A/J", is_calculated=True, sort_order=52),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="C-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_shiguangcheng = [
        S("A1", "租金收入", "收入", sort_order=1),
        S("A2", "物业费收入", "收入", sort_order=2),
        S("A3", "推广收入", "收入", sort_order=3),
        S("A4", "停车收入", "收入", sort_order=4),
        S("A5", "其他收入", "收入", sort_order=5),
        S("A6", "能源收入", "收入", sort_order=6),
        S("A", "总销售额", "收入", formula="A1+A2+A3+A4+A5+A6", is_calculated=True, sort_order=7),
        S("B1", "推广费", "变动费用", sort_order=10),
        S("B2", "维修费", "变动费用", sort_order=11),
        S("B3", "保洁费", "变动费用", sort_order=12),
        S("B4", "安保费", "变动费用", sort_order=13),
        S("B5", "能源费", "变动费用", sort_order=14),
        S("B6", "办公费", "变动费用", sort_order=15),
        S("B7", "折旧费", "变动费用", sort_order=16),
        S("B8", "其他变动费用", "变动费用", sort_order=17),
        S("B9", "税金", "变动费用", sort_order=18),
        S("B", "费用合计", "变动费用", formula="B1+B2+B3+B4+B5+B6+B7+B8+B9", is_calculated=True, sort_order=19),
        S("E", "附加价值", "附加价值", formula="A-B", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F3", "分摊时间", "时间", unit="小时", sort_order=42),
        S("F", "总时间", "时间", formula="F1+F2+F3", is_calculated=True, unit="小时", sort_order=43),
        S("J", "回款额", "重要指标", sort_order=50),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="A-B-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_zhaoshang = [
        S("A1", "租赁收入", "收入", sort_order=1),
        S("A2", "联营收入", "收入", sort_order=2),
        S("A", "总销售额", "收入", formula="A1+A2", is_calculated=True, sort_order=3),
        S("B1", "推广费", "费用", sort_order=10),
        S("B2", "招待费", "费用", sort_order=11),
        S("B3", "差旅费", "费用", sort_order=12),
        S("B4", "办公费", "费用", sort_order=13),
        S("B5", "折旧费", "费用", sort_order=14),
        S("D", "费用合计", "费用", formula="B1+B2+B3+B4+B5", is_calculated=True, sort_order=15),
        S("E", "附加价值", "附加价值", formula="A-D", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F", "总时间", "时间", formula="F1+F2", is_calculated=True, unit="小时", sort_order=42),
        S("J", "月度签约额", "重要指标", sort_order=50),
        S("L", "人均签约额", "重要指标", formula="J/F", is_calculated=True, sort_order=51),
        S("M", "威高广场出租率", "重要指标", unit="%", sort_order=52),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="E-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_safety = [
        S("A1a", "线上支付", "收入", sort_order=1),
        S("A1b", "特来电", "收入", sort_order=2),
        S("A1c", "一点V来", "收入", sort_order=3),
        S("A1d", "积分抵扣", "收入", sort_order=4),
        S("A1e", "停简单", "收入", sort_order=5),
        S("A1", "停车收入", "收入", formula="A1a+A1b+A1c+A1d+A1e", is_calculated=True, sort_order=6),
        S("A2", "月卡收入", "收入", sort_order=7),
        S("A3", "其他收入", "收入", sort_order=8),
        S("A", "总收入", "收入", formula="A1+A2+A3", is_calculated=True, sort_order=9),
        S("D1", "能源费", "固定费用", sort_order=21),
        S("D2", "外包费", "固定费用", sort_order=22),
        S("D3", "维保费", "固定费用", sort_order=23),
        S("D4", "维修费", "固定费用", sort_order=24),
        S("D5", "办公费", "固定费用", sort_order=25),
        S("D6", "折旧费", "固定费用", sort_order=26),
        S("D7", "其他固定费用", "固定费用", sort_order=27),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3+D4+D5+D6+D7", is_calculated=True, sort_order=28),
        S("E", "附加价值", "附加价值", formula="A-D", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F3", "分摊时间", "时间", unit="小时", sort_order=42),
        S("F", "总时间", "时间", formula="F1+F2+F3", is_calculated=True, unit="小时", sort_order=43),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="E-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_environment = [
        S("A1", "绿化租摆", "收入", sort_order=1),
        S("A2", "景观灯电费", "收入", sort_order=2),
        S("A3", "垃圾桶广告", "收入", sort_order=3),
        S("A4", "场地租赁", "收入", sort_order=4),
        S("A", "总收入", "收入", formula="A1+A2+A3+A4", is_calculated=True, sort_order=5),
        S("D1", "绿化外包", "固定费用", sort_order=21),
        S("D2", "水电费", "固定费用", sort_order=22),
        S("D3", "清洁工具", "固定费用", sort_order=23),
        S("D4", "垃圾袋", "固定费用", sort_order=24),
        S("D5", "清运外包", "固定费用", sort_order=25),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3+D4+D5", is_calculated=True, sort_order=26),
        S("E", "附加价值", "附加价值", formula="A-D", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F3", "分摊时间", "时间", unit="小时", sort_order=42),
        S("F", "总时间", "时间", formula="F1+F2+F3", is_calculated=True, unit="小时", sort_order=43),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="E-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_catering = [
        S("A1", "餐饮提成", "收入", sort_order=1),
        S("A2", "其他收入", "收入", sort_order=2),
        S("A", "总收入", "收入", formula="A1+A2", is_calculated=True, sort_order=3),
        S("D1", "招待费", "固定费用", sort_order=21),
        S("D2", "差旅费", "固定费用", sort_order=22),
        S("D3", "办公费", "固定费用", sort_order=23),
        S("D4", "折旧费", "固定费用", sort_order=24),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3+D4", is_calculated=True, sort_order=25),
        S("E", "附加价值", "附加价值", formula="A-D", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F3", "分摊时间", "时间", unit="小时", sort_order=42),
        S("F", "总时间", "时间", formula="F1+F2+F3", is_calculated=True, unit="小时", sort_order=43),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="E-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_engineering = [
        S("D1", "电费公区", "固定费用", sort_order=1),
        S("D2", "空调费", "固定费用", sort_order=2),
        S("D3", "供暖费", "固定费用", sort_order=3),
        S("D4", "水费", "固定费用", sort_order=4),
        S("D5", "电费商户", "固定费用", sort_order=5),
        S("D6", "维保费", "固定费用", sort_order=6),
        S("D7", "维修费A馆", "固定费用", sort_order=7),
        S("D8", "维修费B馆", "固定费用", sort_order=8),
        S("D9", "维修费C馆", "固定费用", sort_order=9),
        S("D10", "材料费", "固定费用", sort_order=10),
        S("D11", "办公费", "固定费用", sort_order=11),
        S("D12", "电话费", "固定费用", sort_order=12),
        S("D13", "团建费", "固定费用", sort_order=13),
        S("D14", "培训费", "固定费用", sort_order=14),
        S("D15", "折旧费", "固定费用", sort_order=15),
        S("D16", "招待费", "固定费用", sort_order=16),
        S("D17", "劳保费", "固定费用", sort_order=17),
        S("D18", "差旅费", "固定费用", sort_order=18),
        S("D19", "交通费", "固定费用", sort_order=19),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3+D4+D5+D6+D7+D8+D9+D10+D11+D12+D13+D14+D15+D16+D17+D18+D19", is_calculated=True, sort_order=20),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F", "总时间", "时间", formula="F1+F2", is_calculated=True, unit="小时", sort_order=42),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
    ]

    subjects_marketing = [
        S("A1", "威高广场客流", "收入", unit="人次", sort_order=1),
        S("A2", "市场收益", "收入", sort_order=2),
        S("A", "月度销售累计", "收入", formula="A1+A2", is_calculated=True, sort_order=3),
        S("D1", "活动费", "固定费用", sort_order=21),
        S("D2", "会员费", "固定费用", sort_order=22),
        S("D3", "新媒体费", "固定费用", sort_order=23),
        S("D4", "品牌费", "固定费用", sort_order=24),
        S("D5", "广告费", "固定费用", sort_order=25),
        S("D6", "差旅费", "固定费用", sort_order=26),
        S("D7", "培训费", "固定费用", sort_order=27),
        S("D8", "交通费", "固定费用", sort_order=28),
        S("D9", "通讯费", "固定费用", sort_order=29),
        S("D10", "办公费", "固定费用", sort_order=30),
        S("D11", "团建费", "固定费用", sort_order=31),
        S("D12", "折旧费", "固定费用", sort_order=32),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3+D4+D5+D6+D7+D8+D9+D10+D11+D12", is_calculated=True, sort_order=33),
        S("E", "附加价值", "附加价值", formula="A-D", is_calculated=True, sort_order=34),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=35),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F", "总时间", "时间", formula="F1+F2", is_calculated=True, unit="小时", sort_order=42),
        S("F1_labor", "劳务费", "人工费", sort_order=60),
        S("N", "人工费", "人工费", formula="F1_labor", is_calculated=True, sort_order=61),
        S("O", "税前利润", "人工费", formula="E-N", is_calculated=True, sort_order=62),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=63),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=64),
    ]

    subjects_service = [
        S("A1", "VIP卡收入", "收入", sort_order=1),
        S("A2", "会员费收入", "收入", sort_order=2),
        S("A3", "微信积分收入", "收入", sort_order=3),
        S("A", "总收入", "收入", formula="A1+A2+A3", is_calculated=True, sort_order=4),
        S("D1", "办公费", "固定费用", sort_order=21),
        S("D2", "折旧费", "固定费用", sort_order=22),
        S("D3", "其他费用", "固定费用", sort_order=23),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3", is_calculated=True, sort_order=24),
        S("E", "附加价值", "附加价值", formula="A-D", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F3", "分摊时间", "时间", unit="小时", sort_order=42),
        S("F", "总时间", "时间", formula="F1+F2+F3", is_calculated=True, unit="小时", sort_order=43),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="E-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_cinema = [
        S("A1", "票房收入", "收入", sort_order=1),
        S("A2", "卖场收入", "收入", sort_order=2),
        S("A3", "广告收入", "收入", sort_order=3),
        S("A4", "其他收入", "收入", sort_order=4),
        S("A", "总收入", "收入", formula="A1+A2+A3+A4", is_calculated=True, sort_order=5),
        S("B1", "票房成本", "变动费用", sort_order=10),
        S("B2", "卖品成本", "变动费用", sort_order=11),
        S("B3", "激光成本", "变动费用", sort_order=12),
        S("B4", "电影专资", "变动费用", sort_order=13),
        S("B5", "促销费", "变动费用", sort_order=14),
        S("B", "变动费用合计", "变动费用", formula="B1+B2+B3+B4+B5", is_calculated=True, sort_order=15),
        S("C", "边界利益", "边界利益", formula="A-B", is_calculated=True, sort_order=20),
        S("D2", "能源费", "固定费用", sort_order=22),
        S("D3", "设备费", "固定费用", sort_order=23),
        S("D4", "其他固定费用", "固定费用", sort_order=24),
        S("D5", "财务费", "固定费用", sort_order=25),
        S("D", "固定费用合计", "固定费用", formula="D2+D3+D4+D5", is_calculated=True, sort_order=26),
        S("E", "附加价值", "附加价值", formula="C-D", is_calculated=True, sort_order=30),
        S("G", "单位时间附加价值", "附加价值", formula="E/F", is_calculated=True, sort_order=31),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F3", "分摊时间", "时间", unit="小时", sort_order=42),
        S("F", "总时间", "时间", formula="F1+F2+F3", is_calculated=True, unit="小时", sort_order=43),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
        S("N", "人工费", "人工费", sort_order=60),
        S("O", "税前利润", "人工费", formula="E-N", is_calculated=True, sort_order=61),
        S("P", "税前利润率", "人工费", formula="O/A", is_calculated=True, unit="%", sort_order=62),
        S("Q", "单位时间人工费", "人工费", formula="N/F", is_calculated=True, sort_order=63),
    ]

    subjects_general = [
        S("D1", "维保费", "固定费用", sort_order=1),
        S("D2", "福利费", "固定费用", sort_order=2),
        S("D3", "招待费", "固定费用", sort_order=3),
        S("D4", "差旅费", "固定费用", sort_order=4),
        S("D5", "通讯费", "固定费用", sort_order=5),
        S("D6", "办公费", "固定费用", sort_order=6),
        S("D7", "法务费", "固定费用", sort_order=7),
        S("D8", "系统建设费", "固定费用", sort_order=8),
        S("D9", "工会费", "固定费用", sort_order=9),
        S("D10", "团建费", "固定费用", sort_order=10),
        S("D11", "认证费", "固定费用", sort_order=11),
        S("D12", "培训费", "固定费用", sort_order=12),
        S("D", "固定费用合计", "固定费用", formula="D1+D2+D3+D4+D5+D6+D7+D8+D9+D10+D11+D12", is_calculated=True, sort_order=13),
        S("F1", "正常工作时间", "时间", unit="小时", sort_order=40),
        S("F2", "加班时间", "时间", unit="小时", sort_order=41),
        S("F", "总时间", "时间", formula="F1+F2", is_calculated=True, unit="小时", sort_order=42),
        S("J", "人数", "重要指标", unit="人", sort_order=50),
    ]

    dept_subjects_map = {
        "minsuqun": subjects_minsuqun,
        "shiguangcheng": subjects_shiguangcheng,
        "zhaoshang": subjects_zhaoshang,
        "safety": subjects_safety,
        "environment": subjects_environment,
        "catering": subjects_catering,
        "engineering": subjects_engineering,
        "marketing": subjects_marketing,
        "service": subjects_service,
        "cinema": subjects_cinema,
        "general": subjects_general,
    }

    for dept_code, subjects_list in dept_subjects_map.items():
        dept_id = dept_map[dept_code]
        for s in subjects_list:
            all_subjects.append(Subject(
                department_id=dept_id,
                code=s["code"],
                name=s["name"],
                category=s["category"],
                formula=s.get("formula"),
                is_calculated=s.get("is_calculated", False),
                is_required=s.get("is_required", False),
                sort_order=s.get("sort_order", 0),
                unit=s.get("unit", "元"),
            ))

    db.add_all(all_subjects)
    db.commit()
    db.close()
    print("数据库初始化完成！")
