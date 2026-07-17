from pydantic import BaseModel, Field


class MedicationCreate(BaseModel):
    name: str
    active_ingredient: str | None = None
    strength: str | None = None
    form: str = Field(default="tablet")
    instructions: str | None = None
    color_hex: str = Field(default="#4f46e5")
    icon: str = Field(default="medication")


class MedicationUpdate(BaseModel):
    name: str | None = None
    active_ingredient: str | None = None
    strength: str | None = None
    form: str | None = None
    instructions: str | None = None
    color_hex: str | None = None
    icon: str | None = None
    is_active: bool | None = None


class MedicationResponse(BaseModel):
    id: str
    name: str
    active_ingredient: str | None = None
    strength: str | None = None
    form: str
    instructions: str | None = None
    color_hex: str
    icon: str
    is_active: bool
    created_at: str
    has_schedules: bool = False


class MedicationScheduleCreate(BaseModel):
    dosage: str
    times: list[str]
    days_of_week: list[int] | None = None
    start_date: str | None = None
    end_date: str | None = None


class MedicationScheduleResponse(BaseModel):
    id: str
    medication_id: str
    dosage: str
    times: list[str]
    days_of_week: list[int] | None = None
    start_date: str | None = None
    end_date: str | None = None


class MedicationLogCreate(BaseModel):
    schedule_id: str | None = None
    taken_at: str | None = None
    dosage_taken: str | None = None
    skipped: bool = False
    notes: str | None = None


class MedicationLogResponse(BaseModel):
    id: str
    medication_id: str
    schedule_id: str | None = None
    taken_at: str | None = None
    dosage_taken: str | None = None
    skipped: bool
    notes: str | None = None
    created_at: str


class MedicationInventoryUpdate(BaseModel):
    initial_count: int | None = None
    remaining_count: int | None = None
    refill_at_count: int | None = None
    prescription_refills: int | None = None
    next_refill_date: str | None = None


class MedicationInventoryResponse(BaseModel):
    id: str
    medication_id: str
    initial_count: int
    remaining_count: int
    refill_at_count: int
    prescription_refills: int | None = None
    next_refill_date: str | None = None
    needs_refill: bool = False


class MedicationTodayItem(BaseModel):
    medication_id: str
    medication_name: str
    color_hex: str
    icon: str
    schedule_id: str | None = None
    dosage: str | None = None
    time: str | None = None
    taken: bool = False
    skipped: bool = False
    kicked_at: str | None = None
    medication_item_id: str | None = None


class MedicationTodayResponse(BaseModel):
    items: list[MedicationTodayItem]
    as_needed: list[MedicationResponse]


class MedicationCheckResponse(BaseModel):
    taken: bool
    skipped: bool
    adherence_rate: float = 0.0
