import json
import os
import tkinter as tk
from dataclasses import dataclass, asdict
from tkinter import messagebox, ttk
from typing import List


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "advanced_plan.json")

PLAN_PRESETS = {
    "Simple": [
        "📝 Commandes simples",
        "🤖 Messages automatiques",
        "👋 Welcome / Auto-role / Infos",
        "✅ Commandes Slash incluses",
        "✅ SAV 24/7 inclus",
    ],
    "Modération": [
        "⛔ Ban / Kick / Mute",
        "🚫 Anti-spam / Anti-lien",
        "⚠️ Warns",
        "📜 Logs",
        "✅ Commandes Slash incluses",
        "✅ SAV 24/7 inclus",
    ],
    "Économie": [
        "🎒 Inventaire",
        "💸 Argent / Métiers",
        "🎁 Récompenses quotidiennes",
        "🛒 Shop",
        "✅ Commandes Slash incluses",
        "✅ SAV 24/7 inclus",
    ],
    "RP / Gaming": [
        "🎲 Inventaire RP",
        "📖 Fiches de personnages",
        "📈 Leveling avancé",
        "✅ Commandes Slash incluses",
        "✅ SAV 24/7 inclus",
    ],
    "Avancé (sur mesure)": [
        "🛠️ 100% personnalisable",
        "✅ Commandes Slash incluses",
        "✅ SAV 24/7 inclus",
    ],
}

PLAN_PRICES = {
    "Simple": 7.0,
    "Modération": 10.0,
    "Économie": 10.0,
    "RP / Gaming": 30.0,
    "Avancé (sur mesure)": 0.0,
}

STATUS_OPTIONS = ["En attente", "En cours", "Terminé", "Payé"]


@dataclass
class CommandItem:
    name: str
    plan: str
    status: str
    price: float
    functions: str


class AdvancedPlanApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gestion des bots Discord")
        self.geometry("520x360")
        self.minsize(500, 330)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.commands: List[CommandItem] = []
        self._load_data()
        self._build_home()

    def _build_home(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=24, pady=24)

        header = ttk.Label(
            container,
            text="Gestionnaire de commandes",
            font=("Segoe UI", 18, "bold"),
        )
        header.pack(pady=(0, 12))

        subtitle = ttk.Label(
            container,
            text="Choisissez une action pour continuer.",
            font=("Segoe UI", 10),
            foreground="#555",
        )
        subtitle.pack(pady=(0, 20))

        button_frame = ttk.Frame(container)
        button_frame.pack(fill="x", expand=True)

        ttk.Button(button_frame, text="Ajouter", command=self._open_add_window).pack(fill="x", pady=6)
        ttk.Button(button_frame, text="À finir", command=self._open_to_finish).pack(fill="x", pady=6)
        ttk.Button(button_frame, text="À livrer", command=self._open_to_deliver).pack(fill="x", pady=6)
        ttk.Button(button_frame, text="Statistiques", command=self._open_stats).pack(fill="x", pady=6)

        list_frame = ttk.LabelFrame(container, text="Commandes")
        list_frame.pack(fill="both", expand=True, pady=(16, 0))

        columns = ("name", "plan", "status", "price")
        self.home_table = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.home_table.heading("name", text="Commande")
        self.home_table.heading("plan", text="Forfait")
        self.home_table.heading("status", text="Statut")
        self.home_table.heading("price", text="Prix (€)")
        self.home_table.column("name", width=180)
        self.home_table.column("plan", width=140)
        self.home_table.column("status", width=90, anchor="center")
        self.home_table.column("price", width=80, anchor="center")
        self.home_table.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.home_table.yview)
        self.home_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        controls_frame = ttk.Frame(container)
        controls_frame.pack(fill="x", pady=(8, 0))

        ttk.Label(controls_frame, text="Statut sélectionné :").pack(side="left", padx=(0, 6))
        self.home_status_var = tk.StringVar(value=STATUS_OPTIONS[0])
        self.home_status_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.home_status_var,
            values=STATUS_OPTIONS,
            state="readonly",
            width=18,
        )
        self.home_status_combo.pack(side="left")
        ttk.Button(controls_frame, text="Mettre à jour", command=self._update_home_status).pack(
            side="left", padx=8
        )

        self.home_table.bind("<<TreeviewSelect>>", self._on_home_select)
        self._refresh_home_table()

        footer = ttk.Label(
            container,
            text="Les données sont sauvegardées automatiquement à la fermeture.",
            font=("Segoe UI", 9),
            foreground="#666",
        )
        footer.pack(side="bottom", pady=(18, 0))

    def _open_add_window(self) -> None:
        AddCommandWindow(self, on_save=self._handle_add_command)

    def _open_to_finish(self) -> None:
        ListWindow(self, title="Commandes à finir", status_filter="En cours")

    def _open_to_deliver(self) -> None:
        ListWindow(self, title="Commandes à livrer", status_filter="Terminé")

    def _open_stats(self) -> None:
        StatsWindow(self)

    def _handle_add_command(self, new_item: CommandItem) -> None:
        self.commands.append(new_item)
        self._save_data(silent=True)
        self._refresh_home_table()

    def _on_home_select(self, _event: tk.Event) -> None:
        selection = self.home_table.selection()
        if not selection:
            return
        item_id = selection[0]
        index = int(self.home_table.item(item_id, "tags")[0])
        command_item = self.commands[index]
        self.home_status_var.set(command_item.status)

    def _update_home_status(self) -> None:
        selection = self.home_table.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez une commande à mettre à jour.")
            return
        item_id = selection[0]
        index = int(self.home_table.item(item_id, "tags")[0])
        self.commands[index].status = self.home_status_var.get()
        self._save_data(silent=True)
        self._refresh_home_table()

    def _refresh_home_table(self) -> None:
        if not hasattr(self, "home_table"):
            return
        for item in self.home_table.get_children():
            self.home_table.delete(item)
        for index, command_item in enumerate(self.commands):
            self.home_table.insert(
                "",
                "end",
                values=(
                    command_item.name,
                    command_item.plan,
                    command_item.status,
                    f"{command_item.price:.2f}",
                ),
                tags=(str(index),),
            )

    def _load_data(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            self.commands = []
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(
                "Chargement impossible",
                "Le fichier de données est invalide. Il sera réinitialisé.",
            )
            self.commands = []
            return
        self.commands = [
            CommandItem(
                name=item.get("name", ""),
                plan=item.get("plan", "Simple"),
                status=item.get("status", STATUS_OPTIONS[0]),
                price=float(item.get("price", 0)),
                functions=item.get("functions", "-"),
            )
            for item in data
            if item.get("name")
        ]
        self._refresh_home_table()

    def _on_close(self) -> None:
        self._save_data(silent=True)
        self.destroy()

    def _save_data(self, silent: bool = False) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as handle:
                json.dump([asdict(item) for item in self.commands], handle, ensure_ascii=False, indent=2)
        except OSError as exc:
            if not silent:
                messagebox.showerror("Erreur", f"Impossible d'enregistrer: {exc}")
            return
        if not silent:
            messagebox.showinfo("Sauvegarde", "Les données ont été enregistrées avec succès.")


class AddCommandWindow(tk.Toplevel):
    def __init__(self, parent: AdvancedPlanApp, on_save) -> None:
        super().__init__(parent)
        self.title("Ajouter une commande")
        self.geometry("760x420")
        self.minsize(720, 400)
        self.parent = parent
        self.on_save = on_save

        self.name_var = tk.StringVar()
        self.plan_var = tk.StringVar(value="Simple")
        self.status_var = tk.StringVar(value=STATUS_OPTIONS[0])
        self.price_var = tk.StringVar()

        self._build_ui()
        self._apply_plan_preset()

    def _build_ui(self) -> None:
        form_frame = ttk.LabelFrame(self, text="Détails de la commande")
        form_frame.pack(fill="x", padx=16, pady=12)

        ttk.Label(form_frame, text="Nom de la commande").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(form_frame, textvariable=self.name_var, width=38).grid(
            row=0, column=1, sticky="w", padx=8, pady=6
        )

        ttk.Label(form_frame, text="Forfait").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        self.plan_combo = ttk.Combobox(
            form_frame,
            textvariable=self.plan_var,
            values=list(PLAN_PRESETS.keys()),
            state="readonly",
            width=20,
        )
        self.plan_combo.grid(row=0, column=3, sticky="w", padx=8, pady=6)
        self.plan_combo.bind("<<ComboboxSelected>>", self._on_plan_change)

        ttk.Label(form_frame, text="Statut").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.status_combo = ttk.Combobox(
            form_frame,
            textvariable=self.status_var,
            values=STATUS_OPTIONS,
            state="readonly",
            width=18,
        )
        self.status_combo.grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(form_frame, text="Prix (€)").grid(row=1, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(form_frame, textvariable=self.price_var, width=18).grid(
            row=1, column=3, sticky="w", padx=8, pady=6
        )

        ttk.Label(form_frame, text="Fonctions / Détails").grid(
            row=2, column=0, sticky="nw", padx=8, pady=6
        )
        self.functions_text = tk.Text(form_frame, height=5, width=70, wrap="word")
        self.functions_text.grid(row=2, column=1, columnspan=3, sticky="we", padx=8, pady=6)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=16, pady=8)

        ttk.Button(button_frame, text="Enregistrer", command=self._save).pack(side="right", padx=4)
        ttk.Button(button_frame, text="Annuler", command=self.destroy).pack(side="right", padx=4)

    def _on_plan_change(self, _event: tk.Event) -> None:
        self._apply_plan_preset()

    def _apply_plan_preset(self) -> None:
        plan = self.plan_var.get()
        is_advanced = plan == "Avancé (sur mesure)"
        self.functions_text.configure(state="normal")
        if is_advanced:
            self.price_var.set("")
            return
        preset_lines = PLAN_PRESETS.get(plan, [])
        price = PLAN_PRICES.get(plan)
        if price is not None:
            self.price_var.set(f"{price:.2f}")
        self.functions_text.delete("1.0", tk.END)
        self.functions_text.insert(tk.END, "\n".join(preset_lines))
        self.functions_text.configure(state="disabled")

    def _save(self) -> None:
        name = self.name_var.get().strip()
        price_text = self.price_var.get().strip().replace(",", ".")
        functions = self.functions_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Erreur", "Le nom de la commande est obligatoire.")
            return
        if not price_text:
            messagebox.showerror("Erreur", "Le prix est obligatoire.")
            return
        try:
            price = float(price_text)
        except ValueError:
            messagebox.showerror("Erreur", "Le prix doit être un nombre valide.")
            return
        if price < 0:
            messagebox.showerror("Erreur", "Le prix doit être positif.")
            return

        new_item = CommandItem(
            name=name,
            plan=self.plan_var.get(),
            status=self.status_var.get(),
            price=price,
            functions=functions or "-",
        )
        self.on_save(new_item)
        self.destroy()


class ListWindow(tk.Toplevel):
    def __init__(self, parent: AdvancedPlanApp, title: str, status_filter: str) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("820x420")
        self.minsize(780, 400)
        self.parent = parent
        self.status_filter = status_filter

        self._build_ui()
        self._refresh_table()
        self._selected_index: int | None = None

    def _build_ui(self) -> None:
        header = ttk.Label(
            self,
            text=f"{self.status_filter} - commandes",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(pady=12)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("name", "plan", "status", "price")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.table.heading("name", text="Commande")
        self.table.heading("plan", text="Forfait")
        self.table.heading("status", text="Statut")
        self.table.heading("price", text="Prix (€)")
        self.table.column("name", width=260)
        self.table.column("plan", width=160)
        self.table.column("status", width=110, anchor="center")
        self.table.column("price", width=90, anchor="center")
        self.table.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.table.bind("<<TreeviewSelect>>", self._on_select)

        details_frame = ttk.LabelFrame(self, text="Détails de la commande")
        details_frame.pack(fill="x", padx=16, pady=(4, 12))

        self.details_text = tk.Text(details_frame, height=4, wrap="word", state="disabled")
        self.details_text.pack(fill="both", expand=True, padx=8, pady=8)

        footer = ttk.Label(
            self,
            text="Les données sont filtrées selon le statut.",
            font=("Segoe UI", 9),
            foreground="#555",
        )
        footer.pack(pady=(0, 10))

    def _on_select(self, _event: tk.Event) -> None:
        selection = self.table.selection()
        if not selection:
            self._show_details("")
            self._selected_index = None
            return
        item_id = selection[0]
        index = int(self.table.item(item_id, "tags")[0])
        self._selected_index = index
        command_item = self._filtered_items[index]
        self._show_details(command_item.functions)

    def _show_details(self, text: str) -> None:
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, text or "-")
        self.details_text.configure(state="disabled")

    def _refresh_table(self) -> None:
        self._filtered_items = []
        for item in self.table.get_children():
            self.table.delete(item)
        for command_item in self.parent.commands:
            if command_item.status != self.status_filter:
                continue
            self._filtered_items.append(command_item)
            self.table.insert(
                "",
                "end",
                values=(
                    command_item.name,
                    command_item.plan,
                    command_item.status,
                    f"{command_item.price:.2f}",
                ),
                tags=(str(len(self._filtered_items) - 1),),
            )
        self._show_details("")


class StatsWindow(tk.Toplevel):
    def __init__(self, parent: AdvancedPlanApp) -> None:
        super().__init__(parent)
        self.title("Statistiques")
        self.geometry("840x520")
        self.minsize(780, 480)
        self.parent = parent

        self._build_ui()
        self._render_stats()

    def _build_ui(self) -> None:
        header = ttk.Label(
            self,
            text="Statistiques des ventes",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(pady=12)

        self.summary_label = ttk.Label(self, text="", font=("Segoe UI", 11))
        self.summary_label.pack(pady=(0, 8))

        self.canvas = tk.Canvas(self, width=760, height=320, bg="white", highlightthickness=1)
        self.canvas.pack(padx=16, pady=12, fill="both", expand=True)

        helper = ttk.Label(
            self,
            text="Le total gagné correspond aux commandes payées.",
            font=("Segoe UI", 9),
            foreground="#555",
        )
        helper.pack(pady=(0, 12))

    def _render_stats(self) -> None:
        totals_by_plan: dict[str, float] = {}
        counts_by_plan: dict[str, int] = {}
        total_paid = 0.0

        for command in self.parent.commands:
            counts_by_plan[command.plan] = counts_by_plan.get(command.plan, 0) + 1
            totals_by_plan[command.plan] = totals_by_plan.get(command.plan, 0.0) + command.price
            if command.status == "Payé":
                total_paid += command.price

        total_commands = len(self.parent.commands)
        self.summary_label.configure(
            text=f"Total gagné: {total_paid:.2f} € | Commandes: {total_commands}"
        )

        self.canvas.delete("all")
        if not totals_by_plan:
            self.canvas.create_text(380, 160, text="Aucune donnée à afficher.", fill="#555")
            return

        plans = list(totals_by_plan.keys())
        values = [totals_by_plan[plan] for plan in plans]
        max_value = max(values) if values else 1

        width = int(self.canvas.winfo_width()) or 760
        height = int(self.canvas.winfo_height()) or 320
        padding = 50
        bar_width = max(40, (width - 2 * padding) // max(len(plans), 1) - 20)
        x = padding

        for plan, value in zip(plans, values):
            bar_height = 0 if max_value == 0 else int((value / max_value) * (height - 2 * padding))
            y_top = height - padding - bar_height
            y_bottom = height - padding

            self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom, fill="#4f81bd", outline="")
            self.canvas.create_text(x + bar_width / 2, y_top - 10, text=f"{value:.0f}€")
            self.canvas.create_text(x + bar_width / 2, y_bottom + 12, text=plan, anchor="n")
            count = counts_by_plan.get(plan, 0)
            self.canvas.create_text(x + bar_width / 2, y_bottom + 28, text=f"{count} bots", anchor="n")
            x += bar_width + 30


if __name__ == "__main__":
    app = AdvancedPlanApp()
    app.mainloop()
