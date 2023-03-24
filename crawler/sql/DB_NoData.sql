-- MySQL dump 10.13  Distrib 8.0.32, for macos13.0 (arm64)
--
-- Host: localhost    Database: DSA_JP
-- ------------------------------------------------------
-- Server version	8.0.32

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

--
-- Current Database: `DSA_JP`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `DSA_JP` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `DSA_JP`;

--
-- Table structure for table `Bus`
--

DROP TABLE IF EXISTS `Bus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Bus` (
  `BusID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Type` int NOT NULL DEFAULT '1',
  `StartBusStopID` int unsigned NOT NULL,
  `EndBusStopID` int unsigned NOT NULL,
  PRIMARY KEY (`BusID`),
  UNIQUE KEY `Bus_UN` (`Name`),
  UNIQUE KEY `Bus_UN2` (`BusID`),
  KEY `Bus_FK` (`StartBusStopID`),
  KEY `Bus_FK_1` (`EndBusStopID`),
  CONSTRAINT `Bus_FK` FOREIGN KEY (`StartBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Bus_FK_1` FOREIGN KEY (`EndBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Bus`
--

LOCK TABLES `Bus` WRITE;
/*!40000 ALTER TABLE `Bus` DISABLE KEYS */;
/*!40000 ALTER TABLE `Bus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BusRoute`
--

DROP TABLE IF EXISTS `BusRoute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BusRoute` (
  `RouteID` int unsigned NOT NULL AUTO_INCREMENT,
  `BusID` int unsigned NOT NULL,
  `BusStopID` int unsigned NOT NULL,
  `StopOrder` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`RouteID`),
  UNIQUE KEY `BusRoute_UN` (`RouteID`),
  KEY `BusRoute_FK` (`BusID`),
  KEY `BusRoute_FK_1` (`BusStopID`),
  CONSTRAINT `BusRoute_FK` FOREIGN KEY (`BusID`) REFERENCES `Bus` (`BusID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `BusRoute_FK_1` FOREIGN KEY (`BusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BusRoute`
--

LOCK TABLES `BusRoute` WRITE;
/*!40000 ALTER TABLE `BusRoute` DISABLE KEYS */;
/*!40000 ALTER TABLE `BusRoute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BusStop`
--

DROP TABLE IF EXISTS `BusStop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BusStop` (
  `BusStopID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(500) NOT NULL,
  `Latitude` double NOT NULL,
  `Longitude` double NOT NULL,
  PRIMARY KEY (`BusStopID`),
  UNIQUE KEY `BusStop_UN` (`Name`),
  UNIQUE KEY `BusStop_UN2` (`BusStopID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BusStop`
--

LOCK TABLES `BusStop` WRITE;
/*!40000 ALTER TABLE `BusStop` DISABLE KEYS */;
/*!40000 ALTER TABLE `BusStop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Edge`
--

DROP TABLE IF EXISTS `Edge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Edge` (
  `EdgeID` int unsigned NOT NULL AUTO_INCREMENT,
  `FromBusStopID` int unsigned NOT NULL,
  `ToBusStopID` int unsigned NOT NULL,
  `RouteID` int unsigned NOT NULL,
  PRIMARY KEY (`EdgeID`),
  UNIQUE KEY `Edge_UN` (`EdgeID`),
  KEY `Edge_FK` (`FromBusStopID`),
  KEY `Edge_FK_1` (`ToBusStopID`),
  KEY `Edge_FK_2` (`RouteID`),
  CONSTRAINT `Edge_FK` FOREIGN KEY (`FromBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Edge_FK_1` FOREIGN KEY (`ToBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Edge_FK_2` FOREIGN KEY (`RouteID`) REFERENCES `BusRoute` (`RouteID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Edge`
--

LOCK TABLES `Edge` WRITE;
/*!40000 ALTER TABLE `Edge` DISABLE KEYS */;
/*!40000 ALTER TABLE `Edge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Schedule`
--

DROP TABLE IF EXISTS `Schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Schedule` (
  `ScheduleID` int unsigned NOT NULL AUTO_INCREMENT,
  `RouteID` int unsigned NOT NULL,
  `Time` time NOT NULL,
  PRIMARY KEY (`ScheduleID`),
  UNIQUE KEY `Schedule_UN` (`ScheduleID`),
  KEY `Schedule_FK` (`RouteID`),
  CONSTRAINT `Schedule_FK` FOREIGN KEY (`RouteID`) REFERENCES `BusRoute` (`RouteID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Schedule`
--

LOCK TABLES `Schedule` WRITE;
/*!40000 ALTER TABLE `Schedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `Schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Weight`
--

DROP TABLE IF EXISTS `Weight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Weight` (
  `WeightID` int unsigned NOT NULL AUTO_INCREMENT,
  `EdgeID` int unsigned NOT NULL,
  `Weight` double NOT NULL DEFAULT '0',
  `Type` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`WeightID`),
  UNIQUE KEY `Weight_UN` (`WeightID`),
  KEY `Weight_FK` (`EdgeID`),
  CONSTRAINT `Weight_FK` FOREIGN KEY (`EdgeID`) REFERENCES `Edge` (`EdgeID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Weight`
--

LOCK TABLES `Weight` WRITE;
/*!40000 ALTER TABLE `Weight` DISABLE KEYS */;
/*!40000 ALTER TABLE `Weight` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-14 22:22:18
