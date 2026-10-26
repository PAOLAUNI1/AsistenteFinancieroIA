-- Migración 006: cuenta de ahorro (flujo "Registrar cuenta de ahorro" de la app).
-- Agrega la tabla de detalle `ahorro_cuenta` (1:1 con `ahorros`): la entidad financiera donde está la cuenta.
-- El tipo de cuenta (ahorros, nómina, digital...) es el subtipo del ahorro.
-- Es idempotente: se puede ejecutar más de una vez y no toca los datos.
--   mysql -u <usuario> -p <base> < db/migraciones/006_ahorro_cuenta.sql
-- Requiere haber aplicado antes 001_ahorros.sql. Una base nueva ya lo trae en db/schema.sql.

CREATE TABLE IF NOT EXISTS `ahorro_cuenta` (
  `ahorro_id` int unsigned NOT NULL,
  `entidad` varchar(100) NOT NULL,
  PRIMARY KEY (`ahorro_id`),
  CONSTRAINT `fk_ahorro_cuenta_ahorro` FOREIGN KEY (`ahorro_id`) REFERENCES `ahorros` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
