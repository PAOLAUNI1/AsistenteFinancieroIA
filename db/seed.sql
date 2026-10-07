-- Catálogos que la app necesita para funcionar: tipos de deuda y categorías de gasto.
-- Se ejecuta DESPUÉS de db/schema.sql:
--   mysql -u <usuario> -p <base> < db/seed.sql

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

LOCK TABLES `tipos_deuda` WRITE;
/*!40000 ALTER TABLE `tipos_deuda` DISABLE KEYS */;
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (1,'HIPOTECARIO','Crédito hipotecario','🏠');
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (2,'TARJETA','Tarjeta de crédito','💳');
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (3,'VEHICULO','Crédito de vehículo','🚗');
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (4,'EDUCATIVO','Crédito educativo','🎓');
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (5,'LIBRE_INVERSION','Préstamo de libre inversión','💰');
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (6,'PRESTAMO_PERSONAL','Préstamo personal','🤝');
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (7,'CONSUMO','Crédito de consumo','🛒');
INSERT INTO `tipos_deuda` (`id`, `codigo`, `nombre`, `icono`) VALUES (8,'OTRO','Otras deudas','📄');
/*!40000 ALTER TABLE `tipos_deuda` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `categorias_gasto` WRITE;
/*!40000 ALTER TABLE `categorias_gasto` DISABLE KEYS */;
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (1,'ALIMENTACION','Alimentación','HOGAR');
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (2,'TRANSPORTE','Transporte','PERSONAL');
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (3,'VESTIMENTA','Vestimenta','PERSONAL');
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (4,'ENTRETENIMIENTO','Entretenimiento','PERSONAL');
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (5,'ARRIENDO','Arriendo o hipoteca','HOGAR');
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (6,'SERVICIOS','Servicios públicos','HOGAR');
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (7,'COLEGIO','Pago de colegio','FAMILIA_EDUCACION');
INSERT INTO `categorias_gasto` (`id`, `codigo`, `nombre`, `grupo`) VALUES (8,'UNIVERSIDAD','Pago de universidad','FAMILIA_EDUCACION');
/*!40000 ALTER TABLE `categorias_gasto` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
