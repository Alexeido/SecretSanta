# Secret Santa App 🎅🎁

Esta es una aplicación de sorteos para el Amigo Invisible, desarrollada en Python utilizando Tkinter para la interfaz gráfica. La aplicación permite agregar participantes, gestionar listas negras (blacklists) y realizar sorteos tanto públicos como privados. En el sorteo privado, los resultados se envían por correo electrónico a cada participante sin que nadie más sepa a quién le toca regalar.

## Características ✨

- ➕ Agregar y eliminar participantes.
- 🚫 Gestionar listas negras para evitar que ciertos participantes se regalen entre sí.
- 💾 Guardar y cargar listas de participantes.
- 🎲 Realizar sorteos públicos y privados.
- 📧 Enviar resultados del sorteo privado por correo electrónico.

## Requisitos 🛠️

- 🐍 Python 3.x
- 🖼️ Tkinter
- 📧 smtplib
- 📧 email
- 📄 json

## Instalación 💻

1. 📥 Clona este repositorio en tu máquina local.
2. ✅ Asegúrate de tener Python 3.x instalado.
3. 📦 Instala las dependencias necesarias (Tkinter, smtplib, email, json).

## Uso 🚀

1. Ejecuta el archivo `secretSanta.py`:
    ```sh
    python secretSanta.py
    ```

2. Utiliza la interfaz gráfica para agregar participantes, gestionar listas negras y realizar sorteos.

## Configuración del Correo SMTP 📧

Para enviar los resultados del sorteo privado por correo electrónico, debes configurar los detalles del servidor SMTP en el método `enviar_correo` de la clase `SecretSantaApp` en el archivo `secretSanta.py`:

```python
def enviar_correo(self, giver, receiver):
    _, giver_email = next((n, e) for n, e in self.participants if n == giver)
    
    # Configuración del correo
    remitente = 'name@example.com'  # Cambia a tu dirección de correo
    nombre_remitente = 'Secret Santa 🎅'
    remitente_formateado = formataddr((nombre_remitente, remitente))
    remitente_contraseña = 'Password'  # Cambia a la contraseña del remitente
    servidor_smtp = 'mail.example.com'  # Cambia al dominio de tu servidor
    puerto_smtp = 465  # Puerto seguro para STARTTLS
    
    msg = MIMEMultipart()
    msg['From'] = remitente_formateado
    msg['To'] = giver_email
    msg['Subject'] = 'Resultado de Amigo Invisible 🤫'
    msg.attach(MIMEText(f"Hola {giver}, te ha tocado regalar a {receiver}. ¡Feliz Amigo Invisible!"))
    
    # Envío del correo
    try:
        with smtplib.SMTP_SSL(servidor_smtp, puerto_smtp) as server:
            server.login(remitente, remitente_contraseña)  # Autenticación
            server.send_message(msg)
            messagebox.showinfo("Correo Enviado", f"Correo enviado a {giver}.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar el correo a {giver}. Error: {str(e)}")
```

## Licencia 📜

Este proyecto está licenciado bajo la Licencia Apache 2.0. Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.

## Contribuciones 🤝

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Contacto 📬

Para cualquier consulta o sugerencia, por favor contacta a [abarrenam03@gmail.com](mailto:abarrenam03@gmail.com).