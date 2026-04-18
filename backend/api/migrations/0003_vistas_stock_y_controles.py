from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_detallemovimiento_cantidad_entregada_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP VIEW IF EXISTS vw_saldo_acumulado_cliente;
            DROP VIEW IF EXISTS vw_resumen_cliente_dia;

            CREATE OR REPLACE VIEW vw_resumen_cliente_dia AS
            SELECT
                (
                    to_char(jd.fecha, 'YYYYMMDD')
                    || lpad(c.id_cliente::text, 10, '0')
                )::bigint AS id,
                jd.fecha,
                c.id_cliente,
                c.rut,
                c.digito_verificador,
                c.nombre_cliente,
                SUM(dm.precio_cobrado * dm.cantidad_entregada) AS venta_dia,
                SUM(COALESCE(dm.cancelacion, 0)) AS pago_dia,
                SUM(dm.precio_cobrado * dm.cantidad_entregada)
                    - SUM(COALESCE(dm.cancelacion, 0)) AS saldo_dia
            FROM detalle_movimiento dm
            JOIN jornada_diaria jd
                ON jd.id_jornada = dm.id_jornada
            JOIN cliente c
                ON c.id_cliente = dm.id_cliente
            GROUP BY
                jd.fecha,
                c.id_cliente,
                c.rut,
                c.digito_verificador,
                c.nombre_cliente;

            CREATE OR REPLACE VIEW vw_saldo_acumulado_cliente AS
            SELECT
                id_cliente AS id,
                id_cliente,
                rut,
                digito_verificador,
                nombre_cliente,
                SUM(saldo_dia) AS saldo_acumulado
            FROM vw_resumen_cliente_dia
            GROUP BY
                id_cliente,
                rut,
                digito_verificador,
                nombre_cliente;

            CREATE OR REPLACE FUNCTION fn_stock_insumo_fecha(
                p_id_insumo BIGINT,
                p_fecha DATE
            )
            RETURNS NUMERIC(10,2)
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_stock NUMERIC(10,2);
            BEGIN
                SELECT
                    COALESCE(i.stock_sugerido_inicial, 0)
                    + COALESCE(
                        SUM(
                            CASE
                                WHEN mb.tipo_movimiento = 'ENTRADA'
                                    THEN mb.cantidad
                                WHEN mb.tipo_movimiento = 'SALIDA'
                                    THEN -mb.cantidad
                                WHEN mb.tipo_movimiento = 'AJUSTE'
                                    THEN mb.cantidad
                                ELSE 0
                            END
                        ),
                        0
                    )
                INTO v_stock
                FROM insumo i
                LEFT JOIN movimiento_bodega mb
                    ON mb.id_insumo = i.id_insumo
                    AND mb.fecha_movimiento <= p_fecha
                WHERE i.id_insumo = p_id_insumo
                GROUP BY i.stock_sugerido_inicial;

                RETURN COALESCE(v_stock, 0);
            END;
            $$;

            UPDATE detalle_movimiento
            SET cancelacion = precio_cobrado * cantidad_entregada
            WHERE cancelacion IS NOT NULL
              AND cancelacion > (precio_cobrado * cantidad_entregada);

            ALTER TABLE detalle_movimiento
            DROP CONSTRAINT IF EXISTS chk_dm_cancelacion_no_supera_venta;

            ALTER TABLE detalle_movimiento
            ADD CONSTRAINT chk_dm_cancelacion_no_supera_venta
            CHECK (
                cancelacion IS NULL
                OR cancelacion <= (precio_cobrado * cantidad_entregada)
            );
            """,
            reverse_sql="""
            DROP FUNCTION IF EXISTS fn_stock_insumo_fecha(BIGINT, DATE);
            DROP VIEW IF EXISTS vw_saldo_acumulado_cliente;
            DROP VIEW IF EXISTS vw_resumen_cliente_dia;

            ALTER TABLE detalle_movimiento
            DROP CONSTRAINT IF EXISTS chk_dm_cancelacion_no_supera_venta;
            """,
        ),
    ]