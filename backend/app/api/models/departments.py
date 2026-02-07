from typing import List, Optional
from pydantic import BaseModel


class Department(BaseModel):
    id: str
    name: str
    short_name: str
    description: str
    category_ids: List[str]  # Categories this dept handles
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    
    
class DepartmentResponse(BaseModel):
    id: str
    name: str
    short_name: str
    description: str
    categories: List[str]  # Category names
    contact_email: Optional[str] = None
    website: Optional[str] = None


class DepartmentStats(BaseModel):
    id: str
    name: str
    short_name: str
    total_complaints: int
    resolved: int
    pending: int
    in_progress: int
    resolution_rate: float  # Percentage
    avg_resolution_hours: Optional[float] = None
    score: float  # Overall performance score


# === Verified Delhi Department Data ===
DELHI_DEPARTMENTS = [
    Department(
        id="mcd",
        name="Municipal Corporation of Delhi",
        short_name="MCD",
        description="Civic infrastructure, sanitation, and local services for Delhi",
        category_ids=["potholes", "sanitation", "garbage", "drainage", "parks", "encroachment"],
        contact_email="commissioner@mcd.gov.in",
        website="https://mcdonline.nic.in"
    ),
    Department(
        id="pwd",
        name="Public Works Department",
        short_name="PWD",
        description="Construction and maintenance of roads, bridges, and government buildings",
        category_ids=["potholes", "roads", "bridges", "footpaths"],
        contact_email="pwddelhi@nic.in",
        website="https://pwd.delhi.gov.in"
    ),
    Department(
        id="djb",
        name="Delhi Jal Board",
        short_name="DJB",
        description="Water supply and sewage management in Delhi",
        category_ids=["water_supply", "sewage", "drainage", "water_leakage"],
        contact_email="ceo@djb.gov.in",
        website="https://delhijalboard.nic.in"
    ),
    Department(
        id="bses",
        name="BSES Electricity",
        short_name="BSES",
        description="Electricity distribution for South and East Delhi",
        category_ids=["streetlights", "electricity", "power_outage"],
        contact_email="customercare@bsesdelhi.com",
        website="https://www.bsesdelhi.com"
    ),
    Department(
        id="tpddl",
        name="Tata Power Delhi Distribution",
        short_name="TPDDL",
        description="Electricity distribution for North and Northwest Delhi",
        category_ids=["streetlights", "electricity", "power_outage"],
        contact_email="tpaborhi@tatapower.com",
        website="https://www.tatapower-ddl.com"
    ),
    Department(
        id="dpcc",
        name="Delhi Pollution Control Committee",
        short_name="DPCC",
        description="Environmental pollution control and monitoring",
        category_ids=["air_pollution", "noise_pollution", "industrial_pollution"],
        contact_email="membersecretary-dpcc@nic.in",
        website="https://dpcc.delhigovt.nic.in"
    ),
    Department(
        id="dusib",
        name="Delhi Urban Shelter Improvement Board",
        short_name="DUSIB",
        description="Slum improvement and rehabilitation",
        category_ids=["housing", "slum", "encroachment"],
        website="https://delhishelterboard.in"
    ),
    Department(
        id="ndmc",
        name="New Delhi Municipal Council",
        short_name="NDMC",
        description="Civic services for New Delhi district (Central Delhi)",
        category_ids=["potholes", "sanitation", "garbage", "streetlights", "water_supply", "parks"],
        contact_email="secretary@ndmc.gov.in",
        website="https://www.ndmc.gov.in"
    ),
    Department(
        id="delhi_police",
        name="Delhi Police",
        short_name="Delhi Police",
        description="Law enforcement and public safety",
        category_ids=["traffic", "crime", "public_safety", "noise_complaint"],
        contact_email="cp.delhi@nic.in",
        website="https://delhipolice.nic.in"
    ),
    Department(
        id="dtc",
        name="Delhi Transport Corporation",
        short_name="DTC",
        description="Public bus transport services",
        category_ids=["bus_service", "public_transport"],
        website="https://www.dtc.nic.in"
    ),
    Department(
        id="dmrc",
        name="Delhi Metro Rail Corporation",
        short_name="DMRC",
        description="Metro rail services",
        category_ids=["metro_service", "public_transport"],
        website="https://www.delhimetrorail.com"
    ),
    Department(
        id="dda",
        name="Delhi Development Authority",
        short_name="DDA",
        description="Urban planning and development",
        category_ids=["construction", "building_violation", "parks", "sports_facilities"],
        website="https://dda.org.in"
    ),
]


# === Complaint Categories ===
class Category(BaseModel):
    id: str
    name: str
    description: str
    icon: str  # Emoji or icon name
    default_department_id: str


COMPLAINT_CATEGORIES = [
    Category(id="potholes", name="Potholes", description="Road potholes and damaged roads", icon="pothole", default_department_id="mcd"),
    Category(id="roads", name="Road Damage", description="Broken roads, cracks, uneven surface", icon="road", default_department_id="pwd"),
    Category(id="sanitation", name="Sanitation", description="Cleanliness and hygiene issues", icon="broom", default_department_id="mcd"),
    Category(id="garbage", name="Garbage Overflow", description="Overflowing dustbins and garbage dumps", icon="trash", default_department_id="mcd"),
    Category(id="drainage", name="Drainage/Sewage", description="Blocked drains and sewage overflow", icon="drain", default_department_id="djb"),
    Category(id="streetlights", name="Street Lights", description="Non-functional or damaged street lights", icon="lightbulb", default_department_id="bses"),
    Category(id="water_supply", name="Water Supply", description="No water, low pressure, contamination", icon="droplet", default_department_id="djb"),
    Category(id="water_leakage", name="Water Leakage", description="Pipeline leaks and wastage", icon="wrench", default_department_id="djb"),
    Category(id="electricity", name="Electricity Issues", description="Power cuts, voltage issues", icon="zap", default_department_id="bses"),
    Category(id="traffic", name="Traffic Issues", description="Signal malfunction, congestion", icon="traffic-light", default_department_id="delhi_police"),
    Category(id="encroachment", name="Encroachment", description="Illegal occupation of public space", icon="construction", default_department_id="mcd"),
    Category(id="noise_pollution", name="Noise Pollution", description="Excessive noise from construction, events", icon="volume-high", default_department_id="dpcc"),
    Category(id="air_pollution", name="Air Pollution", description="Smoke, industrial emissions, burning", icon="cloud", default_department_id="dpcc"),
    Category(id="parks", name="Parks & Gardens", description="Unmaintained parks, broken equipment", icon="tree", default_department_id="mcd"),
    Category(id="footpaths", name="Footpaths", description="Damaged or blocked footpaths", icon="footprints", default_department_id="pwd"),
    Category(id="public_safety", name="Public Safety", description="Unsafe areas, missing railings", icon="alert-triangle", default_department_id="delhi_police"),
    Category(id="other", name="Other", description="Other civic issues", icon="clipboard", default_department_id="mcd"),
]


def get_department_by_id(dept_id: str) -> Optional[Department]:
    """Get department by ID."""
    for dept in DELHI_DEPARTMENTS:
        if dept.id == dept_id:
            return dept
    return None


def get_category_by_id(cat_id: str) -> Optional[Category]:
    """Get category by ID."""
    for cat in COMPLAINT_CATEGORIES:
        if cat.id == cat_id:
            return cat
    return None
