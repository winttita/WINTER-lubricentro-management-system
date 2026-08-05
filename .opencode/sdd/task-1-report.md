# Task 1 Report — B04: Corregir precio_venta index en Ventas

## Status: DONE

## Summary

En `pages/7_Ventas.py:100`, el auto-fill del precio al elegir un producto usaba `p[10]`
(precio_costo) en lugar de `p[11]` (precio_venta). Como resultado, al vender se autocompletaba
el precio de costo, lo que originabaTickets de venta a precio de costo y pérdida de margen.

## Change

- **File:** `pages/7_Ventas.py`
- **Line:** 100
- **Old:** `item['precio'] = float(p[10])`
- **New:** `item['precio'] = float(p[11])`

### Verificación de índices

Schema de `productos` (`database.py:135-151`, orden 0-indexado):

| idx | columna          |
|-----|------------------|
| 0   | id               |
| 1   | codigo_interno   |
| 2   | codigo_barras     |
| 3   | nombre           |
| 4   | descripcion      |
| 5   | categoria_id     |
| 6   | proveedor_id     |
| 7   | tipo_unidad      |
| 8   | stock_actual     |
| 9   | stock_minimo     |
| 10  | precio_costo     |
| 11  | precio_venta     |
| 12  | activo           |
| 13  | categoria_nombre (JOIN) |
| 14  | proveedor_nombre (JOIN) |

`get_productos()` (`database.py:861`) hace `SELECT p.*, c.nombre, prov.nombre`, por lo que
el orden coincide: `p[10]` = precio_costo, `p[11]` = precio_venta. El fix es correcto.

## git diff

```diff
diff --git a/pages/7_Ventas.py b/pages/7_Ventas.py
index fa553b5..fb34216 100644
--- a/pages/7_Ventas.py
+++ b/pages/7_Ventas.py
@@ -97,7 +97,7 @@ with st.form("venta_form"):
             if prod_label and item['precio'] == 0.0:
                 pid = prod_opts[prod_label]
                 p = prod_lookup[pid]
-                item['precio'] = float(p[10])
+                item['precio'] = float(p[11])
         with col_cant:
             item['cantidad'] = st.number_input(
                 "Cant.", min_value=0.0, step=1.0,
```

## Commit

- SHA: `0cfb9adc57e31c880001c9598a369dfc472289bf`
- Subject: `fix: corrige indice de precio_venta en ventas (p[10] a p[11])`

## Notas adicionales

Se revisaron otros usos de `p[10]` en la codebase para confirmar que no son el mismo bug:

- `pages/7_Ventas.py:32` y `pages/4_Ordenes.py:126` — muestran `${p[10]:.2f}` en el LABEL del
  dropdown del producto. El comentario de la línea 96 del archivo editado ("Auto-fill precio con
  precio de venta del producto") sugiere que el dropdown también debería mostrar precio de venta,
  pero eso está fuera del alcance de B04 (que es solo la línea 100). Queda como observación
  potencial para un ticket futuro si el producto lo requiere.
- `pages/3_Productos.py:136` — carga `p[10]` en "Precio Costo" input (correcto, es costo).

No se introdujeron cambios adicionales fuera del alcance del task.
