from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_detalle_reparto_turno'),
    ]

    operations = [
        migrations.RunSQL(
            sql=r"""
CREATE OR REPLACE FUNCTION fn_calcular_rinde_turno(
    p_id_jornada BIGINT,
    p_id_turno INTEGER
)
RETURNS TABLE (
    id_jornada BIGINT,
    id_turno INTEGER,
    kilos_reparto_directos NUMERIC(14,4),
    unidades_reparto NUMERIC(14,4),
    kilos_equivalentes NUMERIC(14,4),
    mostrador_kg NUMERIC(14,4),
    pan_especial_kg NUMERIC(14,4),
    raciones_kg NUMERIC(14,4),
    ajuste_por_error_kg NUMERIC(14,4),
    kilos_totales NUMERIC(14,4),
    quintales_cocidos NUMERIC(14,4),
    rinde NUMERIC(14,4)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_id_jornada IS NULL THEN
        RAISE EXCEPTION 'El parámetro p_id_jornada no puede ser NULL';
    END IF;

    IF p_id_turno IS NULL THEN
        RAISE EXCEPTION 'El parámetro p_id_turno no puede ser NULL';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM jornada_diaria jd
        WHERE jd.id_jornada = p_id_jornada
    ) THEN
        RAISE EXCEPTION 'No existe la jornada con id_jornada = %', p_id_jornada;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM turno t
        WHERE t.id_turno = p_id_turno
    ) THEN
        RAISE EXCEPTION 'No existe el turno con id_turno = %', p_id_turno;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM cierre_turno ct
        WHERE ct.id_jornada = p_id_jornada
        AND ct.id_turno = p_id_turno
    ) THEN
        RAISE EXCEPTION 'No existe cierre_turno para id_jornada = % e id_turno = %',
            p_id_jornada, p_id_turno;
    END IF;

    RETURN QUERY
    WITH reparto AS (
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN drt.unidad_medida = 'KILO'
                    THEN drt.cantidad_entregada
                    ELSE 0
                END
            ), 0) AS kilos_directos,

            COALESCE(SUM(
                CASE
                    WHEN drt.unidad_medida = 'UNIDAD'
                    THEN drt.cantidad_entregada
                    ELSE 0
                END
            ), 0) AS unidades
        FROM detalle_reparto_turno drt
        WHERE drt.id_jornada = p_id_jornada
        AND drt.id_turno = p_id_turno
    ),
    cierre AS (
        SELECT
            COALESCE(ct.mostrador_kg, 0) AS mostrador_kg,
            COALESCE(ct.pan_especial_kg, 0) AS pan_especial_kg,
            COALESCE(ct.raciones_kg, 0) AS raciones_kg,
            COALESCE(ct.ajuste_por_error_kg, 0) AS ajuste_por_error_kg
        FROM cierre_turno ct
        WHERE ct.id_jornada = p_id_jornada
        AND ct.id_turno = p_id_turno
    ),
    produccion_turno AS (
        SELECT
            COALESCE(SUM(p.quintales), 0) AS quintales_cocidos
        FROM produccion p
        INNER JOIN tipo_produccion tp
            ON tp.id_tipo_produccion = p.id_tipo_produccion
        WHERE p.id_jornada = p_id_jornada
        AND p.id_turno = p_id_turno
        AND tp.nombre_tipo_produccion IN ('Pan corriente', 'Pan especial')
    ),
    calculo AS (
        SELECT
            p_id_jornada AS jornada_calculada,
            p_id_turno AS turno_calculado,

            r.kilos_directos,
            r.unidades,
            r.unidades / 13 AS kilos_equivalentes,

            c.mostrador_kg,
            c.pan_especial_kg,
            c.raciones_kg,
            c.ajuste_por_error_kg,
            pt.quintales_cocidos
        FROM reparto r
        CROSS JOIN cierre c
        CROSS JOIN produccion_turno pt
    )
    SELECT
        calc.jornada_calculada::BIGINT,
        calc.turno_calculado::INTEGER,

        calc.kilos_directos::NUMERIC(14,4),
        calc.unidades::NUMERIC(14,4),
        calc.kilos_equivalentes::NUMERIC(14,4),

        calc.mostrador_kg::NUMERIC(14,4),
        calc.pan_especial_kg::NUMERIC(14,4),
        calc.raciones_kg::NUMERIC(14,4),
        calc.ajuste_por_error_kg::NUMERIC(14,4),

        (
            calc.kilos_directos
            + calc.kilos_equivalentes
            + calc.mostrador_kg
            + calc.pan_especial_kg
            + calc.raciones_kg
            + calc.ajuste_por_error_kg
        )::NUMERIC(14,4) AS kilos_totales,

        calc.quintales_cocidos::NUMERIC(14,4),

        (
            (
                calc.kilos_directos
                + calc.kilos_equivalentes
                + calc.mostrador_kg
                + calc.pan_especial_kg
                + calc.raciones_kg
                + calc.ajuste_por_error_kg
            )
            / NULLIF(calc.quintales_cocidos, 0)
        )::NUMERIC(14,4) AS rinde
    FROM calculo calc;
END;
$$;

CREATE OR REPLACE FUNCTION fn_bloquear_reparto_turno_cierre_cerrado()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cerrado BOOLEAN;
BEGIN
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        SELECT EXISTS (
            SELECT 1
            FROM cierre_turno ct
            WHERE ct.id_jornada = OLD.id_jornada
            AND ct.id_turno = OLD.id_turno
            AND ct.estado = 'CERRADO'
        )
        INTO v_cerrado;

        IF v_cerrado THEN
            RAISE EXCEPTION 'No se pueden modificar repartos de un turno cerrado';
        END IF;
    END IF;

    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        SELECT EXISTS (
            SELECT 1
            FROM cierre_turno ct
            WHERE ct.id_jornada = NEW.id_jornada
            AND ct.id_turno = NEW.id_turno
            AND ct.estado = 'CERRADO'
        )
        INTO v_cerrado;

        IF v_cerrado THEN
            RAISE EXCEPTION 'No se pueden modificar repartos de un turno cerrado';
        END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_bloquear_reparto_turno_cierre_cerrado
ON detalle_reparto_turno;

CREATE TRIGGER trg_bloquear_reparto_turno_cierre_cerrado
BEFORE INSERT OR UPDATE OR DELETE
ON detalle_reparto_turno
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_reparto_turno_cierre_cerrado();
""",
            reverse_sql=r"""
DROP TRIGGER IF EXISTS trg_bloquear_reparto_turno_cierre_cerrado
ON detalle_reparto_turno;

DROP FUNCTION IF EXISTS fn_bloquear_reparto_turno_cierre_cerrado();

CREATE OR REPLACE FUNCTION fn_calcular_rinde_turno(
    p_id_jornada BIGINT,
    p_id_turno INTEGER
)
RETURNS TABLE (
    id_jornada BIGINT,
    id_turno INTEGER,
    kilos_reparto_directos NUMERIC(14,4),
    unidades_reparto NUMERIC(14,4),
    kilos_equivalentes NUMERIC(14,4),
    mostrador_kg NUMERIC(14,4),
    pan_especial_kg NUMERIC(14,4),
    raciones_kg NUMERIC(14,4),
    ajuste_por_error_kg NUMERIC(14,4),
    kilos_totales NUMERIC(14,4),
    quintales_cocidos NUMERIC(14,4),
    rinde NUMERIC(14,4)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH movimientos AS (
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN dm.unidad_medida = 'KILO'
                    THEN dm.cantidad_entregada
                    ELSE 0
                END
            ), 0) AS kilos_directos,

            COALESCE(SUM(
                CASE
                    WHEN dm.unidad_medida = 'UNIDAD'
                    THEN dm.cantidad_entregada
                    ELSE 0
                END
            ), 0) AS unidades
        FROM detalle_movimiento dm
        INNER JOIN producto pr
            ON pr.id_producto = dm.id_producto
        INNER JOIN tipo_produccion tp
            ON tp.id_tipo_produccion = pr.id_tipo_produccion
        WHERE dm.id_jornada = p_id_jornada
        AND dm.id_turno = p_id_turno
        AND tp.nombre_tipo_produccion = 'Pan corriente'
    ),
    cierre AS (
        SELECT
            COALESCE(ct.mostrador_kg, 0) AS mostrador_kg,
            COALESCE(ct.pan_especial_kg, 0) AS pan_especial_kg,
            COALESCE(ct.raciones_kg, 0) AS raciones_kg,
            COALESCE(ct.ajuste_por_error_kg, 0) AS ajuste_por_error_kg
        FROM cierre_turno ct
        WHERE ct.id_jornada = p_id_jornada
        AND ct.id_turno = p_id_turno
    ),
    produccion_turno AS (
        SELECT
            COALESCE(SUM(p.quintales), 0) AS quintales_cocidos
        FROM produccion p
        INNER JOIN tipo_produccion tp
            ON tp.id_tipo_produccion = p.id_tipo_produccion
        WHERE p.id_jornada = p_id_jornada
        AND p.id_turno = p_id_turno
        AND tp.nombre_tipo_produccion IN ('Pan corriente', 'Pan especial')
    ),
    calculo AS (
        SELECT
            p_id_jornada AS jornada_calculada,
            p_id_turno AS turno_calculado,

            m.kilos_directos,
            m.unidades,
            m.unidades / 13 AS kilos_equivalentes,

            c.mostrador_kg,
            c.pan_especial_kg,
            c.raciones_kg,
            c.ajuste_por_error_kg,
            pt.quintales_cocidos
        FROM movimientos m
        CROSS JOIN cierre c
        CROSS JOIN produccion_turno pt
    )
    SELECT
        calc.jornada_calculada::BIGINT,
        calc.turno_calculado::INTEGER,

        calc.kilos_directos::NUMERIC(14,4),
        calc.unidades::NUMERIC(14,4),
        calc.kilos_equivalentes::NUMERIC(14,4),

        calc.mostrador_kg::NUMERIC(14,4),
        calc.pan_especial_kg::NUMERIC(14,4),
        calc.raciones_kg::NUMERIC(14,4),
        calc.ajuste_por_error_kg::NUMERIC(14,4),

        (
            calc.kilos_directos
            + calc.kilos_equivalentes
            + calc.mostrador_kg
            + calc.pan_especial_kg
            + calc.raciones_kg
            + calc.ajuste_por_error_kg
        )::NUMERIC(14,4) AS kilos_totales,

        calc.quintales_cocidos::NUMERIC(14,4),

        (
            (
                calc.kilos_directos
                + calc.kilos_equivalentes
                + calc.mostrador_kg
                + calc.pan_especial_kg
                + calc.raciones_kg
                + calc.ajuste_por_error_kg
            )
            / NULLIF(calc.quintales_cocidos, 0)
        )::NUMERIC(14,4) AS rinde
    FROM calculo calc;
END;
$$;
""",
        ),
    ]