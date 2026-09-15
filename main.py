from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timezone, timedelta
import random

app = FastAPI(
    title="FastAPI energy meters API for Municipality of Amfilochia",
    description="Energy meter readings (kWh) for 250 meters across 44 buildings and pumping stations in Amfilochia.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Buildings & pumping stations registry — 44 facilities, 250 meters total
# ---------------------------------------------------------------------------
BUILDINGS: dict[str, dict] = {
    "1":  {"name": "Δημαρχείο Αμφιλοχίας",              "type": "κτίριο",       "base_load_kw": 14.0, "meters": ["7879091612348837","5946796184359938","2597720818971586","9387705318016904"]},
    "2":  {"name": "Δημοτικό Σχολείο Αμφιλοχίας",       "type": "κτίριο",       "base_load_kw": 9.0,  "meters": ["2105636349052316","2482030408735489","2211586136166354"]},
    "3":  {"name": "Γυμνάσιο Αμφιλοχίας",               "type": "κτίριο",       "base_load_kw": 10.0, "meters": ["4331786944192647","6498233778453346","4349917592011640"]},
    "4":  {"name": "Λύκειο Αμφιλοχίας",                 "type": "κτίριο",       "base_load_kw": 12.0, "meters": ["9380032492209779","2176821377232971","9952122687568553"]},
    "5":  {"name": "Κλειστό Γυμναστήριο Αμφιλοχίας",   "type": "κτίριο",       "base_load_kw": 22.0, "meters": ["4117124212178786","3939103675925938","1024263709450027","5469436094862080","2337031897354891"]},
    "6":  {"name": "Δημοτικό Στάδιο Αμφιλοχίας",        "type": "κτίριο",       "base_load_kw": 15.0, "meters": ["3867387737867786","8674898682364938","9655694506952685"]},
    "7":  {"name": "ΚΕΠ Αμφιλοχίας",                    "type": "κτίριο",       "base_load_kw": 6.0,  "meters": ["3913555850845243","1890622811223405"]},
    "8":  {"name": "Παιδικός Σταθμός Αμφιλοχίας",       "type": "κτίριο",       "base_load_kw": 5.0,  "meters": ["3927075207337223","1111252342505996","7717122998924158"]},
    "9":  {"name": "Πνευματικό Κέντρο Αμφιλοχίας",      "type": "κτίριο",       "base_load_kw": 8.0,  "meters": ["9457646838336315","7980842343802904"]},
    "10": {"name": "Δημοτική Βιβλιοθήκη Αμφιλοχίας",   "type": "κτίριο",       "base_load_kw": 4.0,  "meters": ["8666893075412344","7039258754775527"]},
    "11": {"name": "Δημοτικό Σχολείο Μενιδίου",         "type": "κτίριο",       "base_load_kw": 8.0,  "meters": ["3531062613525023","2501558726784896","5036604087717094"]},
    "12": {"name": "Γυμνάσιο Μενιδίου",                 "type": "κτίριο",       "base_load_kw": 10.0, "meters": ["2300593267989896","5780707763791405","3431617881817646"]},
    "13": {"name": "Κοινοτικό Κατάστημα Αμφιλοχίας",   "type": "κτίριο",       "base_load_kw": 4.0,  "meters": ["2423711452837086","9748187442357250"]},
    "14": {"name": "Κοινοτικό Κατάστημα Μενιδίου",      "type": "κτίριο",       "base_load_kw": 4.0,  "meters": ["8148543724703010","7405124632520081"]},
    "15": {"name": "Κοινοτικό Κατάστημα Αγίου Βλασίου","type": "κτίριο",       "base_load_kw": 4.0,  "meters": ["6893082939534523","6045184289954886"]},
    "16": {"name": "Κοινοτικό Κατάστημα Λουτρού",       "type": "κτίριο",       "base_load_kw": 4.0,  "meters": ["9401648430990304","8143492244889353"]},
    "17": {"name": "Αντλιοστάσιο Αμφιλοχίας 1",        "type": "αντλιοστάσιο","base_load_kw": 18.0, "meters": ["7102829248177416","7965153980217242","1687741121433777","5226985369418763","3125894992189399"]},
    "18": {"name": "Αντλιοστάσιο Αμφιλοχίας 2",        "type": "αντλιοστάσιο","base_load_kw": 16.0, "meters": ["4279410597846991","9391207209781575","9396204363944407","7821132071543147"]},
    "19": {"name": "Αντλιοστάσιο Αμφιλοχίας 3",        "type": "αντλιοστάσιο","base_load_kw": 16.0, "meters": ["9734707562554348","4843745219936863","6537483560262363","9557461506013079"]},
    "20": {"name": "Αντλιοστάσιο Μενιδίου 1",          "type": "αντλιοστάσιο","base_load_kw": 16.0, "meters": ["6011765871708607","5543382539338594","9187915858131729","2088754547872093"]},
    "21": {"name": "Αντλιοστάσιο Μενιδίου 2",          "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["4725351036102535","1985612869384477","2756278874557025","7489584138679685"]},
    "22": {"name": "Αντλιοστάσιο Αγίου Βλασίου",       "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["6842225870042602","4533536028824099","4623426492574258","2509367740087728"]},
    "23": {"name": "Αντλιοστάσιο Λουτρού",             "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["5253497487227379","7743411505584981","9464137180453107","8238324235959166"]},
    "24": {"name": "Αντλιοστάσιο Κατούνας",            "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["3208388730562136","2708767172336698","5327822890034608","7558987364216789"]},
    "25": {"name": "Αντλιοστάσιο Αμπελακίου",          "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["5229276808063447","3726814967448133","8688737686548196","7098942055920474"]},
    "26": {"name": "Αντλιοστάσιο Παλαίρου",            "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["6366144643734369","9516217492416985","6388487260338855","3483295999976303"]},
    "27": {"name": "Αντλιοστάσιο Βόνιτσας",            "type": "αντλιοστάσιο","base_load_kw": 18.0, "meters": ["6870366993119311","1211466507138028","3412701900556191","9345358187754315","8626906188664786"]},
    "28": {"name": "Αντλιοστάσιο Στράτου",             "type": "αντλιοστάσιο","base_load_kw": 18.0, "meters": ["2883485642244101","1131757324192298","5676834122168305","8724968596059869","9231986115139583"]},
    "29": {"name": "Αντλιοστάσιο Φυτειών",             "type": "αντλιοστάσιο","base_load_kw": 18.0, "meters": ["6214747523813240","8567215271841741","1471078201976155","1808842397905281","3195223305538314"]},
    "30": {"name": "Αντλιοστάσιο Αγράμπελου",          "type": "αντλιοστάσιο","base_load_kw": 18.0, "meters": ["5536063397683435","4902023923070788","5874448420160896","5929028047880138","2372842538151849"]},
    "31": {"name": "Αντλιοστάσιο Ινάχου",              "type": "αντλιοστάσιο","base_load_kw": 18.0, "meters": ["2699329122240891","8716300720830951","4911169935560960","8751573106298767","9714561270560367"]},
    "32": {"name": "Αντλιοστάσιο Νεοχωρίου",           "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["7189604789304594","8204138983799768","4129132158975128","4735019990804554","3487435776434988"]},
    "33": {"name": "Αντλιοστάσιο Αγίου Ιωάννη",        "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["1922513044739322","7995168801891843","9280277672245709","8555861280011533","8151207668013492"]},
    "34": {"name": "Αντλιοστάσιο Κεφαλόβρυσου",        "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["3603199028896356","9196828357931930","8940716153397771","8164644939635014","6403398392626744"]},
    "35": {"name": "Αντλιοστάσιο Σταμνάς",             "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["8295379305540674","7708167065274619","4874335754564344","4096741608114367","8923298314882606"]},
    "36": {"name": "Αντλιοστάσιο Αγράφων",             "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["1367152929284214","3962217776193688","6027490523540156","5482893666149388","8981169900725888"]},
    "37": {"name": "Αντλιοστάσιο Χρυσοβίτσας",         "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["3846010890309675","1600378956130396","8501653008515200","8478816003674990","8145210152770054"]},
    "38": {"name": "Αντλιοστάσιο Πεντάλοφου",          "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["1944405985308823","9133329572042675","8444633929299972","2708893321259693","3725471689783310"]},
    "39": {"name": "Αντλιοστάσιο Σαρδηνίων",           "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["8848159848929937","2236763663796295","5159024470617640","6545223872832530","3169151580806929"]},
    "40": {"name": "Αντλιοστάσιο Κομπωτής",            "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["2019258978812212","9087289501077273","7542521079649909","1732574912140093","4070659666920014"]},
    "41": {"name": "Αντλιοστάσιο Αμφιλοχίας 4",        "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["3846047245917840","3833680298457786","7629538317619236","6998430173846302","8149016242916716"]},
    "42": {"name": "Αντλιοστάσιο Αμφιλοχίας 5",        "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["8908602314785342","5664145527081679","8734193384558769","2216007535725868","8067393013781844"]},
    "43": {"name": "Αντλιοστάσιο Αμφιλοχίας 6",        "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["8474127727629503","4033232317211354","3095656603480266","7841787994679378","4967745082431238"]},
    "44": {"name": "Αντλιοστάσιο Αμφιλοχίας 7",        "type": "αντλιοστάσιο","base_load_kw": 14.0, "meters": ["9015922737746008","8370608838148920","4394088388009899","4854561191072642","9346716271262479","4396171088366936","3394974761284559","5311241548798604","6150344057074342","6070439171651217","1501595226244857","7285483163871635","1951569619987704","6013658672012890","5555340076620687","1540186227553953","9146976991835562","2350941958237301","8479802547558744","8196398746007345","7546525190993883","5805209698960811","9551067699552339","4749884352372841","2159547425510716","2479489468944956","7934079009318244","4665900612961929","8698346095286511","5608107384991856","5317991348982540","7878254129135795","9261228308081532","9126164103762454","6335872824835160","9464781803232100","4936679609880718","9780364079878825","4597139875780471","6929698957937983","1473730745338406","7839171134186730","3597935850362013","8362389745503076","1752418477872527","4072542430497575","5039644905033528","9301877880861411","1526819722351515","5773474601960460","9433548981678908","5548401774642019","3473894690434301","4920620281057482","8794263548020044","1997443275389506","6707457431889330","1064087248895414","8038250406081002","1811314678177980","3538577244615879","4528028699450907","9910602312902006","4722256308895657","1282706828654845","1845482160193987","1806423359925049","1013792197259913","5216271006731232","4053544880874472","8322082476785364","8666942804688512","6409311097134841","9294863899613393","9970548515222649","7039645186109615","7196629642297798","8807963923168674","4939730555809027","8217461575641421"]},
}

# Flat lookup: meter_id → building_id
METER_TO_BUILDING: dict[str, str] = {
    meter: bid
    for bid, info in BUILDINGS.items()
    for meter in info["meters"]
}

# ---------------------------------------------------------------------------
# Realistic kWh generation — Amfilochia: coastal western Greece
# ---------------------------------------------------------------------------
HOURLY_PROFILE = [
    0.10, 0.08, 0.07, 0.07, 0.08, 0.15,
    0.35, 0.60, 0.85, 0.95, 1.00, 0.98,
    0.90, 0.95, 0.98, 0.95, 0.85, 0.70,
    0.55, 0.40, 0.30, 0.25, 0.18, 0.12,
]

# Pumping stations run 24/7 with higher night load
PUMP_HOURLY_PROFILE = [
    0.80, 0.85, 0.90, 0.90, 0.85, 0.80,
    0.75, 0.70, 0.75, 0.80, 0.85, 0.88,
    0.85, 0.85, 0.88, 0.90, 0.92, 0.95,
    1.00, 0.98, 0.95, 0.90, 0.85, 0.82,
]

WEEKEND_FACTOR_BUILDING = 0.28
WEEKEND_FACTOR_PUMP     = 1.0   # pumping stations run 7 days

def seasonal_factor(month: int) -> float:
    factors = {
        1: 0.88, 2: 0.86, 3: 0.91, 4: 0.95,
        5: 1.02, 6: 1.16, 7: 1.30, 8: 1.28,
        9: 1.08, 10: 0.98, 11: 0.91, 12: 0.89,
    }
    return factors.get(month, 1.0)

def kwh_for_interval(meter_id: str, dt: datetime, interval_minutes: int = 15) -> float:
    bid = METER_TO_BUILDING.get(meter_id)
    if not bid:
        return 0.0
    info = BUILDINGS[bid]
    is_pump = info["type"] == "αντλιοστάσιο"
    n = len(info["meters"])
    base_kw = info["base_load_kw"] / n
    profile = PUMP_HOURLY_PROFILE if is_pump else HOURLY_PROFILE
    hour_factor = profile[dt.hour]
    day_factor = WEEKEND_FACTOR_PUMP if is_pump else (WEEKEND_FACTOR_BUILDING if dt.weekday() >= 5 else 1.0)
    season = seasonal_factor(dt.month)
    seed = int(dt.timestamp()) ^ hash(meter_id)
    noise = 1.0 + random.Random(seed).uniform(-0.04, 0.04)
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

def _resolve_meters(meter_id: Optional[str], building_id: Optional[str],
                    facility_type: Optional[str]) -> Optional[list[str]]:
    if meter_id:
        return [meter_id] if meter_id in METER_TO_BUILDING else None
    if building_id:
        return BUILDINGS[building_id]["meters"] if building_id in BUILDINGS else None
    if facility_type in ("κτίριο", "αντλιοστάσιο"):
        return [m for bid, info in BUILDINGS.items()
                if info["type"] == facility_type for m in info["meters"]]
    return list(METER_TO_BUILDING.keys())

def _reading(mid: str, ts: datetime, interval: str, kwh_val, include_building=True) -> dict:
    bid = METER_TO_BUILDING[mid]
    info = BUILDINGS[bid]
    r = {
        "meter_id": mid,
        "building_id": bid,
        "building_name": info["name"],
        "facility_type": info["type"],
        "interval": interval,
        "status": "ok",
    }
    if interval == "1d":
        r["date"] = ts.date().isoformat()
    else:
        r["timestamp"] = ts.isoformat()
    r["kwh"] = kwh_val
    return r

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def health():
    ktirια = sum(1 for v in BUILDINGS.values() if v["type"] == "κτίριο")
    antlia = sum(1 for v in BUILDINGS.values() if v["type"] == "αντλιοστάσιο")
    return {
        "status": "ok",
        "service": "FastAPI energy meters API for Municipality of Amfilochia",
        "utc_time": datetime.now(timezone.utc).isoformat(),
        "total_facilities": len(BUILDINGS),
        "buildings": ktirια,
        "pumping_stations": antlia,
        "total_meters": len(METER_TO_BUILDING),
    }


@app.get("/buildings", tags=["Registry"])
def list_buildings(
    type: Optional[str] = Query(None, description="Filter by type: 'κτίριο' or 'αντλιοστάσιο'"),
):
    """List all facilities (buildings and pumping stations) with their meters."""
    result = []
    for bid, info in BUILDINGS.items():
        if type and info["type"] != type:
            continue
        result.append({
            "building_id": bid,
            "name": info["name"],
            "facility_type": info["type"],
            "meters": info["meters"],
            "meter_count": len(info["meters"]),
        })
    return {"count": len(result), "facilities": result}


@app.get("/buildings/{building_id}", tags=["Registry"])
def get_building(building_id: str):
    """Get a single facility by ID."""
    if building_id not in BUILDINGS:
        raise HTTPException(status_code=404, detail=f"Facility '{building_id}' not found.")
    info = BUILDINGS[building_id]
    return {
        "building_id": building_id,
        "name": info["name"],
        "facility_type": info["type"],
        "meters": info["meters"],
        "meter_count": len(info["meters"]),
    }


@app.get("/readings/latest", tags=["Readings – 15 min"])
def get_latest(
    type: Optional[str] = Query(None, description="Filter by facility type"),
):
    """Most recent 15-minute reading for every meter."""
    now = snap_to_15min(datetime.now(timezone.utc))
    meters = _resolve_meters(None, None, type)
    results = [_reading(mid, now, "15min", kwh_for_interval(mid, now, 15)) for mid in meters]
    return {"utc_time": now.isoformat(), "count": len(results), "readings": results}


@app.get("/readings/15min", tags=["Readings – 15 min"])
def get_readings_15min(
    meter_id: Optional[str] = Query(None),
    building_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None, description="Filter by facility type: 'κτίριο' or 'αντλιοστάσιο'"),
    from_ts: Optional[datetime] = Query(None, description="Default: last 24h"),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(200, ge=1, le=2000),
):
    """kWh readings at 15-minute intervals."""
    now = datetime.now(timezone.utc)
    end   = snap_to_15min(_tz(to_ts)   if to_ts   else now)
    start = snap_to_15min(_tz(from_ts) if from_ts else now - timedelta(hours=24))
    meters = _resolve_meters(meter_id, building_id, type)
    if meters is None:
        raise HTTPException(status_code=404, detail="Facility or meter not found.")
    results, slot = [], start
    while slot <= end and len(results) < limit:
        for mid in meters:
            results.append(_reading(mid, slot, "15min", kwh_for_interval(mid, slot, 15)))
        slot += timedelta(minutes=15)
    return {"from": start.isoformat(), "to": end.isoformat(), "interval": "15min",
            "count": len(results), "readings": results}


@app.get("/readings/hourly", tags=["Readings – Hourly"])
def get_readings_hourly(
    meter_id: Optional[str] = Query(None),
    building_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    from_ts: Optional[datetime] = Query(None, description="Default: last 7 days"),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
):
    """kWh readings aggregated per hour."""
    now = datetime.now(timezone.utc)
    end   = snap_to_hour(_tz(to_ts)   if to_ts   else now)
    start = snap_to_hour(_tz(from_ts) if from_ts else now - timedelta(days=7))
    meters = _resolve_meters(meter_id, building_id, type)
    if meters is None:
        raise HTTPException(status_code=404, detail="Facility or meter not found.")
    results, slot = [], start
    while slot <= end and len(results) < limit:
        for mid in meters:
            kwh = round(sum(kwh_for_interval(mid, slot + timedelta(minutes=m), 15)
                            for m in [0, 15, 30, 45]), 4)
            results.append(_reading(mid, slot, "1h", kwh))
        slot += timedelta(hours=1)
    return {"from": start.isoformat(), "to": end.isoformat(), "interval": "1h",
            "count": len(results), "readings": results}


@app.get("/readings/daily", tags=["Readings – Daily"])
def get_readings_daily(
    meter_id: Optional[str] = Query(None),
    building_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    from_ts: Optional[datetime] = Query(None, description="Default: last 30 days"),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(365, ge=1, le=1000),
):
    """kWh readings aggregated per day."""
    now = datetime.now(timezone.utc)
    end   = snap_to_day(_tz(to_ts)   if to_ts   else now)
    start = snap_to_day(_tz(from_ts) if from_ts else now - timedelta(days=30))
    meters = _resolve_meters(meter_id, building_id, type)
    if meters is None:
        raise HTTPException(status_code=404, detail="Facility or meter not found.")
    results, slot = [], start
    while slot <= end and len(results) < limit:
        for mid in meters:
            kwh = round(sum(kwh_for_interval(mid, slot + timedelta(minutes=15 * i), 15)
                            for i in range(96)), 4)
            results.append(_reading(mid, slot, "1d", kwh))
        slot += timedelta(days=1)
    return {"from": start.date().isoformat(), "to": end.date().isoformat(), "interval": "1d",
            "count": len(results), "readings": results}


@app.get("/buildings/{building_id}/summary", tags=["Buildings"])
def building_summary(building_id: str):
    """Today's and this month's total kWh for a facility."""
    if building_id not in BUILDINGS:
        raise HTTPException(status_code=404, detail=f"Facility '{building_id}' not found.")
    now = datetime.now(timezone.utc)
    today_start = snap_to_day(now)
    month_start = today_start.replace(day=1)
    meters = BUILDINGS[building_id]["meters"]
    def total_kwh(start, end):
        total, slot = 0.0, start
        while slot < end:
            for mid in meters:
                total += kwh_for_interval(mid, slot, 15)
            slot += timedelta(minutes=15)
        return round(total, 4)
    return {
        "building_id": building_id,
        "building_name": BUILDINGS[building_id]["name"],
        "facility_type": BUILDINGS[building_id]["type"],
        "meters": meters,
        "meter_count": len(meters),
        "utc_time": now.isoformat(),
        "today_kwh": total_kwh(today_start, snap_to_15min(now)),
        "month_to_date_kwh": total_kwh(month_start, snap_to_15min(now)),
    }


@app.get("/buildings/{building_id}/readings", tags=["Buildings"])
def get_building_readings(
    building_id: str,
    from_ts: Optional[datetime] = Query(None, description="Default: last 24h"),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
):
    """15-minute readings for all meters of a specific facility."""
    if building_id not in BUILDINGS:
        raise HTTPException(status_code=404, detail=f"Facility '{building_id}' not found.")
    now = datetime.now(timezone.utc)
    end   = snap_to_15min(_tz(to_ts)   if to_ts   else now)
    start = snap_to_15min(_tz(from_ts) if from_ts else now - timedelta(hours=24))
    meters = BUILDINGS[building_id]["meters"]
    results, slot = [], start
    while slot <= end and len(results) < limit:
        for mid in meters:
            results.append({
                "meter_id": mid,
                "timestamp": slot.isoformat(),
                "kwh": kwh_for_interval(mid, slot, 15),
                "interval": "15min",
                "status": "ok",
            })
        slot += timedelta(minutes=15)
    return {
        "building_id": building_id,
        "building_name": BUILDINGS[building_id]["name"],
        "facility_type": BUILDINGS[building_id]["type"],
        "from": start.isoformat(),
        "to": end.isoformat(),
        "count": len(results),
        "readings": results,
    }
