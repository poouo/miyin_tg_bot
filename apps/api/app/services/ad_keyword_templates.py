"""Built-in ad keyword template packs.

A template is only a curated list of keywords. Importing one into a group simply
creates normal `AdKeyword` rules, so everything can be edited, disabled or deleted
afterwards. Matching is a lower-case substring check (see `match_ad_keyword`),
so keywords are stored lower-case and kept specific on purpose.

Display names / descriptions live in `core/i18n.py` under `ad_tpl_<id>_name` and
`ad_tpl_<id>_desc`.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import AdKeyword
from apps.api.app.services.ad_keyword_service import _split_keywords, list_ad_keywords

# `ad_keywords.keyword` is VARCHAR(255); stay well below it.
MAX_RULE_KEYWORD_LENGTH = 240

RISK_STANDARD = "standard"
RISK_STRICT = "strict"


@dataclass(frozen=True)
class AdKeywordTemplate:
    id: str
    risk: str
    keywords: tuple[str, ...]


TEMPLATES: tuple[AdKeywordTemplate, ...] = (
    AdKeywordTemplate(
        id="gambling",
        risk=RISK_STANDARD,
        keywords=(
            "菠菜", "博彩", "百家乐", "时时彩", "六合彩", "赌场", "网赌", "赌博网站",
            "真人视讯", "体育投注", "彩票代理", "澳门新葡京", "皇冠体育", "太阳城娱乐",
            "线上娱乐", "娱乐城", "棋牌代理", "开户送", "注册送", "首充", "返水", "彩金",
            "下注", "包赢", "稳赚不赔", "casino", "sportsbook", "bet365", "1xbet",
            "online betting",
        ),
    ),
    AdKeywordTemplate(
        id="part_time",
        risk=RISK_STANDARD,
        keywords=(
            "刷单", "兼职", "日结", "日赚", "日入", "轻松赚钱", "在家赚钱", "手机赚钱",
            "躺赚", "副业", "高薪兼职", "垫付佣金", "高额返佣", "做任务赚", "点赞赚钱",
            "打字员", "无需经验", "时间自由", "宝妈兼职", "学生兼职", "刷信誉", "刷好评",
            "代刷", "刷粉",
        ),
    ),
    AdKeywordTemplate(
        id="adult",
        risk=RISK_STANDARD,
        keywords=(
            "约炮", "同城约", "上门服务", "外围女", "楼凤", "裸聊", "福利姬", "成人视频",
            "成人资源", "无码", "色情", "援交", "包夜", "学生妹", "一夜情", "性服务",
            "看片", "福利群", "裸照", "偷拍", "porn", "onlyfans", "nsfw",
        ),
    ),
    AdKeywordTemplate(
        id="fraud_finance",
        risk=RISK_STANDARD,
        keywords=(
            "杀猪盘", "跑分", "洗钱", "代收代付", "套现", "无抵押贷款", "网贷", "黑户贷款",
            "征信修复", "刷流水", "资金盘", "带单", "荐股", "内幕消息", "保本收益",
            "高回报", "日息", "月息", "老师带单", "喊单", "提现失败", "冻结资金", "解冻费",
            "缴纳保证金", "充值返利", "稳赚",
        ),
    ),
    AdKeywordTemplate(
        id="black_industry",
        risk=RISK_STANDARD,
        keywords=(
            "办证", "假证", "假发票", "代开发票", "出售银行卡", "银行卡出售", "四件套",
            "实名账号", "号商", "接码", "协议号", "出售账号", "手机卡出售", "社工库",
            "查档", "短信轰炸", "呼死你", "爆粉", "引流脚本", "采集群成员", "拉人软件",
            "群发软件", "代考", "替考", "黑客服务", "追回被骗资金", "追款",
        ),
    ),
    AdKeywordTemplate(
        id="en_spam",
        risk=RISK_STANDARD,
        keywords=(
            "crypto signals", "forex signal", "binary option", "guaranteed profit",
            "earn $", "make money online", "passive income", "investment plan",
            "double your", "claim your reward", "free usdt", "click here to claim",
            "join my channel", "cheap followers",
        ),
    ),
    AdKeywordTemplate(
        id="tg_promo",
        risk=RISK_STRICT,
        keywords=(
            "t.me/+", "t.me/joinchat", "telegram.me/joinchat", "点击加入", "点击进群",
            "进群领", "扫码进群", "私聊我", "私我", "加我", "联系客服", "招代理", "代理招募",
            "招商加盟", "免费领取", "限时福利", "广告位", "互推", "全网首发", "飞机号",
            "加微信", "加vx", "加v信", "加qq", "威信", "薇信", "微信号", "资源群",
        ),
    ),
    AdKeywordTemplate(
        id="crypto",
        risk=RISK_STRICT,
        keywords=(
            "usdt换汇", "u换汇", "承兑", "币商", "搬砖套利", "usdt搬砖", "合约带单",
            "点位喊单", "空投领取", "钱包授权", "授权盗币", "助记词", "假usdt", "跑u", "洗u",
        ),
    ),
)

_TEMPLATES_BY_ID = {template.id: template for template in TEMPLATES}


def get_template(template_id: str) -> AdKeywordTemplate | None:
    return _TEMPLATES_BY_ID.get(template_id)


def chunk_keywords(keywords: list[str], max_length: int = MAX_RULE_KEYWORD_LENGTH) -> list[str]:
    """Pack keywords into comma separated rule strings no longer than `max_length`."""
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for keyword in keywords:
        added = len(keyword) + (1 if current else 0)
        if current and current_length + added > max_length:
            chunks.append(",".join(current))
            current = []
            current_length = 0
            added = len(keyword)
        current.append(keyword)
        current_length += added
    if current:
        chunks.append(",".join(current))
    return chunks


async def _existing_keywords(db: AsyncSession, chat_id: int) -> set[str]:
    existing: set[str] = set()
    for rule in await list_ad_keywords(db, chat_id):
        existing.update(_split_keywords(rule.keyword))
    return existing


async def describe_templates(db: AsyncSession, chat_id: int) -> list[dict]:
    existing = await _existing_keywords(db, chat_id)
    return [
        {
            "id": template.id,
            "risk": template.risk,
            "keyword_count": len(template.keywords),
            "imported_count": sum(1 for keyword in template.keywords if keyword in existing),
        }
        for template in TEMPLATES
    ]


async def apply_templates(
    db: AsyncSession,
    chat_id: int,
    template_ids: list[str],
    *,
    delete_message: bool = True,
    mute_user: bool = False,
    mute_minutes: int = 30,
    ban_user: bool = False,
    ban_minutes: int = 1440,
    apply_to_mentions: bool = False,
) -> dict[str, int]:
    """Create rules for the chosen templates, skipping keywords the group already has."""
    selected: list[AdKeywordTemplate] = []
    for template_id in template_ids:
        template = get_template(template_id)
        if template is None:
            raise ValueError(f"unknown ad keyword template: {template_id}")
        if template not in selected:
            selected.append(template)

    existing = await _existing_keywords(db, chat_id)
    created_rules = 0
    added_keywords = 0
    skipped_keywords = 0

    for template in selected:
        fresh: list[str] = []
        for keyword in template.keywords:
            if keyword in existing:
                skipped_keywords += 1
                continue
            existing.add(keyword)
            fresh.append(keyword)
        for chunk in chunk_keywords(fresh):
            db.add(
                AdKeyword(
                    chat_id=chat_id,
                    keyword=chunk,
                    enabled=True,
                    delete_message=delete_message,
                    mute_user=mute_user,
                    mute_minutes=mute_minutes,
                    ban_user=ban_user,
                    ban_minutes=ban_minutes,
                    apply_to_mentions=apply_to_mentions,
                )
            )
            created_rules += 1
        added_keywords += len(fresh)

    if created_rules:
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise
    return {
        "created_rules": created_rules,
        "added_keywords": added_keywords,
        "skipped_keywords": skipped_keywords,
    }
