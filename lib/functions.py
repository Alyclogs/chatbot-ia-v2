from datetime import datetime
import re
from bson import ObjectId
from connection import db

cita = {"_id": ObjectId(), "fecha": None, "idCliente": None, "idSede": None,
        "nomCliente": None, "nomSede": None, "idEmpleado": None,
        "nomEmpleado": None, "motivo": None, "estado": "PENDIENTE"}

COMANDOS = {
    "informacion_sede": lambda args: obtener_informacion_sede(*args),
    "horario_sede": lambda args: obtener_horario_sede(*args),
    "citas_usuario": lambda args: obtener_citas_usuario(*args),
    "agendar_cita": lambda args: agendar_cita(*args),
    "verificar_disponibilidad": lambda args: verificar_disponibilidad(*args),
}

def obtener_informacion_sede(sede_id):
    sede = db["sedes"].find_one({'_id': ObjectId(sede_id)}, {"_id": 0})
    return f"[[informacion_sede]]: 🏢 **Información de la sede:** {sede}" if sede else "[[informacion_sede]]: ⚠️ No se encontró información de la sede."

def obtener_horario_sede(sede_id, dia=None):
    sede = db["sedes"].find_one({'_id': ObjectId(sede_id)}, {"horario": 1})

    if not sede or "horario" not in sede:
        return "[[horario_sede]]: ⚠️ No se encontró la sede o el horario de la sede."

    dias = {'lun': "Lunes", 'mar': "Martes", 'mier': "Miércoles", 'jue': "Jueves", 'vier': "Viernes", 'sab': "Sábado", 'dom': "Domingo"}

    if dia:
        horario = sede["horario"].get(dia)
        return f"[[horario_sede]]: 🕒 Horario para el día {dias[dia]}: {horario}" if horario else f"[[horario_sede]]: ⚠️ No hay horarios disponibles para {dias.get(dia, dia)}."

    return "[[horario_sede]]: 🕒 Horario de la sede:\n" + "\n".join([f"🕒 **{dias[d]}:** {h}" for d, h in sede["horario"].items()])

def obtener_citas_usuario(id_usuario):
    citas = db["citas"].find({"clienteId": ObjectId(id_usuario.strip())})
    return "[[citas_usuario]]: Citas del usuario:\n" + "\n".join([f"- 📅 {cita['fecha']} - {cita['estado']}" for cita in citas]) or "[[citas_usuario]]: ℹ️ No hay citas registradas."

def convertir_fecha(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
        return fecha
    except ValueError:
        return None

def verificar_disponibilidad(id_sede, fecha_str):
    fecha = convertir_fecha(fecha_str)
    if not fecha:
        return "[[verificar_disponibilidad]]: ⚠️ Formato de fecha incorrecto. Usa DD/MM/AAAA HH:MM"

    existe_cita = db["citas"].find_one({"idSede": ObjectId(id_sede), "fecha": fecha})
    return "[[verificar_disponibilidad]]: ✅ Horario disponible." if not existe_cita else "⚠️ Este horario ya está ocupado."

def agendar_cita(fechaStr: str, id_usuario: str, id_sede: str, motivo: str):
    fecha = convertir_fecha(fechaStr)
    if not fecha:
        return "[[agendar_cita]]: ⚠️ Formato de fecha incorrecto. Usa DD/MM/AAAA HH:MM"
    
    sede = db["sedes"].find_one({'_id': ObjectId(id_sede)})
    usuario = db["usuarios"].find_one({'_id': ObjectId(id_usuario)})

    if sede and usuario:
        cita["fecha"] = fecha
        cita["idCliente"] = ObjectId(id_usuario)
        cita["nomCliente"] = usuario["nombres"]
        cita["idSede"] = ObjectId(id_sede)
        cita["nomSede"] = sede["nombre"]
        cita["motivo"] = motivo

        db["citas"].insert_one(cita)
        return f"[[agendar_cita]]: ✅ Cita confirmada en {sede['nombre']} el {cita['fecha']} para el usuario {usuario["nombres"]}."
    return "[[agendar_cita]]: ⚠️ Faltan datos para completar la cita. Verifica la sintaxis del comando"

def procesar_comandos(mensaje: str):
    patron = r"\[\[([a-zA-Z_]+)\]\](?:\(([^)]*)\))?"
    comandos_ejecutados = []
    comandos_intactos = {"ubicacion_usuario", "sedes_cercanas", "opciones", "enviar_correo_detalles", "enviar_sms", "programar_notificacion"}
    print(f"Mensaje de la IA: {mensaje}")

    def reemplazo(match):
        comando, parametros = match.groups()
        print(f"🔍 Detectado comando: {comando} con parámetros: {parametros}")

        if comando in comandos_intactos:
            print(f"Comando: {comando} ignorado")
            return match.group(0)
        
        
        parametros = [param.strip() for param in parametros.split(",")] if parametros else []
        resultado = COMANDOS.get(comando, lambda args: "⚠️ Comando desconocido.")(parametros)
        comandos_ejecutados.append(resultado)

    mensaje_visible = re.sub(patron, reemplazo, mensaje)

    if comandos_ejecutados:
        mensaje_sistema = "\n".join(comandos_ejecutados)
        return {"comandos": True, "mensaje": mensaje_visible, "mensaje_sistema": mensaje_sistema}

    return {"comandos": False, "mensaje": mensaje_visible}