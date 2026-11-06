import http.server
import socketserver
import urllib.parse
import sqlite3

PORT = 5000

# Inicialización de la base de datos para pruebas de conexión local
def init_db():
    conn = sqlite3.connect('github_demo.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS respaldos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante TEXT NOT NULL,
            proyecto TEXT NOT NULL,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class GitHubDemoHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path in ['/', '/index.html']:
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                
                # Consultar confirmaciones de respaldo
                conn = sqlite3.connect('github_demo.db')
                conn.row_factory = sqlite3.Row
                registros = conn.execute('SELECT id, estudiante, proyecto, fecha FROM respaldos').fetchall()
                conn.close()
                
                # Interfaz simple con Pico.css por CDN
                html = f"""<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Respaldo en GitHub - CECyTEC 302</title>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
                </head>
                <body class="container">
                    <header>
                        <h2>Prueba de Código en GitHub Web Admin</h2>
                        <p><small>CECyTEC Plantel 5 "Profr. Otilio Montaño" | Docente: Ing. Humberto G. Aguilera E.</small></p>
                        <hr>
                    </header>
                    <main>
                        <section>
                            <h3>Registro Local de Confirmación de Repositorio</h3>
                            <form action="/guardar" method="POST">
                                <div class="grid">
                                    <div>
                                        <label for="estudiante">Nombre del Estudiante:</label>
                                        <input type="text" id="estudiante" name="estudiante" required placeholder="Ej. Juan Pérez">
                                    </div>
                                    <div>
                                        <label for="proyecto">Nombre del Repositorio:</label>
                                        <input type="text" id="proyecto" name="proyecto" required value="boleta-cecytec-302">
                                    </div>
                                </div>
                                <button type="submit">Confirmar Registro en Servidor Local</button>
                            </form>
                        </section>

                        <section>
                            <h3>Historial de Verificaciones de la Clase</h3>
                            <figure>
                                <table role="grid">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Estudiante</th>
                                            <th>Repositorio</th>
                                            <th>Fecha/Hora</th>
                                        </tr>
                                    </thead>
                                    <tbody>"""
                
                for r in registros:
                    html += f"""<tr>
                        <td>{r['id']}</td>
                        <td><strong>{r['estudiante']}</strong></td>
                        <td><code>{r['proyecto']}</code></td>
                        <td>{r['fecha']}</td>
                    </tr>"""
                
                if not registros:
                    html += '<tr><td colspan="4" style="text-align:center;">No hay registros confirmados localmente.</td></tr>'
                    
                html += """        </tbody>
                                </table>
                            </figure>
                        </section>
                    </main>
                </body>
                </html>"""
                
                self.wfile.write(html.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write("404 Página no encontrada".encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error en servidor: {str(e)}".encode("utf-8"))

    def do_POST(self):
        try:
            if self.path == '/guardar':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                params = urllib.parse.parse_qs(post_data)
                
                estudiante = params.get('estudiante', [''])[0].strip()
                proyecto = params.get('proyecto', ['boleta-cecytec-302'])[0].strip()

                if estudiante and proyecto:
                    conn = sqlite3.connect('github_demo.db')
                    conn.execute(
                        'INSERT INTO respaldos (estudiante, proyecto) VALUES (?, ?)',
                        (estudiante, proyecto)
                    )
                    conn.commit()
                    conn.close()

                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error al guardar: {str(e)}".encode("utf-8"))

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), GitHubDemoHTTPHandler) as httpd:
        print(f"Servidor activo en puerto {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
