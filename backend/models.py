from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    apellidos = Column(String, nullable=True)
    dni = Column(String, nullable=True) # Step 1
    telefono = Column(String, nullable=True, index=True) # Step 1 (Celular)
    email = Column(String, unique=True, index=True) # Step 1
    hashed_password = Column(String)
    ciudad = Column(String, nullable=True) # Step 1
    distrito_principal = Column(String, nullable=True) # Step 1
    provincia = Column(String, nullable=True)
    
    rol = Column(String, default="cliente") # cliente, trabajador, empresa
    activo = Column(Boolean, default=True)

    perfil_prestador = relationship("PerfilPrestador", back_populates="usuario", uselist=False)

class PerfilCliente(Base):
    __tablename__ = "perfiles_cliente"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    ciudad = Column(String, nullable=True)
    provincia = Column(String, nullable=True)
    distrito = Column(String, nullable=True)
    zona = Column(String, nullable=True)
    servicios_frecuentes = Column(String, nullable=True)  # comma-separated category ids
    foto_perfil = Column(String, nullable=True)

    usuario = relationship("Usuario")

class PerfilPrestador(Base):
    __tablename__ = "perfiles_prestador"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Step 2: Informacion del Servicio
    oficio_principal = Column(String, nullable=True)
    servicios = Column(String, nullable=True) # Almacenado como JSON o string separado por comas
    experiencia_anios = Column(String, nullable=True) # "Menos de 1 año", "1-3 años", etc.
    zonas_atencion = Column(String, nullable=True)
    
    # Step 3: Disponibilidad
    dias_trabajo = Column(String, nullable=True) # Ej: "LUN,MAR,MIE"
    horario_atencion = Column(String, nullable=True) # "Mañana", "Tarde", "Noche", "Todo el dia"
    atiende_emergencias = Column(Boolean, default=False)
    
    # Step 4: Perfil Profesional
    descripcion = Column(Text, nullable=True)
    foto_perfil = Column(String, nullable=True) # URL
    fotos_trabajos = Column(Text, nullable=True) # URLs separadas por comas
    
    # Step 5: Precios
    tipo_cobro = Column(String, nullable=True) # "Por hora", "Por visita", etc.
    precio_referencial = Column(String, nullable=True)
    
    # Step 6: Verificacion
    foto_dni_frente = Column(String, nullable=True)
    foto_dni_reverso = Column(String, nullable=True)
    selfie = Column(String, nullable=True)
    
    # Otros campos existentes
    tiene_ruc = Column(Boolean, default=False)
    ruc = Column(String, nullable=True)
    razon_social = Column(String, nullable=True)
    nivel_confianza = Column(Integer, default=1)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    
    usuario = relationship("Usuario", back_populates="perfil_prestador")

class Servicio(Base):
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, index=True)
    nombre = Column(String, index=True)


class Conversacion(Base):
    __tablename__ = "conversaciones"

    id = Column(Integer, primary_key=True, index=True)
    # For MVP: store username strings. Later migrate to FK usuario_id
    cliente_username = Column(String, index=True)
    prestador_id = Column(String, index=True)  # matches Provider.id from frontend data
    prestador_nombre = Column(String)
    prestador_categoria = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    mensajes = relationship("Mensaje", back_populates="conversacion", order_by="Mensaje.created_at")


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    conversacion_id = Column(Integer, ForeignKey("conversaciones.id"))
    # "cliente" or "prestador"
    remitente = Column(String)
    texto = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversacion = relationship("Conversacion", back_populates="mensajes")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    provider_id = Column(Integer, ForeignKey("usuarios.id"))
    
    servicio = Column(String, nullable=True) # Titulo del trabajo (ej: Gasfiteria urgente)
    fecha = Column(String, nullable=True) # Ej: "Mañana", "2024-10-10"
    hora = Column(String, nullable=True) # Ej: "10:00 AM - 12:00 PM"
    estado = Column(String, default="nueva") # nueva, pendiente, programada, completada, rechazada
    precio_estimado = Column(Float, nullable=True)
    direccion = Column(String, nullable=True)
    descripcion = Column(Text, nullable=True)
    fotos = Column(Text, nullable=True) # URLs separadas por comas
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    provider = relationship("Usuario", foreign_keys=[provider_id])

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    provider_id = Column(Integer, ForeignKey("usuarios.id"))
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    rating = Column(Float, nullable=False)
    texto = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking")
    provider = relationship("Usuario", foreign_keys=[provider_id])
    cliente = relationship("Usuario", foreign_keys=[cliente_id])

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo = Column(String) # trabajo_nuevo, pago_recibido, mensaje, calificacion
    titulo = Column(String)
    contenido = Column(Text)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Usuario", foreign_keys=[user_id])

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    provider_id = Column(Integer, ForeignKey("usuarios.id"))
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    
    monto = Column(Float)
    comision = Column(Float)
    estado = Column(String, default="pendiente") # pendiente, procesando, completado, fallido
    pasarela = Column(String) # "efectivo", "transferencia" por ahora, luego "stripe"
    receipt_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking")

class PaymentCard(Base):
    __tablename__ = "payment_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    brand = Column(String) # Visa, Mastercard, Amex, etc.
    last4 = Column(String)
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    cardholder = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Usuario", foreign_keys=[user_id])
