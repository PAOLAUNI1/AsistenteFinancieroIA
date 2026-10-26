-- Migración 004: fondo de inversión (flujo "Registrar fondo de inversión" de la app).
-- Agrega la tabla de detalle `ahorro_fondo` (1:1 con `ahorros`): entidad, tasa de rendimiento esperada,
-- tipo de rentabilidad, reinversión, plazo sugerido y fecha de inversión. El tipo de fondo es el subtipo del ahorro.
-- Es idempotente: se puede ejecutar más de una vez y no toca los datos.
--   mysql -u <usuario> -p <base> < db/migraciones/004_ahorro_fondo.sql
-- Requiere haber aplicado antes 001_ahorros.sql. Una base nueva ya lo trae en db/schema.sql.

CREATE TABLE IF NOT EXISTS `ahorro_fondo` (
  `ahorro_id` int unsigned NOT NULL,
  `entidad` varchar(100) NOT NULL,
  `tasa_rendimiento` decimal(7,4) NOT NULL COMMENT 'Rendimiento esperado, efectivo anual (%)',
  `tipo_rentabilidad` enum('FIJA','VARIABLE') NOT NULL,
  `reinversion` tinyint(1) NOT NULL DEFAULT '0',
  `plazo_sugerido` enum('CORTO','MEDIANO','LARGO') DEFAULT NULL,
  `fecha_inversion` date NOT NULL,
  PRIMARY KEY (`ahorro_id`),
  CONSTRAINT `fk_ahorro_fondo_ahorro` FOREIGN KEY (`ahorro_id`) REFERENCES `ahorros` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_ahorro_fondo_tasa` CHECK ((`tasa_rendimiento` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
