-- Migración 005: CDT (flujo "Registrar CDT" de la app).
-- Agrega la tabla de detalle `ahorro_cdt` (1:1 con `ahorros`): entidad, tasa de interés anual, plazo en meses,
-- fechas de apertura y vencimiento y renovación automática con sus instrucciones. El tipo de tasa (fija o
-- variable) es el subtipo del ahorro.
-- Es idempotente: se puede ejecutar más de una vez y no toca los datos.
--   mysql -u <usuario> -p <base> < db/migraciones/005_ahorro_cdt.sql
-- Requiere haber aplicado antes 001_ahorros.sql. Una base nueva ya lo trae en db/schema.sql.

CREATE TABLE IF NOT EXISTS `ahorro_cdt` (
  `ahorro_id` int unsigned NOT NULL,
  `entidad` varchar(100) NOT NULL,
  `tasa_interes` decimal(7,4) NOT NULL COMMENT 'Tasa de interés anual (%)',
  `plazo_meses` smallint NOT NULL,
  `fecha_apertura` date NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `renovacion_automatica` tinyint(1) NOT NULL DEFAULT '0',
  `instruccion_renovacion` enum('MISMO_MONTO','CAPITAL_E_INTERESES','SOLO_CAPITAL') DEFAULT NULL,
  PRIMARY KEY (`ahorro_id`),
  CONSTRAINT `fk_ahorro_cdt_ahorro` FOREIGN KEY (`ahorro_id`) REFERENCES `ahorros` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_ahorro_cdt_tasa` CHECK ((`tasa_interes` > 0)),
  CONSTRAINT `chk_ahorro_cdt_plazo` CHECK ((`plazo_meses` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
