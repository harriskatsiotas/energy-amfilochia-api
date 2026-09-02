from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from datetime import datetime, timezone, timedelta
import random
import hashlib

app = FastAPI(
    title="FastAPI energy meters API for Municipality of Amfilochia",
    description="Energy meter readings (kWh) for 250 meters in Amfilochia. Data available at 15-minute, hourly, and daily resolution.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Meters registry — 250 meters, identified by sequential ID
# ---------------------------------------------------------------------------
METERS: list[dict] = [
    {"meter_id": "7879091612348837",  "seq": 1},
    {"meter_id": "5946796184359938",  "seq": 2},
    {"meter_id": "2597720818971586",  "seq": 3},
    {"meter_id": "9387705318016904",  "seq": 4},
    {"meter_id": "2105636349052316",  "seq": 5},
    {"meter_id": "2482030408735489",  "seq": 6},
    {"meter_id": "2211586136166354",  "seq": 7},
    {"meter_id": "4331786944192647",  "seq": 8},
    {"meter_id": "6498233778453346",  "seq": 9},
    {"meter_id": "4349917592011640",  "seq": 10},
    {"meter_id": "9380032492209779",  "seq": 11},
    {"meter_id": "2176821377232971",  "seq": 12},
    {"meter_id": "9952122687568553",  "seq": 13},
    {"meter_id": "4117124212178786",  "seq": 14},
    {"meter_id": "3939103675925938",  "seq": 15},
    {"meter_id": "1024263709450027",  "seq": 16},
    {"meter_id": "5469436094862080",  "seq": 17},
    {"meter_id": "2337031897354891",  "seq": 18},
    {"meter_id": "3867387737867786",  "seq": 19},
    {"meter_id": "8674898682364938",  "seq": 20},
    {"meter_id": "9655694506952685",  "seq": 21},
    {"meter_id": "3913555850845243",  "seq": 22},
    {"meter_id": "1890622811223405",  "seq": 23},
    {"meter_id": "3927075207337223",  "seq": 24},
    {"meter_id": "1111252342505996",  "seq": 25},
    {"meter_id": "7717122998924158",  "seq": 26},
    {"meter_id": "9457646838336315",  "seq": 27},
    {"meter_id": "7980842343802904",  "seq": 28},
    {"meter_id": "8666893075412344",  "seq": 29},
    {"meter_id": "7039258754775527",  "seq": 30},
    {"meter_id": "3531062613525023",  "seq": 31},
    {"meter_id": "2501558726784896",  "seq": 32},
    {"meter_id": "5036604087717094",  "seq": 33},
    {"meter_id": "2300593267989896",  "seq": 34},
    {"meter_id": "5780707763791405",  "seq": 35},
    {"meter_id": "3431617881817646",  "seq": 36},
    {"meter_id": "2423711452837086",  "seq": 37},
    {"meter_id": "9748187442357250",  "seq": 38},
    {"meter_id": "8148543724703010",  "seq": 39},
    {"meter_id": "7405124632520081",  "seq": 40},
    {"meter_id": "6893082939534523",  "seq": 41},
    {"meter_id": "6045184289954886",  "seq": 42},
    {"meter_id": "9401648430990304",  "seq": 43},
    {"meter_id": "8143492244889353",  "seq": 44},
    {"meter_id": "7102829248177416",  "seq": 45},
    {"meter_id": "7965153980217242",  "seq": 46},
    {"meter_id": "1687741121433777",  "seq": 47},
    {"meter_id": "5226985369418763",  "seq": 48},
    {"meter_id": "3125894992189399",  "seq": 49},
    {"meter_id": "4279410597846991",  "seq": 50},
    {"meter_id": "9391207209781575",  "seq": 51},
    {"meter_id": "9396204363944407",  "seq": 52},
    {"meter_id": "7821132071543147",  "seq": 53},
    {"meter_id": "9734707562554348",  "seq": 54},
    {"meter_id": "4843745219936863",  "seq": 55},
    {"meter_id": "6537483560262363",  "seq": 56},
    {"meter_id": "6011765871708607",  "seq": 57},
    {"meter_id": "5543382539338594",  "seq": 58},
    {"meter_id": "9557461506013079",  "seq": 59},
    {"meter_id": "9187915858131729",  "seq": 60},
    {"meter_id": "2088754547872093",  "seq": 61},
    {"meter_id": "4725351036102535",  "seq": 62},
    {"meter_id": "1985612869384477",  "seq": 63},
    {"meter_id": "2756278874557025",  "seq": 64},
    {"meter_id": "7489584138679685",  "seq": 65},
    {"meter_id": "6842225870042602",  "seq": 66},
    {"meter_id": "4533536028824099",  "seq": 67},
    {"meter_id": "4623426492574258",  "seq": 68},
    {"meter_id": "2509367740087728",  "seq": 69},
    {"meter_id": "5253497487227379",  "seq": 70},
    {"meter_id": "7743411505584981",  "seq": 71},
    {"meter_id": "9464137180453107",  "seq": 72},
    {"meter_id": "8238324235959166",  "seq": 73},
    {"meter_id": "3208388730562136",  "seq": 74},
    {"meter_id": "2708767172336698",  "seq": 75},
    {"meter_id": "5327822890034608",  "seq": 76},
    {"meter_id": "7558987364216789",  "seq": 77},
    {"meter_id": "5229276808063447",  "seq": 78},
    {"meter_id": "3726814967448133",  "seq": 79},
    {"meter_id": "8688737686548196",  "seq": 80},
    {"meter_id": "7098942055920474",  "seq": 81},
    {"meter_id": "6366144643734369",  "seq": 82},
    {"meter_id": "9516217492416985",  "seq": 83},
    {"meter_id": "6388487260338855",  "seq": 84},
    {"meter_id": "3483295999976303",  "seq": 85},
    {"meter_id": "6870366993119311",  "seq": 86},
    {"meter_id": "1211466507138028",  "seq": 87},
    {"meter_id": "3412701900556191",  "seq": 88},
    {"meter_id": "9345358187754315",  "seq": 89},
    {"meter_id": "8626906188664786",  "seq": 90},
    {"meter_id": "2883485642244101",  "seq": 91},
    {"meter_id": "1131757324192298",  "seq": 92},
    {"meter_id": "5676834122168305",  "seq": 93},
    {"meter_id": "8724968596059869",  "seq": 94},
    {"meter_id": "9231986115139583",  "seq": 95},
    {"meter_id": "6214747523813240",  "seq": 96},
    {"meter_id": "8567215271841741",  "seq": 97},
    {"meter_id": "1471078201976155",  "seq": 98},
    {"meter_id": "1808842397905281",  "seq": 99},
    {"meter_id": "3195223305538314",  "seq": 100},
    {"meter_id": "5536063397683435",  "seq": 101},
    {"meter_id": "4902023923070788",  "seq": 102},
    {"meter_id": "5874448420160896",  "seq": 103},
    {"meter_id": "5929028047880138",  "seq": 104},
    {"meter_id": "2372842538151849",  "seq": 105},
    {"meter_id": "2699329122240891",  "seq": 106},
    {"meter_id": "8716300720830951",  "seq": 107},
    {"meter_id": "4911169935560960",  "seq": 108},
    {"meter_id": "8751573106298767",  "seq": 109},
    {"meter_id": "9714561270560367",  "seq": 110},
    {"meter_id": "7189604789304594",  "seq": 111},
    {"meter_id": "8204138983799768",  "seq": 112},
    {"meter_id": "4129132158975128",  "seq": 113},
    {"meter_id": "4735019990804554",  "seq": 114},
    {"meter_id": "3487435776434988",  "seq": 115},
    {"meter_id": "1922513044739322",  "seq": 116},
    {"meter_id": "7995168801891843",  "seq": 117},
    {"meter_id": "9280277672245709",  "seq": 118},
    {"meter_id": "8555861280011533",  "seq": 119},
    {"meter_id": "8151207668013492",  "seq": 120},
    {"meter_id": "3603199028896356",  "seq": 121},
    {"meter_id": "9196828357931930",  "seq": 122},
    {"meter_id": "8940716153397771",  "seq": 123},
    {"meter_id": "8164644939635014",  "seq": 124},
    {"meter_id": "6403398392626744",  "seq": 125},
    {"meter_id": "8295379305540674",  "seq": 126},
    {"meter_id": "7708167065274619",  "seq": 127},
    {"meter_id": "4874335754564344",  "seq": 128},
    {"meter_id": "4096741608114367",  "seq": 129},
    {"meter_id": "8923298314882606",  "seq": 130},
    {"meter_id": "1367152929284214",  "seq": 131},
    {"meter_id": "3962217776193688",  "seq": 132},
    {"meter_id": "6027490523540156",  "seq": 133},
    {"meter_id": "5482893666149388",  "seq": 134},
    {"meter_id": "8981169900725888",  "seq": 135},
    {"meter_id": "3846010890309675",  "seq": 136},
    {"meter_id": "1600378956130396",  "seq": 137},
    {"meter_id": "8501653008515200",  "seq": 138},
    {"meter_id": "8478816003674990",  "seq": 139},
    {"meter_id": "8145210152770054",  "seq": 140},
    {"meter_id": "1944405985308823",  "seq": 141},
    {"meter_id": "9133329572042675",  "seq": 142},
    {"meter_id": "8444633929299972",  "seq": 143},
    {"meter_id": "2708893321259693",  "seq": 144},
    {"meter_id": "3725471689783310",  "seq": 145},
    {"meter_id": "8848159848929937",  "seq": 146},
    {"meter_id": "2236763663796295",  "seq": 147},
    {"meter_id": "5159024470617640",  "seq": 148},
    {"meter_id": "6545223872832530",  "seq": 149},
    {"meter_id": "3169151580806929",  "seq": 150},
    {"meter_id": "2019258978812212",  "seq": 151},
    {"meter_id": "9087289501077273",  "seq": 152},
    {"meter_id": "7542521079649909",  "seq": 153},
    {"meter_id": "1732574912140093",  "seq": 154},
    {"meter_id": "4070659666920014",  "seq": 155},
    {"meter_id": "3846047245917840",  "seq": 156},
    {"meter_id": "3833680298457786",  "seq": 157},
    {"meter_id": "7629538317619236",  "seq": 158},
    {"meter_id": "6998430173846302",  "seq": 159},
    {"meter_id": "8149016242916716",  "seq": 160},
    {"meter_id": "8908602314785342",  "seq": 161},
    {"meter_id": "5664145527081679",  "seq": 162},
    {"meter_id": "8734193384558769",  "seq": 163},
    {"meter_id": "2216007535725868",  "seq": 164},
    {"meter_id": "8067393013781844",  "seq": 165},
    {"meter_id": "8474127727629503",  "seq": 166},
    {"meter_id": "4033232317211354",  "seq": 167},
    {"meter_id": "3095656603480266",  "seq": 168},
    {"meter_id": "7841787994679378",  "seq": 169},
    {"meter_id": "4967745082431238",  "seq": 170},
    {"meter_id": "9015922737746008",  "seq": 171},
    {"meter_id": "8370608838148920",  "seq": 172},
    {"meter_id": "4394088388009899",  "seq": 173},
    {"meter_id": "4854561191072642",  "seq": 174},
    {"meter_id": "9346716271262479",  "seq": 175},
    {"meter_id": "4396171088366936",  "seq": 176},
    {"meter_id": "3394974761284559",  "seq": 177},
    {"meter_id": "5311241548798604",  "seq": 178},
    {"meter_id": "6150344057074342",  "seq": 179},
    {"meter_id": "6070439171651217",  "seq": 180},
    {"meter_id": "1501595226244857",  "seq": 181},
    {"meter_id": "7285483163871635",  "seq": 182},
    {"meter_id": "1951569619987704",  "seq": 183},
    {"meter_id": "6013658672012890",  "seq": 184},
    {"meter_id": "5555340076620687",  "seq": 185},
    {"meter_id": "1540186227553953",  "seq": 186},
    {"meter_id": "9146976991835562",  "seq": 187},
    {"meter_id": "2350941958237301",  "seq": 188},
    {"meter_id": "8479802547558744",  "seq": 189},
    {"meter_id": "8196398746007345",  "seq": 190},
    {"meter_id": "7546525190993883",  "seq": 191},
    {"meter_id": "5805209698960811",  "seq": 192},
    {"meter_id": "9551067699552339",  "seq": 193},
    {"meter_id": "4749884352372841",  "seq": 194},
    {"meter_id": "2159547425510716",  "seq": 195},
    {"meter_id": "2479489468944956",  "seq": 196},
    {"meter_id": "7934079009318244",  "seq": 197},
    {"meter_id": "4665900612961929",  "seq": 198},
    {"meter_id": "8698346095286511",  "seq": 199},
    {"meter_id": "5608107384991856",  "seq": 200},
    {"meter_id": "5317991348982540",  "seq": 201},
    {"meter_id": "7878254129135795",  "seq": 202},
    {"meter_id": "9261228308081532",  "seq": 203},
    {"meter_id": "9126164103762454",  "seq": 204},
    {"meter_id": "6335872824835160",  "seq": 205},
    {"meter_id": "9464781803232100",  "seq": 206},
    {"meter_id": "4936679609880718",  "seq": 207},
    {"meter_id": "9780364079878825",  "seq": 208},
    {"meter_id": "4597139875780471",  "seq": 209},
    {"meter_id": "6929698957937983",  "seq": 210},
    {"meter_id": "1473730745338406",  "seq": 211},
    {"meter_id": "7839171134186730",  "seq": 212},
    {"meter_id": "3597935850362013",  "seq": 213},
    {"meter_id": "8362389745503076",  "seq": 214},
    {"meter_id": "1752418477872527",  "seq": 215},
    {"meter_id": "4072542430497575",  "seq": 216},
    {"meter_id": "5039644905033528",  "seq": 217},
    {"meter_id": "9301877880861411",  "seq": 218},
    {"meter_id": "1526819722351515",  "seq": 219},
    {"meter_id": "5773474601960460",  "seq": 220},
    {"meter_id": "9433548981678908",  "seq": 221},
    {"meter_id": "5548401774642019",  "seq": 222},
    {"meter_id": "3473894690434301",  "seq": 223},
    {"meter_id": "4920620281057482",  "seq": 224},
    {"meter_id": "8794263548020044",  "seq": 225},
    {"meter_id": "1997443275389506",  "seq": 226},
    {"meter_id": "6707457431889330",  "seq": 227},
    {"meter_id": "1064087248895414",  "seq": 228},
    {"meter_id": "8038250406081002",  "seq": 229},
    {"meter_id": "1811314678177980",  "seq": 230},
    {"meter_id": "3538577244615879",  "seq": 231},
    {"meter_id": "4528028699450907",  "seq": 232},
    {"meter_id": "9910602312902006",  "seq": 233},
    {"meter_id": "4722256308895657",  "seq": 234},
    {"meter_id": "1282706828654845",  "seq": 235},
    {"meter_id": "1845482160193987",  "seq": 236},
    {"meter_id": "1806423359925049",  "seq": 237},
    {"meter_id": "1013792197259913",  "seq": 238},
    {"meter_id": "5216271006731232",  "seq": 239},
    {"meter_id": "4053544880874472",  "seq": 240},
    {"meter_id": "8322082476785364",  "seq": 241},
    {"meter_id": "8666942804688512",  "seq": 242},
    {"meter_id": "6409311097134841",  "seq": 243},
    {"meter_id": "9294863899613393",  "seq": 244},
    {"meter_id": "9970548515222649",  "seq": 245},
    {"meter_id": "7039645186109615",  "seq": 246},
    {"meter_id": "7196629642297798",  "seq": 247},
    {"meter_id": "8807963923168674",  "seq": 248},
    {"meter_id": "4939730555809027",  "seq": 249},
    {"meter_id": "8217461575641421",  "seq": 250},
]

METER_MAP: dict[str, dict] = {m["meter_id"]: m for m in METERS}
SEQ_MAP:   dict[int, dict]  = {m["seq"]: m for m in METERS}

# ---------------------------------------------------------------------------
# Offline meters: ~60% do not transmit (deterministic per meter_id)
# ---------------------------------------------------------------------------
def is_offline(meter_id: str) -> bool:
    return int(hashlib.md5(meter_id.encode()).hexdigest(), 16) % 10 < 6

# ---------------------------------------------------------------------------
# Realistic kWh generation
# ---------------------------------------------------------------------------
# Amfilochia: coastal western Greece, Mediterranean climate
HOURLY_PROFILE = [
    0.10, 0.08, 0.07, 0.07, 0.08, 0.15,
    0.35, 0.60, 0.85, 0.95, 1.00, 0.98,
    0.90, 0.95, 0.98, 0.95, 0.85, 0.70,
    0.55, 0.40, 0.30, 0.25, 0.18, 0.12,
]

WEEKEND_FACTOR = 0.28

def seasonal_factor(month: int) -> float:
    factors = {
        1: 0.88, 2: 0.86, 3: 0.91, 4: 0.95,
        5: 1.02, 6: 1.16, 7: 1.30, 8: 1.28,
        9: 1.08, 10: 0.98, 11: 0.91, 12: 0.89,
    }
    return factors.get(month, 1.0)

# Base load varies slightly per meter using its sequence number
def base_load_kw(seq: int) -> float:
    # Range 3–18 kW, deterministic per meter
    return round(3.0 + (seq % 16), 1)

def kwh_for_interval(meter_id: str, dt: datetime, interval_minutes: int = 15) -> float:
    m = METER_MAP.get(meter_id)
    if not m:
        return 0.0
    base_kw = base_load_kw(m["seq"])
    hour_factor  = HOURLY_PROFILE[dt.hour]
    day_factor   = WEEKEND_FACTOR if dt.weekday() >= 5 else 1.0
    season       = seasonal_factor(dt.month)
    seed         = int(dt.timestamp()) ^ hash(meter_id)
    noise        = 1.0 + random.Random(seed).uniform(-0.04, 0.04)
    kw = base_kw * hour_factor * day_factor * season * noise
    return round(max(kw * (interval_minutes / 60), 0.0), 4)

def snap_to_15min(dt: datetime) -> datetime:
    return dt.replace(minute=(dt.minute // 15) * 15, second=0, microsecond=0)

def snap_to_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)

def snap_to_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def _tz(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

def _resolve_meters(meter_id: Optional[str], seq: Optional[int]) -> Optional[list[str]]:
    if meter_id:
        return [meter_id] if meter_id in METER_MAP else None
    if seq is not None:
        m = SEQ_MAP.get(seq)
        return [m["meter_id"]] if m else None
    return [m["meter_id"] for m in METERS]

def _reading(mid: str, ts: datetime, interval: str, kwh_val) -> dict:
    base = {
        "seq":      METER_MAP[mid]["seq"],
        "meter_id": mid,
        "status":   "offline" if is_offline(mid) else "ok",
        "interval": interval,
    }
    if interval == "1d":
        base["date"] = ts.date().isoformat()
    else:
        base["timestamp"] = ts.isoformat()
    base["kwh"] = kwh_val
    return base

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def health():
    online  = sum(1 for m in METERS if not is_offline(m["meter_id"]))
    offline = len(METERS) - online
    return {
        "status": "ok",
        "service": "FastAPI energy meters API for Municipality of Amfilochia",
        "utc_time": datetime.now(timezone.utc).isoformat(),
        "total_meters": len(METERS),
        "online": online,
        "offline": offline,
    }


@app.get("/meters", tags=["Registry"])
def list_meters():
    """List all 250 meters with their sequential ID and online/offline status."""
    return [
        {
            "seq": m["seq"],
            "meter_id": m["meter_id"],
            "status": "offline" if is_offline(m["meter_id"]) else "ok",
        }
        for m in METERS
    ]


@app.get("/readings/latest", tags=["Readings – 15 min"])
def get_latest():
    """Most recent 15-minute reading for every meter."""
    now = snap_to_15min(datetime.now(timezone.utc))
    results = []
    for m in METERS:
        mid = m["meter_id"]
        kwh = None if is_offline(mid) else kwh_for_interval(mid, now, 15)
        results.append(_reading(mid, now, "15min", kwh))
    return {"utc_time": now.isoformat(), "count": len(results), "readings": results}


@app.get("/readings/15min", tags=["Readings – 15 min"])
def get_readings_15min(
    meter_id: Optional[str] = Query(None, description="Filter by meter ID"),
    seq: Optional[int] = Query(None, description="Filter by sequential number (1-250)"),
    from_ts: Optional[datetime] = Query(None, description="Default: last 24h"),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(200, ge=1, le=2000),
):
    """kWh readings at 15-minute intervals. Default window: last 24 hours."""
    now = datetime.now(timezone.utc)
    end   = snap_to_15min(_tz(to_ts)   if to_ts   else now)
    start = snap_to_15min(_tz(from_ts) if from_ts else now - timedelta(hours=24))
    meters = _resolve_meters(meter_id, seq)
    if meters is None:
        raise HTTPException(status_code=404, detail="Meter not found.")

    results, slot = [], start
    while slot <= end and len(results) < limit:
        for mid in meters:
            kwh = None if is_offline(mid) else kwh_for_interval(mid, slot, 15)
            results.append(_reading(mid, slot, "15min", kwh))
        slot += timedelta(minutes=15)

    return {"from": start.isoformat(), "to": end.isoformat(), "interval": "15min", "count": len(results), "readings": results}


@app.get("/readings/hourly", tags=["Readings – Hourly"])
def get_readings_hourly(
    meter_id: Optional[str] = Query(None),
    seq: Optional[int] = Query(None),
    from_ts: Optional[datetime] = Query(None, description="Default: last 7 days"),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
):
    """kWh readings aggregated per hour. Default window: last 7 days."""
    now = datetime.now(timezone.utc)
    end   = snap_to_hour(_tz(to_ts)   if to_ts   else now)
    start = snap_to_hour(_tz(from_ts) if from_ts else now - timedelta(days=7))
    meters = _resolve_meters(meter_id, seq)
    if meters is None:
        raise HTTPException(status_code=404, detail="Meter not found.")

    results, slot = [], start
    while slot <= end and len(results) < limit:
        for mid in meters:
            kwh = None if is_offline(mid) else round(
                sum(kwh_for_interval(mid, slot + timedelta(minutes=m), 15) for m in [0, 15, 30, 45]), 4
            )
            results.append(_reading(mid, slot, "1h", kwh))
        slot += timedelta(hours=1)

    return {"from": start.isoformat(), "to": end.isoformat(), "interval": "1h", "count": len(results), "readings": results}


@app.get("/readings/daily", tags=["Readings – Daily"])
def get_readings_daily(
    meter_id: Optional[str] = Query(None),
    seq: Optional[int] = Query(None),
    from_ts: Optional[datetime] = Query(None, description="Default: last 30 days"),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(365, ge=1, le=1000),
):
    """kWh readings aggregated per day. Default window: last 30 days."""
    now = datetime.now(timezone.utc)
    end   = snap_to_day(_tz(to_ts)   if to_ts   else now)
    start = snap_to_day(_tz(from_ts) if from_ts else now - timedelta(days=30))
    meters = _resolve_meters(meter_id, seq)
    if meters is None:
        raise HTTPException(status_code=404, detail="Meter not found.")

    results, slot = [], start
    while slot <= end and len(results) < limit:
        for mid in meters:
            kwh = None if is_offline(mid) else round(
                sum(kwh_for_interval(mid, slot + timedelta(minutes=15 * i), 15) for i in range(96)), 4
            )
            results.append(_reading(mid, slot, "1d", kwh))
        slot += timedelta(days=1)

    return {"from": start.date().isoformat(), "to": end.date().isoformat(), "interval": "1d", "count": len(results), "readings": results}


@app.get("/meters/{identifier}", tags=["Registry"])
def get_meter(identifier: str):
    """Get a single meter by meter_id or sequential number (e.g. 42)."""
    # Try seq number first
    if identifier.isdigit():
        m = SEQ_MAP.get(int(identifier))
    else:
        m = METER_MAP.get(identifier)
    if not m:
        raise HTTPException(status_code=404, detail=f"Meter '{identifier}' not found.")
    return {
        "seq": m["seq"],
        "meter_id": m["meter_id"],
        "status": "offline" if is_offline(m["meter_id"]) else "ok",
    }
