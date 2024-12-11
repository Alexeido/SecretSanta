from email.utils import formataddr
import tkinter as tk
from tkinter import messagebox, Toplevel, Checkbutton, IntVar, StringVar
from tkinter import ttk
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime  # CAMBIO: para fecha actual

class SecretSantaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecretSanta 🎅")
        
        # Lista de participantes y diccionario de blacklists
        self.participants = []  # [(name, email, note)]
        self.blacklists = {}
        
        # Variables para edición de participantes
        self.selected_participant = None
        self.edit_name_var = StringVar()
        self.edit_email_var = StringVar()
        self.edit_note_var = StringVar()
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 10), padding=10)
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TEntry', font=('Segoe UI', 10))
        
        # Interfaz gráfica
        self.create_widgets()
    
    def create_widgets(self):
        # Frame de entrada
        frame_entry = ttk.Frame(self.root)
        frame_entry.pack(pady=10)
        
        ttk.Label(frame_entry, text="Nombre:").grid(row=0, column=0, sticky='w', padx=5)
        self.name_entry = ttk.Entry(frame_entry)
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame_entry, text="Correo:").grid(row=1, column=0, sticky='w', padx=5)
        self.email_entry = ttk.Entry(frame_entry)
        self.email_entry.grid(row=1, column=1, pady=5)

        # CAMBIO: Campo para la nota
        ttk.Label(frame_entry, text="Nota:").grid(row=2, column=0, sticky='w', padx=5)
        self.note_entry = ttk.Entry(frame_entry)
        self.note_entry.grid(row=2, column=1, pady=5)
        
        add_button = ttk.Button(frame_entry, text="Agregar ➕", command=self.add_participant)
        add_button.grid(row=3, columnspan=2, pady=5)
        
        # Lista de participantes
        self.participant_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, font=('Segoe UI', 10))
        self.participant_listbox.pack(padx=10, pady=5)
        self.participant_listbox.bind("<Button-3>", self.show_blacklist_section)
        self.participant_listbox.bind("<Button-1>", self.show_edit_section)
        
        # Sección dinámica
        self.dynamic_section = ttk.Frame(self.root)
        self.dynamic_section.pack(padx=10, pady=10)
        
        # Botones de opciones
        frame_options = ttk.Frame(self.root)
        frame_options.pack(pady=10)
        
        ttk.Button(frame_options, text="Guardar Lista 💾", command=self.save_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_options, text="Cargar Lista 📂", command=self.load_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_options, text="Sortear Público 🎉", command=self.sortear_publico).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_options, text="Sortear Privado 📧", command=self.sortear_privado).pack(side=tk.LEFT, padx=5)
    
    def add_participant(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        note = self.note_entry.get().strip()
        
        if not name or not email:
            messagebox.showwarning("Advertencia ⚠️", "Por favor, ingrese nombre y correo.")
            return
        
        self.participants.append((name, email, note))
        self.blacklists[name] = []
        
        self.participant_listbox.insert(tk.END, name)
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
    
    def show_blacklist_section(self, event):
        selected_index = self.participant_listbox.curselection()
        if not selected_index:
            return
        
        selected_name = self.participant_listbox.get(selected_index)
        
        for widget in self.dynamic_section.winfo_children():
            widget.destroy()
        
        ttk.Label(self.dynamic_section, text=f"Blacklist para {selected_name}").pack(anchor="w")
        check_vars = {}
        
        for name, _, _nt in self.participants:
            if name != selected_name:
                var = IntVar(value=1 if name in self.blacklists[selected_name] else 0)
                check_vars[name] = var
                Checkbutton(self.dynamic_section, text=name, variable=var, font=('Segoe UI', 10)).pack(anchor='w')
        
        def save_blacklist():
            self.blacklists[selected_name] = [name for name, var in check_vars.items() if var.get() == 1]
            messagebox.showinfo("Blacklist", f"Blacklist actualizada para {selected_name}.")
        
        ttk.Button(self.dynamic_section, text="Guardar Blacklist 💾", command=save_blacklist).pack(pady=5)
    
    def show_edit_section(self, event):
        selected_index = self.participant_listbox.curselection()
        if not selected_index:
            return
        
        self.selected_participant = self.participant_listbox.get(selected_index)
        
        name, email, note = next((n, e, nt) for n, e, nt in self.participants if n == self.selected_participant)
        self.edit_name_var.set(name)
        self.edit_email_var.set(email)
        self.edit_note_var.set(note)
        
        for widget in self.dynamic_section.winfo_children():
            widget.destroy()
        
        ttk.Label(self.dynamic_section, text="Editar Participante ✏️").pack(anchor="w")
        
        ttk.Label(self.dynamic_section, text="Nombre:").pack(anchor="w")
        ttk.Entry(self.dynamic_section, textvariable=self.edit_name_var).pack(anchor="w")
        
        ttk.Label(self.dynamic_section, text="Correo:").pack(anchor="w")
        ttk.Entry(self.dynamic_section, textvariable=self.edit_email_var).pack(anchor="w")

        ttk.Label(self.dynamic_section, text="Nota:").pack(anchor="w")
        ttk.Entry(self.dynamic_section, textvariable=self.edit_note_var).pack(anchor="w")
        
        ttk.Button(self.dynamic_section, text="Guardar Cambios 💾", command=self.save_edits).pack(pady=5)
        ttk.Button(self.dynamic_section, text="Eliminar Participante ❌", command=self.delete_participant).pack(pady=5)
    
    def save_edits(self):
        new_name = self.edit_name_var.get().strip()
        new_email = self.edit_email_var.get().strip()
        new_note = self.edit_note_var.get().strip()
        
        if not new_name or not new_email:
            messagebox.showwarning("Advertencia ⚠️", "Por favor, ingrese nombre y correo.")
            return
        
        for i, (name, email, note) in enumerate(self.participants):
            if name == self.selected_participant:
                self.participants[i] = (new_name, new_email, new_note)
                self.blacklists[new_name] = self.blacklists.pop(name)
                break
        
        self.refresh_participant_listbox()
        messagebox.showinfo("Edición", "Datos actualizados correctamente.")
    
    def delete_participant(self):
        self.participants = [(n, e, nt) for n, e, nt in self.participants if n != self.selected_participant]
        self.blacklists.pop(self.selected_participant, None)
        
        self.refresh_participant_listbox()
        messagebox.showinfo("Eliminar", "Participante eliminado.")
    
    def refresh_participant_listbox(self):
        self.participant_listbox.delete(0, tk.END)
        for name, _, _nt in self.participants:
            self.participant_listbox.insert(tk.END, name)
    
    def save_list(self):
        data = {
            "participants": self.participants,
            "blacklists": self.blacklists
        }
        with open("secretsanta_data.json", "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Guardar Lista", "Lista guardada en 'secretsanta_data.json'.")
    
    def load_list(self):
        try:
            with open("secretsanta_data.json", "r") as f:
                data = json.load(f)
            self.participants = data["participants"]
            self.blacklists = data["blacklists"]
            
            self.participant_listbox.delete(0, tk.END)
            for name, _, _ in self.participants:
                self.participant_listbox.insert(tk.END, name)
            
            messagebox.showinfo("Cargar Lista", "Lista cargada correctamente.")
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Error", "No se pudo cargar la lista. Verifique que el archivo exista y esté en formato correcto.")
    
    def sortear_publico(self):
        resultado = self.generar_sorteo()
        if resultado:
            result_window = Toplevel(self.root)
            result_window.title("Resultados del Sorteo 🎉")
            for giver, receiver in resultado.items():
                ttk.Label(result_window, text=f"{giver} regala a {receiver}").pack()

    def sortear_privado(self):
        resultado = self.generar_sorteo()
        if resultado:
            # CAMBIO: Crear carpeta con la fecha actual
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            if not os.path.exists(fecha_actual):
                os.makedirs(fecha_actual)
            
            # Por cada participante, enviamos el correo y generamos su archivo txt individual
            for giver, receiver in resultado.items():
                success = self.enviar_correo(giver, receiver)
                
                # CAMBIO: Crear un .txt con el mensaje que se le envió (o se intentó enviar)
                giver_file_path = os.path.join(fecha_actual, f"{giver}.txt")
                
                # Obtenemos el contenido del mensaje que se envió
                contenido = self.contenido_mensaje(giver, receiver)
                with open(giver_file_path, "w", encoding="utf-8") as gf:
                    gf.write(contenido + "\n")
                    if success:
                        gf.write("Estado del envío: ENVIADO CON ÉXITO")
                    else:
                        gf.write("Estado del envío: FALLO AL ENVIAR")
            
            messagebox.showinfo("Sorteo Privado", f"Correos enviados con los resultados.\nSe han generado archivos individuales por persona en la carpeta {fecha_actual}.")
    
    def generar_sorteo(self):
        if len(self.participants) < 2:
            messagebox.showerror("Error", "Debe haber al menos 2 participantes.")
            return None
        
        names = [n for n, _, _ in self.participants]
        shuffled = names[:]
        
        for _ in range(100):
            random.shuffle(shuffled)
            if all(self.validar_sorteo(n, s) for n, s in zip(names, shuffled)):
                return dict(zip(names, shuffled))
        
        messagebox.showerror("Error", "No se pudo generar un sorteo válido.")
        return None
    
    def validar_sorteo(self, giver, receiver):
        if giver == receiver and giver != "Dani":
            return False
        if receiver in self.blacklists[giver]:
            return False
        return True
    
    def contenido_mensaje(self, giver, receiver):
        # CAMBIO: función auxiliar para obtener el contenido del mensaje
        giver_email = ""
        receiver_note = ""
        
        for n, e, nt in self.participants:
            if n == giver:
                giver_email = e
            if n == receiver:
                receiver_note = nt
        
        if receiver_note:
            contenido = f"Hola {giver}, te ha tocado regalar a {receiver}. Su nota indica: {receiver_note}\n¡Feliz Amigo Invisible!"
        else:
            contenido = f"Hola {giver}, te ha tocado regalar a {receiver}. ¡Feliz Amigo Invisible!"
        
        return contenido
        
    def enviar_correo(self, giver, receiver):
        giver_email = ""
        
        for n, e, nt in self.participants:
            if n == giver:
                giver_email = e
        
        # Configuración del correo
        remitente = 'name@example.com'  # Cambiar a tu dirección de correo
        nombre_remitente = 'Secret Santa 🎅'
        remitente_formateado = formataddr((nombre_remitente, remitente))
        remitente_contraseña = 'Password'  # Cambiar a la contraseña del remitente
        servidor_smtp = 'mail.example.com' # Cambiar al servidor SMTP
        puerto_smtp = 465
        
        contenido = self.contenido_mensaje(giver, receiver)
        
        msg = MIMEMultipart()
        msg['From'] = remitente_formateado
        msg['To'] = giver_email
        msg['Subject'] = 'Resultado de Amigo Invisible 🤫'
        msg.attach(MIMEText(contenido))
        
        try:
            with smtplib.SMTP_SSL(servidor_smtp, puerto_smtp) as server:
                server.login(remitente, remitente_contraseña)
                server.send_message(msg)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el correo a {giver} ({giver_email}). Error: {str(e)}")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = SecretSantaApp(root)
    root.mainloop()
