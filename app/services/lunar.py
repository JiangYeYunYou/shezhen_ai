from datetime import date, datetime
from typing import Optional
from zhDateTime import DateTime

from app.schemas.lunar import LunarCalendarResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

FESTIVALS = {
    (1, 1): "元旦",
    (2, 14): "情人节",
    (3, 8): "妇女节",
    (3, 12): "植树节",
    (4, 1): "愚人节",
    (5, 1): "劳动节",
    (5, 4): "青年节",
    (6, 1): "儿童节",
    (7, 1): "建党节",
    (8, 1): "建军节",
    (9, 10): "教师节",
    (10, 1): "国庆节",
    (10, 2): "国庆节",
    (10, 3): "国庆节",
    (10, 4): "国庆节",
    (10, 5): "国庆节",
    (10, 6): "国庆节",
    (10, 7): "国庆节",
    (12, 25): "圣诞节",
}

LUNAR_FESTIVALS = {
    (1, 1): "春节",
    (1, 15): "元宵节",
    (5, 5): "端午节",
    (7, 7): "七夕节",
    (8, 15): "中秋节",
    (9, 9): "重阳节",
    (12, 30): "除夕",
}

YI_JI_DATA = {
    "甲子": {"yi": ["祭祀", "祈福", "出行", "嫁娶"], "ji": ["动土", "安葬"]},
    "乙丑": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "丙寅": {"yi": ["出行", "嫁娶", "开市"], "ji": ["祭祀", "祈福"]},
    "丁卯": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "破土"]},
    "戊辰": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "己巳": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "庚午": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "辛未": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "壬申": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "癸酉": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "甲戌": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "乙亥": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "丙子": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "丁丑": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "戊寅": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "己卯": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "庚辰": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "辛巳": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "壬午": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "癸未": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "甲申": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "乙酉": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "丙戌": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "丁亥": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "戊子": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "己丑": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "庚寅": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "辛卯": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "壬辰": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "癸巳": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "甲午": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "乙未": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "丙申": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "丁酉": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "戊戌": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "己亥": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "庚子": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "辛丑": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "壬寅": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "癸卯": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "甲辰": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "乙巳": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "丙午": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "丁未": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "戊申": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "己酉": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "庚戌": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "辛亥": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "壬子": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "癸丑": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "甲寅": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "乙卯": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "丙辰": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "丁巳": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "戊午": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "己未": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "庚申": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
    "辛酉": {"yi": ["祭祀", "祈福", "求嗣"], "ji": ["动土", "修造"]},
    "壬戌": {"yi": ["祭祀", "修造", "动土"], "ji": ["嫁娶", "开市"]},
    "癸亥": {"yi": ["出行", "嫁娶", "开市"], "ji": ["安葬", "破土"]},
}

LUNAR_MONTH_NAMES = {
    1: "正月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月",
    7: "七月", 8: "八月", 9: "九月", 10: "十月", 11: "冬月", 12: "腊月"
}

LUNAR_DAY_NAMES = {
    1: "初一", 2: "初二", 3: "初三", 4: "初四", 5: "初五",
    6: "初六", 7: "初七", 8: "初八", 9: "初九", 10: "初十",
    11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五",
    16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
    21: "廿一", 22: "廿二", 23: "廿三", 24: "廿四", 25: "廿五",
    26: "廿六", 27: "廿七", 28: "廿八", 29: "廿九", 30: "三十"
}


class LunarService:
    def get_lunar_info(self, target_date: Optional[date] = None) -> LunarCalendarResponse:
        if target_date is None:
            target_date = date.today()
        
        dt = DateTime(
            target_date.year, 
            target_date.month, 
            target_date.day
        )
        zh_date = dt.chinesize
        
        lunar_month = zh_date.chinese_calendar_month
        lunar_day = zh_date.chinese_calendar_day
        
        lunar_month_name = LUNAR_MONTH_NAMES.get(lunar_month, f"{lunar_month}月")
        lunar_day_name = LUNAR_DAY_NAMES.get(lunar_day, f"{lunar_day}日")
        lunar_date_str = f"农历{lunar_month_name}{lunar_day_name}"
        
        ganzhi_year = zh_date.gānzhī_year
        ganzhi_day = zh_date.gānzhī_day
        ganzhi_str = f"{ganzhi_year}年 {ganzhi_day}日"
        
        weekday = WEEKDAYS[target_date.weekday()]
        
        season = self._get_season(target_date.month)
        
        festivals = self._get_festivals(target_date, lunar_month, lunar_day)
        
        yi_ji = YI_JI_DATA.get(ganzhi_day, {"yi": ["诸事皆宜"], "ji": ["无"]})
        
        return LunarCalendarResponse(
            date=target_date.strftime("%Y-%m-%d"),
            lunar_date=lunar_date_str,
            ganzhi=ganzhi_str,
            weekday=weekday,
            season=season,
            festival=festivals,
            yi=yi_ji["yi"],
            ji=yi_ji["ji"]
        )
    
    def _get_season(self, month: int) -> str:
        if month in [12, 1, 2]:
            return "冬"
        elif month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        else:
            return "秋"
    
    def _get_festivals(self, solar_date: date, lunar_month: int, lunar_day: int) -> str:
        festivals = []
        
        solar_key = (solar_date.month, solar_date.day)
        if solar_key in FESTIVALS:
            festivals.append(FESTIVALS[solar_key])
        
        lunar_key = (lunar_month, lunar_day)
        if lunar_key in LUNAR_FESTIVALS:
            festivals.append(LUNAR_FESTIVALS[lunar_key])
        
        return "、".join(festivals) if festivals else "无"


lunar_service = LunarService()
