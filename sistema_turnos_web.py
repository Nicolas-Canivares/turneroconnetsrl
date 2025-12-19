from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from gtts import gTTS
import os

app = Flask(__name__)
CORS(app)

class SistemaDeTurnos:
    def __init__(self):
        self.turno_actual = 1
        self.cola_turnos = []
        self.cajas = {}

    def sacar_turno(self):
        self.cola_turnos.append(self.turno_actual)
        turno = self.turno_actual
        self.turno_actual += 1
        return turno

    def atender_turno(self, caja):
        if caja not in self.cajas:
            self.cajas[caja] = None

        if self.cajas[caja] is not None:
            return {"error": f"La caja {caja} ya está atendiendo el turno {self.cajas[caja]}"}

        if not self.cola_turnos:
            return {"error": "No hay turnos en la cola para atender."}

        turno_atendido = self.cola_turnos.pop(0)
        self.cajas[caja] = turno_atendido

        # Generar síntesis de voz para el turno atendido
        texto = f"Caja {caja}, turno {turno_atendido}"
        audio_dir = os.path.join(os.getcwd(), "audio")  # Ruta a la carpeta audio
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)  # Crea la carpeta si no existe

        #audio_file = os.path.join(audio_dir, f"turno_caja{caja}.mp3")
        audio_file = os.path.join(audio_dir, f"turno_caja{caja}_turno{turno_atendido}.mp3")
        tts = gTTS(texto, lang='es')
        tts.save(audio_file)

        return {"caja": caja, "turno": turno_atendido, "audio": f"/audio/{os.path.basename(audio_file)}"}


    def liberar_caja(self, caja):
        if caja not in self.cajas or self.cajas[caja] is None:
            return {"error": f"La caja {caja} ya está libre o no existe."}

        turno = self.cajas[caja]
        self.cajas[caja] = None
        return {"caja": caja, "turno_liberado": turno}

    def mostrar_estado(self):
        return {
            "cola_turnos": self.cola_turnos,
            "cajas": self.cajas
        }

# Inicialización del sistema de turnos
sistema = SistemaDeTurnos()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sacar_turno", methods=["POST"])
def sacar_turno():
    turno = sistema.sacar_turno()
    return jsonify({"turno_generado": turno})

@app.route("/atender_turno", methods=["POST"])
def atender_turno():
    data = request.json
    caja = data.get("caja")
    if not caja:
        return jsonify({"error": "Debe proporcionar el número de caja."}), 400

    resultado = sistema.atender_turno(caja)
    return jsonify(resultado)

@app.route("/audio/<filename>")
def servir_audio(filename):
    file_path = os.path.join(os.getcwd(), "audio", filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="audio/mp3")
    return jsonify({"error": "Archivo no encontrado"}), 404

@app.route("/liberar_caja", methods=["POST"])
def liberar_caja():
    data = request.json
    caja = data.get("caja")
    if not caja:
        return jsonify({"error": "Debe proporcionar el número de caja."}), 400

    resultado = sistema.liberar_caja(caja)
    return jsonify(resultado)

@app.route("/estado", methods=["GET"])
def estado():
    estado_actual = sistema.mostrar_estado()
    return jsonify(estado_actual)

@app.route("/caja/<int:caja_id>")
def caja(caja_id):
    return render_template("caja.html", caja_id=caja_id)

@app.route("/sacar_turno_pantalla")
def sacar_turno_pantalla():
    return render_template("sacar_turno.html")

@app.route("/pantalla_turnos")
def pantalla_turnos():
    return render_template("pantalla_turnos.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)