#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilidades comunes para widgets de la interfaz.
"""

import tkinter as tk


def _coerce_value(value):
    """Intenta convertir el valor a un tipo comparable (numérico cuando aplique)."""
    if value is None:
        return ""

    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()
    if text == "":
        return ""

    sanitized = text.replace("$", "").replace(",", ".")

    for cast in (int, float):
        try:
            return cast(sanitized)
        except ValueError:
            continue

    return text.lower()


def enable_treeview_sorting(treeview: tk.Widget):
    """
    Habilita el ordenamiento asc/desc al hacer clic en los encabezados de columnas.
    """

    def sort_column(col, descending):
        data = [
            (_coerce_value(treeview.set(child, col)), child)
            for child in treeview.get_children("")
        ]
        data.sort(key=lambda item: item[0], reverse=descending)

        for index, (_, child) in enumerate(data):
            treeview.move(child, "", index)

        treeview.heading(col, command=lambda: sort_column(col, not descending))

    for column in treeview["columns"]:
        treeview.heading(column, command=lambda c=column: sort_column(c, False))

