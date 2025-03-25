from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..database import crud
from ..database.database import get_db
from ..schemas import template as template_schema
from ..schemas import user as user_schema
from ..auth.security import get_current_active_user

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.post("/", response_model=template_schema.Template)
async def create_template(
    template: template_schema.TemplateCreate,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Create a new template"""
    # Add owner_id to template
    template.owner_id = current_user.id
    return crud.create_template(db, template)

@router.get("/", response_model=List[template_schema.Template])
async def get_templates(
    template_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get all templates or templates by type"""
    if template_type:
        templates = crud.get_templates_by_type(db, template_type, skip, limit)
    else:
        # Implement get_templates in crud
        templates = []
    return templates

@router.get("/{template_id}", response_model=template_schema.Template)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get template by ID"""
    template = crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=template_schema.Template)
async def update_template(
    template_id: str,
    template_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Update template"""
    template = crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if user is owner or admin
    if template.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this template")
    
    updated_template = crud.update_template(db, template_id, template_data)
    return updated_template

@router.delete("/{template_id}", response_model=dict)
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Delete template"""
    template = crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if user is owner or admin
    if template.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this template")
    
    # Implement delete_template in crud
    # crud.delete_template(db, template_id)
    
    return {"detail": "Template deleted successfully"}

@router.post("/customization", response_model=template_schema.TemplateCustomization)
async def create_template_customization(
    customization: template_schema.TemplateCustomizationCreate,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Create or update template customization"""
    # Check if template exists
    template = crud.get_template(db, customization.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if customization already exists
    existing_customization = crud.get_template_customization(db, customization.template_id)
    if existing_customization:
        # Update existing customization
        updated_customization = crud.update_template_customization(
            db, 
            customization.template_id, 
            customization.dict(exclude={"template_id"})
        )
        return updated_customization
    
    # Create new customization
    return crud.create_template_customization(db, customization)

@router.get("/customization/{template_id}", response_model=template_schema.TemplateCustomization)
async def get_template_customization(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get template customization by template ID"""
    customization = crud.get_template_customization(db, template_id)
    if customization is None:
        raise HTTPException(status_code=404, detail="Template customization not found")
    return customization

@router.put("/customization/{template_id}", response_model=template_schema.TemplateCustomization)
async def update_template_customization(
    template_id: str,
    customization_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Update template customization"""
    # Check if template exists
    template = crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if user is owner or admin
    if template.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this template customization")
    
    # Update customization
    customization = crud.update_template_customization(db, template_id, customization_data)
    if customization is None:
        raise HTTPException(status_code=404, detail="Template customization not found")
    
    return customization
