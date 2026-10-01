from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from typing import Optional
from pydantic import BaseModel
from core.auth_deps import get_current_user

router = APIRouter()


class PerfilProviderUpdate(BaseModel):
    usuario_id: Optional[int] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    ruc: Optional[str] = None
    razon_social: Optional[str] = None
    telefono: Optional[str] = None
    departamento: Optional[str] = None
    provincia: Optional[str] = None
    distrito: Optional[str] = None
    oficio_principal: Optional[str] = None
    servicios: Optional[str] = None
    experiencia_anios: Optional[str] = None
    zonas_atencion: Optional[str] = None
    dias_trabajo: Optional[str] = None
    horario_atencion: Optional[str] = None
    atiende_emergencias: Optional[bool] = False
    descripcion: Optional[str] = None
    foto_perfil: Optional[str] = None
    fotos_trabajos: Optional[str] = None
    tipo_cobro: Optional[str] = None
    precio_referencial: Optional[str] = None


@router.post("/perfil")
def create_or_update_perfil(
    data: PerfilProviderUpdate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea o actualiza el PerfilPrestador del usuario autenticado.
    Usable desde el onboarding wizard al finalizar.
    """
    # Actualizar rol a trabajador si era cliente
    if current_user.rol == "cliente":
        current_user.rol = "trabajador"

    # Actualizar datos de usuario
    if data.nombres is not None: current_user.nombre = data.nombres
    if data.apellidos is not None: current_user.apellidos = data.apellidos
    if data.dni is not None: current_user.dni = data.dni
    if data.telefono is not None: current_user.telefono = data.telefono
    if data.provincia is not None: current_user.provincia = data.provincia
    if data.distrito is not None: current_user.distrito_principal = data.distrito

    # Buscar perfil existente
    perfil = db.query(models.PerfilPrestador).filter(
        models.PerfilPrestador.usuario_id == current_user.id
    ).first()

    if perfil:
        # Update
        if data.oficio_principal is not None: perfil.oficio_principal = data.oficio_principal
        if data.servicios is not None: perfil.servicios = data.servicios
        if data.experiencia_anios is not None: perfil.experiencia_anios = data.experiencia_anios
        if data.zonas_atencion is not None: perfil.zonas_atencion = data.zonas_atencion
        if data.dias_trabajo is not None: perfil.dias_trabajo = data.dias_trabajo
        if data.horario_atencion is not None: perfil.horario_atencion = data.horario_atencion
        if data.atiende_emergencias is not None: perfil.atiende_emergencias = data.atiende_emergencias
        if data.descripcion is not None: perfil.descripcion = data.descripcion
        if data.foto_perfil is not None: perfil.foto_perfil = data.foto_perfil
        if data.fotos_trabajos is not None: perfil.fotos_trabajos = data.fotos_trabajos
        if data.tipo_cobro is not None: perfil.tipo_cobro = data.tipo_cobro
        if data.precio_referencial is not None: perfil.precio_referencial = data.precio_referencial
        if data.ruc is not None: 
            perfil.ruc = data.ruc
            perfil.tiene_ruc = True
        if data.razon_social is not None: perfil.razon_social = data.razon_social
    else:
        # Create
        perfil = models.PerfilPrestador(
            usuario_id=current_user.id,
            oficio_principal=data.oficio_principal,
            servicios=data.servicios,
            experiencia_anios=data.experiencia_anios,
            zonas_atencion=data.zonas_atencion,
            dias_trabajo=data.dias_trabajo,
            horario_atencion=data.horario_atencion,
            atiende_emergencias=data.atiende_emergencias,
            descripcion=data.descripcion,
            foto_perfil=data.foto_perfil,
            fotos_trabajos=data.fotos_trabajos,
            tipo_cobro=data.tipo_cobro,
            precio_referencial=data.precio_referencial,
            ruc=data.ruc,
            tiene_ruc=True if data.ruc else False,
            razon_social=data.razon_social
        )
        db.add(perfil)

    db.commit()
    db.refresh(perfil)
    db.refresh(current_user)

    return {
        "message": "Perfil guardado exitosamente",
        "perfil_id": perfil.id,
        "rol": current_user.rol
    }





@router.get("/")
def list_providers(db: Session = Depends(get_db)):
    """Lista todos los proveedores con su perfil."""
    providers = db.query(models.Usuario).join(
        models.PerfilPrestador,
        models.Usuario.id == models.PerfilPrestador.usuario_id
    ).filter(
        models.Usuario.rol.in_(["trabajador", "independiente", "empresa", "proveedor"])
    ).all()

    from sqlalchemy import func
    results = []
    for u in providers:
        avg = db.query(func.avg(models.Review.rating)).filter(
            models.Review.provider_id == u.id
        ).scalar() or 0.0
        perfil = u.perfil_prestador
        results.append({
            "id": u.id,
            "nombre": u.nombre,
            "oficio_principal": perfil.oficio_principal if perfil else None,
            "zonas_atencion": perfil.zonas_atencion if perfil else None,
            "rating": round(avg, 1),
            "foto_perfil": perfil.foto_perfil if perfil else None,
        })
    return results
