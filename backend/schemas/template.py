from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    description: str
    template_type: str  # AR, PR, Invoice, ServiceLog
    content: Dict[str, Any]
    is_default: bool = False

class TemplateCreate(TemplateBase):
    owner_id: str

class Template(TemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime
    owner_id: str

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class TemplateCustomizationBase(BaseModel):
    logo_path: Optional[str] = None
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    font_family: str = "Arial"
    font_size: int = 12
    primary_color: str = "#000000"
    secondary_color: str = "#808080"
    additional_settings: Optional[Dict[str, Any]] = None

class TemplateCustomizationCreate(TemplateCustomizationBase):
    template_id: str

class TemplateCustomization(TemplateCustomizationBase):
    id: str
    template_id: str

    class Config:
        orm_mode = True

class TemplateElement(BaseModel):
    id: str
    element_type: str  # text, image, table, placeholder
    content: Any
    position: Dict[str, int]  # x, y coordinates
    size: Dict[str, int]  # width, height
    style: Optional[Dict[str, Any]] = None  # font, color, etc.

class TemplateTable(BaseModel):
    id: str
    rows: int
    columns: int
    headers: List[str]
    data: List[List[Any]]
    style: Optional[Dict[str, Any]] = None

class TemplatePlaceholder(BaseModel):
    id: str
    field_name: str
    default_value: Optional[str] = None
    format: Optional[str] = None  # date format, number format, etc.
