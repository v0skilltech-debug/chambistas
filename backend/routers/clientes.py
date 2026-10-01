from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from core.auth_deps import get_current_user

router = APIRouter()

@router.post("/perfil", response_model=schemas.PerfilClienteResponse)
def crear_o_actualizar_perfil(
    perfil_data: schemas.PerfilClienteCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the client profile. Expects Authorization header as Bearer <token>."""
    perfil = db.query(models.PerfilCliente).filter(
        models.PerfilCliente.usuario_id == current_user.id
    ).first()

    if perfil:
        # Update existing
        if perfil_data.ciudad is not None:
            perfil.ciudad = perfil_data.ciudad
        if perfil_data.provincia is not None:
            perfil.provincia = perfil_data.provincia
            current_user.provincia = perfil_data.provincia
        if perfil_data.distrito is not None:
            perfil.distrito = perfil_data.distrito
            current_user.distrito_principal = perfil_data.distrito
        if perfil_data.zona is not None:
            perfil.zona = perfil_data.zona
        if perfil_data.servicios_frecuentes is not None:
            perfil.servicios_frecuentes = perfil_data.servicios_frecuentes
        if perfil_data.foto_perfil is not None:
            perfil.foto_perfil = perfil_data.foto_perfil
    else:
        # Create new
        perfil = models.PerfilCliente(
            usuario_id=current_user.id,
            ciudad=perfil_data.ciudad,
            provincia=perfil_data.provincia,
            distrito=perfil_data.distrito,
            zona=perfil_data.zona,
            servicios_frecuentes=perfil_data.servicios_frecuentes,
            foto_perfil=perfil_data.foto_perfil,
        )
        db.add(perfil)
        
        # Sync with user table
        current_user.provincia = perfil_data.provincia
        current_user.distrito_principal = perfil_data.distrito

    db.commit()
    db.refresh(perfil)
    db.refresh(current_user)
    return perfil

@router.get("/perfil", response_model=schemas.PerfilClienteResponse)
def get_perfil(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current client's profile."""
    perfil = db.query(models.PerfilCliente).filter(
        models.PerfilCliente.usuario_id == current_user.id
    ).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return perfil

@router.get("/reviews", response_model=list[schemas.ReviewResponse])
def get_client_reviews(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the reviews written by the current client."""
    return db.query(models.Review).filter(models.Review.cliente_id == current_user.id).all()
