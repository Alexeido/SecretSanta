from email.utils import formataddr
import tkinter as tk
from tkinter import messagebox, Toplevel, Checkbutton, IntVar, StringVar
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

class SecretSantaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecretSanta")
        
        # Lista de participantes y diccionario de blacklists
        self.participants = []
        self.blacklists = {}
        
        # Variables para edición de participantes
        self.selected_participant = None
        self.edit_name_var = StringVar()
        self.edit_email_var = StringVar()
        
        # Interfaz gráfica
        self.create_widgets()
    
    def create_widgets(self):
        # Frame de entrada
        frame_entry = tk.Frame(self.root)
        frame_entry.pack(pady=10)
        
        tk.Label(frame_entry, text="Nombre:").grid(row=0, column=0)
        self.name_entry = tk.Entry(frame_entry)
        self.name_entry.grid(row=0, column=1)
        
        tk.Label(frame_entry, text="Correo:").grid(row=1, column=0)
        self.email_entry = tk.Entry(frame_entry)
        self.email_entry.grid(row=1, column=1)
        
        add_button = tk.Button(frame_entry, text="Agregar", command=self.add_participant)
        add_button.grid(row=2, columnspan=2, pady=5)
        
        # Lista de participantes
        self.participant_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.participant_listbox.pack(padx=10, pady=5)
        self.participant_listbox.bind("<Button-3>", self.show_blacklist_section)
        self.participant_listbox.bind("<Button-1>", self.show_edit_section)
        
        # Sección dinámica para blacklist y edición
        self.dynamic_section = tk.Frame(self.root)
        self.dynamic_section.pack(padx=10, pady=10)
        
        # Botones de opciones
        frame_options = tk.Frame(self.root)
        frame_options.pack(pady=10)
        
        tk.Button(frame_options, text="Guardar Lista", command=self.save_list).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_options, text="Cargar Lista", command=self.load_list).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_options, text="Sortear Público", command=self.sortear_publico).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_options, text="Sortear Privado", command=self.sortear_privado).pack(side=tk.LEFT, padx=5)
    
    def add_participant(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name or not email:
            messagebox.showwarning("Advertencia", "Por favor, ingrese ambos campos.")
            return
        
        self.participants.append((name, email))
        self.blacklists[name] = []
        
        self.participant_listbox.insert(tk.END, name)
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
    
    def show_blacklist_section(self, event):
        # Obtiene el nombre seleccionado
        selected_index = self.participant_listbox.curselection()
        if not selected_index:
            return
        
        selected_name = self.participant_listbox.get(selected_index)
        
        # Limpia la sección dinámica y crea los checkboxes de blacklist
        for widget in self.dynamic_section.winfo_children():
            widget.destroy()
        
        tk.Label(self.dynamic_section, text=f"Blacklist para {selected_name}").pack(anchor="w")
        check_vars = {}
        
        # Crear un checkbox para cada participante excepto el propio
        for name, _ in self.participants:
            if name != selected_name:
                var = IntVar(value=1 if name in self.blacklists[selected_name] else 0)
                check_vars[name] = var
                Checkbutton(self.dynamic_section, text=name, variable=var).pack(anchor='w')
        
        # Botón para guardar la blacklist actualizada
        def save_blacklist():
            self.blacklists[selected_name] = [name for name, var in check_vars.items() if var.get() == 1]
            messagebox.showinfo("Blacklist", f"Blacklist actualizada para {selected_name}.")
        
        tk.Button(self.dynamic_section, text="Guardar Blacklist", command=save_blacklist).pack(pady=5)
    
    def show_edit_section(self, event):
        # Obtiene el nombre seleccionado
        selected_index = self.participant_listbox.curselection()
        if not selected_index:
            return
        
        self.selected_participant = self.participant_listbox.get(selected_index)
        
        # Carga los datos del participante seleccionado en la sección de edición
        name, email = next((n, e) for n, e in self.participants if n == self.selected_participant)
        self.edit_name_var.set(name)
        self.edit_email_var.set(email)
        
        # Limpia la sección dinámica y crea los campos de edición
        for widget in self.dynamic_section.winfo_children():
            widget.destroy()
        
        tk.Label(self.dynamic_section, text="Editar Participante").pack(anchor="w")
        
        tk.Label(self.dynamic_section, text="Nombre:").pack(anchor="w")
        tk.Entry(self.dynamic_section, textvariable=self.edit_name_var).pack(anchor="w")
        
        tk.Label(self.dynamic_section, text="Correo:").pack(anchor="w")
        tk.Entry(self.dynamic_section, textvariable=self.edit_email_var).pack(anchor="w")
        
        # Botones para guardar cambios o eliminar participante
        tk.Button(self.dynamic_section, text="Guardar Cambios", command=self.save_edits).pack(pady=5)
        tk.Button(self.dynamic_section, text="Eliminar Participante", command=self.delete_participant).pack(pady=5)
    
    def save_edits(self):
        new_name = self.edit_name_var.get().strip()
        new_email = self.edit_email_var.get().strip()
        
        if not new_name or not new_email:
            messagebox.showwarning("Advertencia", "Por favor, ingrese ambos campos.")
            return
        
        # Actualiza el participante en la lista y en la interfaz
        for i, (name, email) in enumerate(self.participants):
            if name == self.selected_participant:
                self.participants[i] = (new_name, new_email)
                self.blacklists[new_name] = self.blacklists.pop(name)  # Actualiza el nombre en la blacklist
                break
        
        self.refresh_participant_listbox()
        messagebox.showinfo("Edición", "Datos actualizados correctamente.")
    
    def delete_participant(self):
        # Elimina al participante seleccionado
        self.participants = [(n, e) for n, e in self.participants if n != self.selected_participant]
        self.blacklists.pop(self.selected_participant, None)
        
        self.refresh_participant_listbox()
        messagebox.showinfo("Eliminar", "Participante eliminado.")
    
    def refresh_participant_listbox(self):
        self.participant_listbox.delete(0, tk.END)
        for name, _ in self.participants:
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
            for name, _ in self.participants:
                self.participant_listbox.insert(tk.END, name)
            
            messagebox.showinfo("Cargar Lista", "Lista cargada correctamente.")
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Error", "No se pudo cargar la lista. Verifique que el archivo exista y esté en formato correcto.")
    
    def sortear_publico(self):
        resultado = self.generar_sorteo()
        if resultado:
            result_window = Toplevel(self.root)
            result_window.title("Resultados del Sorteo")
            for giver, receiver in resultado.items():
                tk.Label(result_window, text=f"{giver} regala a {receiver}").pack()

    def sortear_privado(self):
        resultado = self.generar_sorteo()
        if resultado:
            for giver, receiver in resultado.items():
                self.enviar_correo(giver, receiver)


            messagebox.showinfo("Sorteo Privado", "Correos enviados con los resultados.")
    
    def generar_sorteo(self):
        if len(self.participants) < 2:
            messagebox.showerror("Error", "Debe haber al menos 2 participantes.")
            return None
        
        names = [n for n, _ in self.participants]
        shuffled = names[:]
        
        for _ in range(100):  # Intenta generar combinaciones
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
        
    def enviar_correo(self, giver, receiver):
        _, giver_email = next((n, e) for n, e in self.participants if n == giver)
        
        # Configuración del correo
        remitente = 'name@example.com'  # Cambia a tu dirección de correo en Mail-in-a-Box
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


if __name__ == "__main__":
    root = tk.Tk()
    app = SecretSantaApp(root)
    root.mainloop()




